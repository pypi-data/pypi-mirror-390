"""
Constrained Multinomial Logistic Regression (CMLR) implementations

This module implements CMLR1 (reference-based) and CMLR2 (sum-to-zero constrained)
using only numpy, as described in "Simplex-based Multinomial Logistic Regression with
Diverging Numbers of Categories and Covariates" by Fu et al. (2024).

CMLR1: Reference-based MLR where theta_r = 0 for reference category r
CMLR2: Symmetric constrained MLR with sum(ti-zero constraint: j=1^k j = 0
"""

import numpy as np


class CMLR1:
    """
    Constrained Multinomial Logistic Regression (CMLR1) - Reference-based approach

    In CMLR1, we choose a reference category r and set r = 0.
    This resolves the identifiability issue in standard MLR.
    """

    def __init__(self, max_iter=1000, tol=1e-6, penalty=None, gamma=1.0):
        self.max_iter = max_iter
        self.tol = tol
        self.penalty = penalty
        self.gamma = gamma
        self.coef_ = None
        self.n_classes_ = None
        self.n_features_ = None
        self.reference_class_ = None

    def _softmax(self, X):
        """Compute softmax probabilities"""
        exp_X = np.exp(X - np.max(X, axis=1, keepdims=True))
        return exp_X / np.sum(exp_X, axis=1, keepdims=True)

    def _logistic_loss_gradient(self, X, y, coef_flat):
        """
        Compute loss and gradient for reference-based MLR with optional penalty
        """
        n_samples = X.shape[0]
        n_features = X.shape[1]
        n_classes = self.n_classes_

        # Reshape coefficients excluding reference class
        coef_non_ref = coef_flat.reshape(n_features, n_classes - 1)

        # Create full coefficient matrix with reference class = 0
        coef_full = np.zeros((n_features, n_classes))
        mask = np.ones(n_classes, dtype=bool)
        mask[self.reference_class_] = False
        coef_full[:, mask] = coef_non_ref

        # Compute linear predictors
        X_beta = X.dot(coef_full)  # Shape: (n_samples, n_classes)
        prob = self._softmax(X_beta)

        # Compute log-likelihood
        log_likelihood = np.sum(X_beta[np.arange(n_samples), y] -
                                np.log(np.sum(np.exp(X_beta), axis=1)))
        loss = -log_likelihood / n_samples

        # Add penalty terms
        if self.penalty == 'l1':
            penalty_loss = self.gamma * np.sum(np.abs(coef_flat))
            loss += penalty_loss
        elif self.penalty == 'l2':
            penalty_loss = 0.5 * self.gamma * np.sum(coef_flat ** 2)
            loss += penalty_loss

        # Compute gradient for non-reference classes only
        grad = np.zeros((n_features, n_classes - 1))

        # For each non-reference class, compute gradient
        grad_mask_idx = 0
        for j in range(n_classes):
            if j == self.reference_class_:
                continue

            # Create indicator: 1 if y_i = j, -1 if y_i = reference, else 0
            indicator = np.zeros(n_samples)
            indicator[y == j] = 1
            indicator[y == self.reference_class_] = -1

            # Compute difference in probabilities: p(y=j|x) - p(y=reference|x)
            prob_diff = prob[:, j] - prob[:, self.reference_class_]

            # Compute residual: indicator - prob_diff
            residual = indicator - prob_diff

            # Compute gradient for this class
            grad[:, grad_mask_idx] = X.T.dot(residual) / n_samples

            grad_mask_idx += 1

        # Add penalty gradient
        if self.penalty == 'l1':
            grad_penalty = self.gamma * np.sign(coef_flat)
            grad_flat = grad.ravel() - grad_penalty
        elif self.penalty == 'l2':
            grad_penalty = self.gamma * coef_flat
            grad_flat = grad.ravel() - grad_penalty
        else:
            grad_flat = grad.ravel()

        return loss, -grad_flat  # Return negative gradient for minimization

    def fit(self, X, y, reference_class=0):
        """
        Fit CMLR1 model

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training data
        y : array-like, shape (n_samples,)
            Target labels, encoded as integers 0, 1, ..., n_classes-1
        reference_class : int, default=0
            Index of the reference category

        Returns
        -------
        self : object
        """
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)

        self.n_features_ = X.shape[1]
        self.n_classes_ = len(np.unique(y))
        self.reference_class_ = reference_class

        # Initialize coefficients for non-reference classes only
        n_params = self.n_features_ * (self.n_classes_ - 1)
        coef = np.zeros(n_params)

        # Simple gradient descent optimization (can be improved with better algorithms)
        learning_rate = 0.1
        for iter in range(self.max_iter):
            loss, grad = self._logistic_loss_gradient(X, y, coef)

            # Update coefficients
            coef_new = coef - learning_rate * grad

            # Check convergence
            if np.linalg.norm(grad) < self.tol:
                break

            coef = coef_new

            if iter % 100 == 0:
                learning_rate *= 0.95  # Simple learning rate decay

        # Store coefficients in matrix form (excluding reference class)
        self.coef_ = coef.reshape(self.n_features_, self.n_classes_ - 1)

        return self

    def predict_proba(self, X):
        """
        Predict class probabilities

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Data to predict

        Returns
        -------
        prob : array, shape (n_samples, n_classes)
            Predicted probabilities
        """
        X = np.asarray(X, dtype=float)

        # Create full coefficient matrix including reference class
        coef_full = np.zeros((self.n_features_, self.n_classes_))
        mask = np.ones(self.n_classes_, dtype=bool)
        mask[self.reference_class_] = False
        coef_full[:, mask] = self.coef_

        # Compute probabilities
        X_beta = X.dot(coef_full)
        return self._softmax(X_beta)

    def predict(self, X):
        """Predict class labels"""
        return np.argmax(self.predict_proba(X), axis=1)


