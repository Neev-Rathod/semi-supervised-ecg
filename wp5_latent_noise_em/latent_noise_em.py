"""Latent-noise EM with a regularized multinomial logistic classifier."""
import numpy as np
from scipy.optimize import minimize
from scipy.special import log_softmax, softmax
from sklearn.preprocessing import StandardScaler
from shared.base_model import BaseSSLModel


class LatentNoiseEM(BaseSSLModel):
    def __init__(self, n_classes=5, max_iter=30, tol=1e-4, alpha=1.5, C_lr=1.0):
        super().__init__("LatentNoiseEM")
        self.n_classes, self.max_iter, self.tol = n_classes, max_iter, tol
        self.alpha, self.C_lr = alpha, C_lr
        self.T_hat_ = None

    def fit(self, X_L, y_L, X_U, y_U_noisy=None):
        if y_U_noisy is None or len(y_U_noisy) != len(X_U):
            raise ValueError("Provide one observed label per pool record.")
        c = self.n_classes
        if self.alpha < 1 or self.C_lr <= 0 or self.max_iter < 1:
            raise ValueError("Invalid EM hyperparameters.")
        gold = np.eye(c)[y_L]
        observed = np.eye(c)[y_U_noisy]
        self.scaler_ = StandardScaler()
        scaled = self.scaler_.fit_transform(np.vstack([X_L, X_U]).astype(float))
        design = np.column_stack([scaled, np.ones(len(scaled))])
        weights = np.zeros((design.shape[1], c))

        def optimize(x, target, initial):
            def objective(flat):
                w = flat.reshape(initial.shape)
                logp = log_softmax(x @ w, axis=1)
                loss = -np.sum(target * logp) + np.sum(w[:-1]**2)/(2*self.C_lr)
                grad = x.T @ (np.exp(logp) - target)
                grad[:-1] += w[:-1]/self.C_lr
                return loss / len(x), grad.ravel() / len(x)
            result = minimize(objective, initial.ravel(), jac=True, method="L-BFGS-B",
                              options={"maxiter": 500, "ftol": 1e-10})
            if not result.success:
                raise RuntimeError(result.message)
            return result.x.reshape(initial.shape)

        weights = optimize(design[:len(gold)], gold, weights)
        transition = np.full((c, c), 0.1/(c-1))
        np.fill_diagonal(transition, 0.9)
        for self.n_iter_ in range(1, self.max_iter + 1):
            log_prior = log_softmax(design[len(gold):] @ weights, axis=1)
            with np.errstate(divide="ignore"):
                posterior = softmax(log_prior + np.log(transition[:, y_U_noisy].T), axis=1)
            counts = posterior.T @ observed + (self.alpha - 1)
            totals = counts.sum(axis=1, keepdims=True)
            updated = np.divide(counts, totals, out=transition.copy(), where=totals > 0)
            weights = optimize(design, np.vstack([gold, posterior]), weights)
            self.delta_ = np.linalg.norm(updated-transition)
            transition = updated
            if self.delta_ < self.tol:
                break
        self.weights_, self.T_hat_, self._is_fitted = weights, transition, True
        return self

    def predict_proba(self, X):
        return softmax(self.scaler_.transform(X) @ self.weights_[:-1] + self.weights_[-1], axis=1)

    def predict(self, X):
        return self.predict_proba(X).argmax(axis=1)

    def get_confusion_matrix(self):
        if self.T_hat_ is None:
            raise RuntimeError("Call fit() first.")
        return self.T_hat_
