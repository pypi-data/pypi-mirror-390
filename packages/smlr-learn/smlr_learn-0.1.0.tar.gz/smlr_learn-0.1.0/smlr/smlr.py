import numpy as np
from .utils.functions import simplex_matrix

class SMLR:
    def __init__(self, penalty: None | str = None, gamma: float | int = 0, fit_intercept: bool =True):
        """
        Simplex-Based Multinomial Logistic Regression

        Parameters
        -----
        :param penalty: str, l1 penalty or no penalty
        :param gamma: float, regularization parameter
        :param fit_intercept: bool, whether to fit for intercept
        """

        err_msg = f"penalty must be 'l1', 'l2' or None but got: {penalty}"
        assert penalty in [None, 'l1', 'l2'], err_msg

        assert isinstance(gamma, (int, float)), f"gamma must be a float or int number, but got {gamma}"
        assert isinstance(fit_intercept, bool), "fit_intercept must be bool value!"

        self.beta = None
        self.gamma = 0 if penalty is None else gamma
        self.penalty = penalty
        self.fit_intercept = fit_intercept
        self._is_fit = False

    def fit(self, X: np.ndarray, y: np.ndarray, lr=0.01, tol=1e-7, max_iter=10000, verbose: bool = True):
        """
        Parameters
        ----------
        X : :py:class:`ndarray <numpy.ndarray>` of shape `(N, M)`
            A dataset consisting of `N` examples, each of dimension `M`.
        y : :py:class:`ndarray <numpy.ndarray>` of shape `(N,)`
            The targets for each of the `N` examples in `X`.
        lr : float
            The gradient descent learning rate. Default is 0.01.
        tol : float
            Tolerance for convergence. Default is 1e-7.
        max_iter : int
            The maximum number of iterations to run the gradient descent
            solver. Default is 10000.
        verbose : bool
            Whether to print progress. Default is True.
        """

        # convert X to a design matrix if we're fitting an intercept
        if self.fit_intercept:
            X = np.c_[np.ones(X.shape[0]), X]

        assert y.ndim == 1, "y should be 1-D array!"
        assert X.ndim == 2, "X should be 2-D array!"

        N, M = X.shape
        self.k = len(np.unique(y))
        self.W = simplex_matrix(self.k)

        # Initialize beta matrix (M x k-1)
        self.beta = np.random.randn(M, self.k - 1) * 0.01

        # Convert y to one-hot encoding
        y_onehot = np.eye(self.k)[y]

        # Gradient descent optimization
        prev_loss = float('inf')
        for i in range(int(max_iter)):
            # Compute probabilities
            probs = self._compute_probabilities(X)

            # Compute loss
            loss = self._NLL(X, y_onehot, probs)

            # Check convergence
            if abs(prev_loss - loss) < tol:
                if verbose:
                    print(f"Converged after {i+1} iterations, loss: {loss:.6f}")
                break

            prev_loss = loss

            # Compute gradient
            gradient = self._compute_gradient(X, y_onehot, probs)

            # Update beta
            self.beta -= lr * gradient

            if verbose and (i + 1) % 1000 == 0:
                print(f"Iteration {i+1}, loss: {loss:.6f}")

        self._is_fit = True


    def _compute_probabilities(self, X):
        """Compute class probabilities using the simplex transformation."""
        N = X.shape[0]
        probs = np.zeros((N, self.k))

        for i in range(self.k):
            # Compute linear combination for each class
            linear_combo = X @ self.beta @ self.W[:, i]
            probs[:, i] = linear_combo

        # Apply softmax to get probabilities
        # Subtract max for numerical stability
        probs = probs - np.max(probs, axis=1, keepdims=True)
        probs = np.exp(probs)
        probs = probs / np.sum(probs, axis=1, keepdims=True)

        return probs

    def _compute_gradient(self, X, y_true, probs):
        """Compute the gradient of the negative log likelihood."""
        N = X.shape[0]
        gradient = np.zeros_like(self.beta)

        for i in range(self.k):
            # Residual for class i
            residual = probs[:, i] - y_true[:, i]
            # Gradient contribution for class i
            gradient += X.T @ (residual.reshape(-1, 1) @ self.W[:, i].reshape(1, -1))

        # Add regularization if specified
        if self.penalty == 'l1':
            gradient += self.gamma * np.sign(self.beta)
        elif self.penalty == 'l2':
            gradient += self.gamma * self.beta

        return gradient / N

    def _NLL(self, X, y, probs):
        """
        Penalized negative log likelihood of the targets under the current
        model for multinomial classification.
        """
        N = X.shape[0]
        beta, gamma = self.beta, self.gamma

        # Multinomial negative log likelihood
        nll = -np.sum(y * np.log(probs + 1e-15))  # Add small epsilon to avoid log(0)

        # Regularization penalty
        if self.penalty == 'l1':
            penalty = gamma * np.sum(np.abs(beta))
        elif self.penalty == 'l2':
            penalty = (gamma / 2) * np.sum(beta ** 2)
        else:
            penalty = 0

        return (nll + penalty) / N
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict dataset X for its labels

        Parameters
        -----

        :param X: data matrix.
        """

        assert self._is_fit, "Please use .fit() first to fit your model."

        # Add intercept if needed
        if self.fit_intercept:
            X = np.c_[np.ones(X.shape[0]), X]

        # Get probabilities
        probs = self._compute_probabilities(X)

        # Return class predictions
        return np.argmax(probs, axis=1)


    def predict_prob(self, X: np.ndarray) -> np.ndarray:
        """
        Predict dataset X for its label probability

        Parameters
        -----

        :param X: data matrix.
        """
        assert self._is_fit, "Please use .fit() first to fit your model."

        # Add intercept if needed
        if self.fit_intercept:
            X = np.c_[np.ones(X.shape[0]), X]

        # Get probabilities
        return self._compute_probabilities(X)
    
        
    
    def _get_params(self) -> dict:
        return {
            "beta": self.beta,
            "gamma": self.gamma,
            "penalty": self.penalty,
            "fit_intercept": self.fit_intercept,
            "_is_fit": self._is_fit,
        }
    
    

    