class CMLR2:
    """
    Constrained Multinomial Logistic Regression (CMLR2) - Sum-to-zero constrained

    In CMLR2, we impose the constraint _j _j = 0 for all j.
    This provides a symmetric treatment of all categories.
    """

    def __init__(self, max_iter=1000, tol=1e-6, penalty=None, gamma=1.0):
        self.max_iter = max_iter
        self.tol = tol
        self.penalty = penalty
        self.gamma = gamma
        self.coef_ = None
        self.n_classes_ = None
        self.n_features_ = None

    def _project_to_constraint(self, theta):
        """Project theta to satisfy sum-to-zero constraint"""
        # Reshape to matrix form: (n_features, n_classes)
        theta_mat = theta.reshape(self.n_features_, self.n_classes_)
        # For each feature, subtract mean across classes
        theta_mean = np.mean(theta_mat, axis=1, keepdims=True)
        theta_proj = theta_mat - theta_mean
        return theta_proj.ravel()

    def _softmax(self, X):
        """Compute softmax probabilities"""
        exp_X = np.exp(X - np.max(X, axis=1, keepdims=True))
        return exp_X / np.sum(exp_X, axis=1, keepdims=True)

    def _logistic_loss_gradient(self, X, y, theta_flat):
        """
        Compute loss and gradient for sum-to-zero constrained MLR
        """
        n_samples = X.shape[0]
        n_features = X.shape[1]

        # Project theta to constraint
        theta_proj = self._project_to_constraint(theta_flat)
        theta_mat = theta_proj.reshape(n_features, self.n_classes_)

        # Compute linear predictors
        X_beta = X.dot(theta_mat)  # Shape: (n_samples, n_classes)
        prob = self._softmax(X_beta)

        # Compute log-likelihood
        log_likelihood = np.sum(X_beta[np.arange(n_samples), y] -
                                np.log(np.sum(np.exp(X_beta), axis=1)))
        loss = -log_likelihood / n_samples

        # Add penalty terms
        if self.penalty == 'l1':
            penalty_loss = self.gamma * np.sum(np.abs(theta_flat))
            loss += penalty_loss
        elif self.penalty == 'l2':
            penalty_loss = 0.5 * self.gamma * np.sum(theta_flat ** 2)
            loss += penalty_loss

        # Compute gradient
        grad = np.zeros((n_features, self.n_classes_))

        # Standard MLR gradient
        for j in range(self.n_classes_):
            # Indicator: 1 if y_i = j, else 0
            indicator = (y == j).astype(float)

            # Compute gradient for this class
            grad[:, j] = X.T.dot(indicator - prob[:, j]) / n_samples

        # Add penalty gradient
        if self.penalty == 'l1':
            grad_penalty = self.gamma * np.sign(theta_flat)
            grad_flat = grad.ravel() - grad_penalty
        elif self.penalty == 'l2':
            grad_penalty = self.gamma * theta_flat
            grad_flat = grad.ravel() - grad_penalty
        else:
            grad_flat = grad.ravel()

        # Project gradient to constraint subspace
        grad_proj = self._project_to_constraint(grad_flat)

        return loss, -grad_proj  # Return negative gradient for minimization

    def fit(self, X, y):
        """
        Fit CMLR2 model

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training data
        y : array-like, shape (n_samples,)
            Target labels, encoded as integers 0, 1, ..., n_classes-1

        Returns
        -------
        self : object
        """
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)

        self.n_features_ = X.shape[1]
        self.n_classes_ = len(np.unique(y))

        # Initialize coefficients
        n_params = self.n_features_ * self.n_classes_
        theta = np.zeros(n_params)

        # Gradient descent optimization with projection to constraint
        learning_rate = 0.1
        for iter in range(self.max_iter):
            loss, grad = self._logistic_loss_gradient(X, y, theta)

            # Update with projected gradient
            theta_new = theta - learning_rate * grad

            # Check convergence
            if np.linalg.norm(grad) < self.tol:
                break

            theta = theta_new

            if iter % 100 == 0:
                learning_rate *= 0.95  # Simple learning rate decay

        # Final projection to ensure constraint satisfaction
        theta_final = self._project_to_constraint(theta)
        self.coef_ = theta_final.reshape(self.n_features_, self.n_classes_)

        return self

    def predict_proba(self, X):
        """
        Predict class probabilities

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Data to predict

        Returns
        -------
        prob : array, shape (n_samples, n_classes)
            Predicted probabilities
        """
        X = np.asarray(X, dtype=float)

        # Verify constraint is satisfied
        if hasattr(self, 'coef_'):
            constraint_sum = np.sum(self.coef_, axis=1)
            if np.any(np.abs(constraint_sum) > 1e-10):
                print("Warning: Constraint not exactly satisfied, projecting...")
                self.coef_ = self._project_to_constraint(self.coef_.ravel()).reshape(
                    self.n_features_, self.n_classes_)

        # Compute probabilities
        X_beta = X.dot(self.coef_)
        return self._softmax(X_beta)

    def predict(self, X):
        """Predict class labels"""
        return np.argmax(self.predict_proba(X), axis=1)


