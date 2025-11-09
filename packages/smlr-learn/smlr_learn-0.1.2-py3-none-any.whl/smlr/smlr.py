import numpy as np
from .utils.functions import simplex_matrix
import warnings


class SMLR:
    """
    Simplex-Based Multinomial Logistic Regression (Proximal Optimization)

    Implements the model from Fu et al. (2024), optimized by proximal
    gradient descent supporting L1/L2 penalties.
    """

    def __init__(self, penalty: None | str = None, gamma: float | int = 0, fit_intercept: bool = True):
        """
        Parameters
        ----------
        penalty : {'l1', 'l2', None}
            Regularization type. 'l1' uses soft thresholding.
        gamma : float
            Regularization strength.
        fit_intercept : bool
            Whether to fit an intercept term.
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

    # -----------------------------------------------------------
    # Core optimization (proximal gradient)
    # -----------------------------------------------------------
    def fit(self, X: np.ndarray, y: np.ndarray,
            lr: float = 0.05, tol: float = 1e-7,
            max_iter: int = 10000, verbose: bool = True):
        """
        Fit the SMLR model using proximal gradient descent.

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
        self.k = len(np.unique(y))
        self.W = simplex_matrix(self.k)

        # Initialize coefficients (M x (k-1))
        self.beta = np.random.randn(M, self.k - 1) * 0.01
        Y = np.eye(self.k)[y]

        prev_loss = np.inf
        for i in range(max_iter):
            # Forward: compute scores & probs
            scores = X @ self.beta @ self.W
            probs = self._softmax(scores)

            # Compute gradient of smooth part
            grad = X.T @ ((probs - Y) @ self.W.T) / N

            # Gradient step
            Z = self.beta - lr * grad

            # Proximal operator
            self.beta = self._prox(Z, lr)

            # Check convergence by parameter change
            delta = np.linalg.norm(lr * grad)
            if delta < tol:
                if verbose:
                    print(f"Converged after {i+1} iterations, |Δβ|={delta:.3e}")
                break

            # Monitor every 1000 iters
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
        """Proximal operator for penalty."""
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
        scores = X @ self.beta @ self.W
        return self._softmax(scores)

    def _get_params(self) -> dict:
        return {
            "beta": self.beta,
            "gamma": self.gamma,
            "penalty": self.penalty,
            "fit_intercept": self.fit_intercept,
            "_is_fit": self._is_fit,
        }
