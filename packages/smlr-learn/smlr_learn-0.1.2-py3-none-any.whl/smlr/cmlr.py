"""
Constrained Multinomial Logistic Regression (CMLR) implementations

This module implements CMLR1 (reference-based) and CMLR2 (sum-to-zero constrained)
using only numpy, as described in "Simplex-based Multinomial Logistic Regression with
Diverging Numbers of Categories and Covariates" by Fu et al. (2024).

CMLR1: Reference-based MLR where theta_r = 0 for reference category r
CMLR2: Symmetric constrained MLR with sum(ti-zero constraint: j=1^k j = 0
"""

import numpy as np
import warnings


class CMLR1:
    """
    Constrained Multinomial Logistic Regression (CMLR1) - Reference-based

    Implements multinomial logistic regression by fixing one reference class
    coefficient vector to zero to remove identifiability, optimized using
    proximal gradient descent.
    """

    def __init__(self, penalty: None | str = None, gamma: float | int = 0, fit_intercept: bool = True):
        """
        Parameters
        ----------
        penalty : {'l1', 'l2', None}
            Type of regularization. 'l1' uses soft-thresholding.
        gamma : float
            Regularization strength.
        fit_intercept : bool
            Whether to include intercept term.
        """
        err_msg = f"penalty must be 'l1', 'l2' or None but got: {penalty}"
        assert penalty in [None, 'l1', 'l2'], err_msg
        assert isinstance(gamma, (int, float)), f"gamma must be numeric but got {type(gamma)}"
        assert isinstance(fit_intercept, bool), "fit_intercept must be a bool."

        self.beta = None
        self.gamma = 0 if penalty is None else gamma
        self.penalty = penalty
        self.fit_intercept = fit_intercept
        self._is_fit = False

    def fit(self, X: np.ndarray, y: np.ndarray, reference_class: int = 0,
            lr: float = 0.05, tol: float = 1e-7,
            max_iter: int = 10000, verbose: bool = True):
        """
        Fit the CMLR1 model using proximal gradient descent.

        Parameters
        ----------
        X : ndarray of shape (N, M)
            Input data.
        y : ndarray of shape (N,)
            Class labels.
        reference_class : int
            Index of the reference category whose coefficients are fixed to zero.
        lr : float
            Learning rate (step size).
        tol : float
            Convergence tolerance.
        max_iter : int
            Maximum number of iterations.
        verbose : bool
            Print progress if True.
        """
        if self.fit_intercept:
            X = np.c_[np.ones(X.shape[0]), X]

        assert X.ndim == 2, "X should be a 2D array."
        if y.ndim >= 2:
            warnings.warn("Passed y is multidimensional; flattening.")
            y = y.flatten()

        N, M = X.shape
        classes = np.unique(y)
        self.k = len(classes)
        self.reference_class_ = reference_class

        assert 0 <= reference_class < self.k, f"reference_class must be in [0, {self.k-1}]"

        # Initialize β (M × (k-1)), only for non-reference classes
        self.beta = np.random.randn(M, self.k - 1) * 0.01

        # Build mapping mask
        mask = np.ones(self.k, dtype=bool)
        mask[reference_class] = False

        Y = np.eye(self.k)[y]
        prev_loss = np.inf

        for i in range(max_iter):
            # Forward: full coefficient matrix
            coef_full = np.zeros((M, self.k))
            coef_full[:, mask] = self.beta

            # Compute probabilities
            scores = X @ coef_full
            probs = self._softmax(scores)

            # Gradient for non-reference classes
            grad_full = X.T @ (probs - Y) / N
            grad = grad_full[:, mask]

            # Gradient step
            Z = self.beta - lr * grad

            # Proximal operator
            self.beta = self._prox(Z, lr)

            # Convergence check
            delta = np.linalg.norm(lr * grad)
            if delta < tol:
                if verbose:
                    print(f"Converged after {i+1} iterations, |Δβ|={delta:.3e}")
                break

            # Optional logging
            if verbose and (i + 1) % 1000 == 0:
                loss = self._NLL(Y, probs)
                print(f"Iteration {i+1}, loss={loss:.6f}, |Δβ|={delta:.3e}")

        self._is_fit = True
        return self


    @staticmethod
    def _softmax(scores: np.ndarray) -> np.ndarray:
        scores -= np.max(scores, axis=1, keepdims=True)
        exp_s = np.exp(scores)
        return exp_s / np.sum(exp_s, axis=1, keepdims=True)

    def _prox(self, Z: np.ndarray, lr: float) -> np.ndarray:
        """Proximal operator for regularization."""
        if self.penalty == 'l1':
            return np.sign(Z) * np.maximum(np.abs(Z) - lr * self.gamma, 0.0)
        elif self.penalty == 'l2':
            return Z / (1 + lr * self.gamma)
        return Z

    def _NLL(self, Y: np.ndarray, probs: np.ndarray) -> float:
        """Compute penalized negative log-likelihood."""
        N = Y.shape[0]
        nll = -np.sum(Y * np.log(probs + 1e-15)) / N
        if self.penalty == 'l1':
            reg = self.gamma * np.sum(np.abs(self.beta))
        elif self.penalty == 'l2':
            reg = 0.5 * self.gamma * np.sum(self.beta ** 2)
        else:
            reg = 0
        return nll + reg / N

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        assert self._is_fit, "Call .fit() before predict()."
        if self.fit_intercept:
            X = np.c_[np.ones(X.shape[0]), X]
        probs = self._predict_proba_internal(X)
        return np.argmax(probs, axis=1)

    def predict_prob(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        assert self._is_fit, "Call .fit() before predict()."
        if self.fit_intercept:
            X = np.c_[np.ones(X.shape[0]), X]
        return self._predict_proba_internal(X)

    def _predict_proba_internal(self, X: np.ndarray) -> np.ndarray:
        coef_full = np.zeros((X.shape[1], self.k))
        mask = np.ones(self.k, dtype=bool)
        mask[self.reference_class_] = False
        coef_full[:, mask] = self.beta
        scores = X @ coef_full
        return self._softmax(scores)

    def _get_params(self) -> dict:
        return {
            "beta": self.beta,
            "gamma": self.gamma,
            "penalty": self.penalty,
            "fit_intercept": self.fit_intercept,
            "reference_class": self.reference_class_,
            "_is_fit": self._is_fit,
        }


class CMLR2:
    """
    Constrained Multinomial Logistic Regression (CMLR2)
    ---------------------------------------------------
    Implements the constraint formulation:
        sum_{j=1}^k β_j = 0
    This ensures identifiability without selecting a reference class.

    Optimization is performed via proximal gradient descent with
    projection onto the affine constraint subspace.
    """

    def __init__(self, penalty: None | str = None, gamma: float | int = 0, fit_intercept: bool = True):
        """
        Parameters
        ----------
        penalty : {'l1', 'l2', None}
            Regularization type. 'l1' uses soft-thresholding.
        gamma : float
            Regularization strength.
        fit_intercept : bool
            Whether to include intercept term.
        """
        err_msg = f"penalty must be 'l1', 'l2' or None but got: {penalty}"
        assert penalty in [None, 'l1', 'l2'], err_msg
        assert isinstance(gamma, (int, float)), f"gamma must be numeric but got {type(gamma)}"
        assert isinstance(fit_intercept, bool), "fit_intercept must be a bool."

        self.beta = None
        self.gamma = 0 if penalty is None else gamma
        self.penalty = penalty
        self.fit_intercept = fit_intercept
        self._is_fit = False

    def fit(self, X: np.ndarray, y: np.ndarray,
            lr: float = 0.05, tol: float = 1e-7,
            max_iter: int = 10000, verbose: bool = True):
        """
        Fit the CMLR2 model.

        Parameters
        ----------
        X : ndarray of shape (N, M)
            Input data.
        y : ndarray of shape (N,)
            Class labels.
        lr : float
            Learning rate (step size).
        tol : float
            Convergence tolerance.
        max_iter : int
            Maximum number of iterations.
        verbose : bool
            Print progress if True.
        """
        if self.fit_intercept:
            X = np.c_[np.ones(X.shape[0]), X]

        assert X.ndim == 2, "X should be a 2D array."
        if y.ndim >= 2:
            warnings.warn("Passed y is multidimensional; flattening.")
            y = y.flatten()

        N, M = X.shape
        classes = np.unique(y)
        self.k = len(classes)

        # Initialize β (M × k), subject to sum β_j = 0
        self.beta = np.random.randn(M, self.k) * 0.01
        self._project_to_constraint()

        Y = np.eye(self.k)[y]
        prev_loss = np.inf

        for i in range(max_iter):
            # Forward
            scores = X @ self.beta
            probs = self._softmax(scores)

            # Gradient of smooth part
            grad = X.T @ (probs - Y) / N

            # Gradient step
            Z = self.beta - lr * grad

            # Proximal operator for penalty
            self.beta = self._prox(Z, lr)

            # Projection onto constraint: sum_j β_j = 0
            self._project_to_constraint()

            # Convergence check
            delta = np.linalg.norm(lr * grad)
            if delta < tol:
                if verbose:
                    print(f"Converged after {i+1} iterations, |Δβ|={delta:.3e}")
                break

            if verbose and (i + 1) % 1000 == 0:
                loss = self._NLL(Y, probs)
                print(f"Iteration {i+1}, loss={loss:.6f}, |Δβ|={delta:.3e}")

        self._is_fit = True
        return self


    @staticmethod
    def _softmax(scores: np.ndarray) -> np.ndarray:
        scores -= np.max(scores, axis=1, keepdims=True)
        exp_s = np.exp(scores)
        return exp_s / np.sum(exp_s, axis=1, keepdims=True)

    def _prox(self, Z: np.ndarray, lr: float) -> np.ndarray:
        """Proximal operator for L1/L2 penalties."""
        if self.penalty == 'l1':
            return np.sign(Z) * np.maximum(np.abs(Z) - lr * self.gamma, 0.0)
        elif self.penalty == 'l2':
            return Z / (1 + lr * self.gamma)
        return Z

    def _project_to_constraint(self):
        """Project β onto constraint subspace: sum_j β_j = 0."""
        mean_beta = np.mean(self.beta, axis=1, keepdims=True)
        self.beta -= mean_beta  # subtract mean across classes

    def _NLL(self, Y: np.ndarray, probs: np.ndarray) -> float:
        """Compute penalized negative log-likelihood."""
        N = Y.shape[0]
        nll = -np.sum(Y * np.log(probs + 1e-15)) / N
        if self.penalty == 'l1':
            reg = self.gamma * np.sum(np.abs(self.beta))
        elif self.penalty == 'l2':
            reg = 0.5 * self.gamma * np.sum(self.beta ** 2)
        else:
            reg = 0
        return nll + reg / N

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        assert self._is_fit, "Call .fit() before predict()."
        if self.fit_intercept:
            X = np.c_[np.ones(X.shape[0]), X]
        probs = self._predict_proba_internal(X)
        return np.argmax(probs, axis=1)

    def predict_prob(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        assert self._is_fit, "Call .fit() before predict()."
        if self.fit_intercept:
            X = np.c_[np.ones(X.shape[0]), X]
        return self._predict_proba_internal(X)

    def _predict_proba_internal(self, X: np.ndarray) -> np.ndarray:
        scores = X @ self.beta
        return self._softmax(scores)

    def _get_params(self) -> dict:
        return {
            "beta": self.beta,
            "gamma": self.gamma,
            "penalty": self.penalty,
            "fit_intercept": self.fit_intercept,
            "_is_fit": self._is_fit,
        }