def example_usage():
    """Example usage of both CMLR implementations"""
    np.random.seed(42)

    # Generate synthetic data
    n_samples = 200
    n_features = 4
    n_classes = 3

    # Generate features
    X = np.random.randn(n_samples, n_features)

    # Generate true parameters (using CMLR2 constraint)
    true_coef = np.random.randn(n_features, n_classes)
    # Project to sum-to-zero constraint
    true_coef = true_coef - np.mean(true_coef, axis=1, keepdims=True)

    # Generate true probabilities and labels
    logits = X.dot(true_coef)
    prob = np.exp(logits) / np.sum(np.exp(logits), axis=1, keepdims=True)
    y = np.array([np.random.choice(n_classes, p=pi) for pi in prob])

    print("=== Generated Data ===")
    print(f"Samples: {n_samples}, Features: {n_features}, Classes: {n_classes}")
    print(f"True base probabilities per class (empirical): {np.bincount(y) / n_samples}")

    # Test CMLR1 (reference-based)
    print("\n=== CMLR1 (Reference-based) ===")
    cmlr1 = CMLR1(max_iter=200, tol=1e-6)
    cmlr1.fit(X, y, reference_class=0)
    y_pred = cmlr1.predict(X)
    acc1 = np.mean(y_pred == y)
    print(f"Training Accuracy: {acc1:.4f}")
    print(f"Coefficients shape: {cmlr1.coef_.shape}")
    print(f"Reference class: {cmlr1.reference_class_}")

    # Test CMLR2 (sum-to-zero constrained)
    print("\n=== CMLR2 (Sum-to-zero constrained) ===")
    cmlr2 = CMLR2(max_iter=200, tol=1e-6)
    cmlr2.fit(X, y)
    y_pred = cmlr2.predict(X)
    acc2 = np.mean(y_pred == y)
    print(f"Training Accuracy: {acc2:.4f}")
    print(f"Coefficients shape: {cmlr2.coef_.shape}")
    print(f"Sum of coefficients per feature (constraint check): {np.sum(cmlr2.coef_, axis=1)}")

    print("\n=== Implementation Notes ===")
    print("CMLR1 sets reference class coefficients to 0 and estimates others")
    print("CMLR2 ensures all feature-wise coefficient sums equal 0")
    print("Both achieve the same likelihood theoretically (per the paper), but use different parameterizations")


if __name__ == "__main__":
    example_usage()