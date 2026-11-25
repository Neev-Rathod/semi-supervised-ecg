"""
wp4_cotraining_tsvm/tsvm.py
=============================
Implements a Transductive SVM (Proposal §4.5) using margin-filtered iterative
label switching (Joachims 1999) with C_U annealing and class balancing.

Switching & Annealing Algorithm
-------------------------------
1. Standardize all data using StandardScaler fit on X_L ∪ X_U.
2. Train a class-balanced standard SVM on X_L to obtain initial pseudo-labels ŷ_U
   and decision margins on X_U.
3. Filter X_U to the top confident unlabeled points (above `margin_percentile`)
   and weight each retained unlabeled sample by its margin confidence, preventing
   noisy boundary points from collapsing the margin.
4. Anneal C_U from a small initial value up to C_U_max (bounded relative to
   N_L / N_U_kept so unlabeled points never overwhelm the Gold Set):
   a. Fit class-balanced SVC on [X_L, X_U_kept] with sample weights.
   b. Run iterative label switching on X_U_kept until convergence or max_iter.
   c. Double C_U.
5. Return the final fitted model.
"""

import warnings
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import ConvergenceWarning

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.base_model import BaseSSLModel


class TSVMClassifier(BaseSSLModel):
    """
    Transductive SVM (multi-class via one-vs-rest / pairwise SVC).

    Parameters
    ----------
    C_L               : regularization weight for labeled points (default 2.0)
    C_U               : initial regularization weight for unlabeled points (default 0.05)
    C_U_max           : maximum unlabeled regularization weight (default 0.30)
    margin_percentile : percentile of unlabeled decision margins below which
                        uncertain boundary points are excluded (default 65.0)
    kernel            : SVM kernel ('rbf', 'linear', etc.)
    max_iter          : maximum switching iterations per annealing step
    class_weight      : class weights (default 'balanced')
    random_state      : random seed for reproducibility
    """

    def __init__(
        self,
        C_L: float = 2.0,
        C_U: float = 0.05,
        C_U_max: float = 0.30,
        margin_percentile: float = 65.0,
        kernel: str = "rbf",
        max_iter: int = 3,
        class_weight="balanced",
        random_state: int = 42,
    ):
        super().__init__(name=f"TSVM(CL={C_L},CU={C_U}→{C_U_max})")
        self.C_L               = C_L
        self.C_U               = C_U
        self.C_U_max           = C_U_max
        self.margin_percentile = margin_percentile
        self.kernel            = kernel
        self.max_iter          = max_iter
        self.class_weight      = class_weight
        self.random_state      = random_state

        self._clf = None
        self._scaler = StandardScaler()
        self.n_support_ = None
        self.total_support_vectors_ = None
        self.n_unlabeled_kept_ = 0
        self.history_ = []

    def fit(self, X_L: np.ndarray, y_L: np.ndarray, X_U: np.ndarray, y_U_noisy: np.ndarray | None = None):
        """
        Fit a transductive SVM by margin-filtered iterative label switching with C_U annealing.
        y_U_noisy is ignored (TSVM treats unlabeled labels as latent optimization variables).
        """
        warnings.filterwarnings("ignore", category=ConvergenceWarning)
        warnings.filterwarnings("ignore", category=UserWarning)

        # 1. Scale data across X_L and X_U (transductive feature scaling)
        X_all = np.vstack([X_L, X_U])
        self._scaler.fit(X_all)
        X_L_s = self._scaler.transform(X_L)
        X_U_s = self._scaler.transform(X_U)

        # 2. Initial labels and margins for X_U from balanced SVM on D_L
        base_svm = SVC(
            C=1.0,
            kernel=self.kernel,
            class_weight=self.class_weight,
            decision_function_shape="ovr",
            random_state=self.random_state,
        )
        base_svm.fit(X_L_s, y_L)
        y_U_hat = base_svm.predict(X_U_s)
        df = base_svm.decision_function(X_U_s)
        if df.ndim == 1:
            margins = np.abs(df)
        else:
            s_sorted = np.sort(df, axis=1)
            margins = s_sorted[:, -1] - s_sorted[:, -2]

        # 3. Filter to confident unlabeled points & compute margin confidence weights
        thresh = np.percentile(margins, self.margin_percentile)
        keep_mask = margins >= thresh
        if not keep_mask.any():
            keep_mask = np.ones(len(X_U_s), dtype=bool)

        X_U_keep = X_U_s[keep_mask]
        y_U_keep = y_U_hat[keep_mask].copy()
        conf_keep = 1.0 / (1.0 + np.exp(-margins[keep_mask]))
        self.n_unlabeled_kept_ = int(keep_mask.sum())

        # 4. Annealing loop (cap C_U_max relative to N_L / N_U_kept)
        c_u_max = min(self.C_U_max, 0.8 * len(X_L) / max(1, len(X_U_keep)))
        C_U = min(self.C_U, c_u_max)
        X_train = np.vstack([X_L_s, X_U_keep])
        clf = None
        self.history_ = []

        while C_U <= c_u_max + 1e-9:
            weights = np.hstack([
                np.full(len(X_L), 1.0),
                C_U * conf_keep,
            ])

            clf = SVC(
                C=self.C_L,
                kernel=self.kernel,
                class_weight=self.class_weight,
                decision_function_shape="ovr",
                random_state=self.random_state,
            )
            y_train = np.hstack([y_L, y_U_keep])
            clf.fit(X_train, y_train, sample_weight=weights)

            # Inner switching loop
            swaps_in_step = 0
            for _ in range(self.max_iter):
                new_pred = clf.predict(X_U_keep)
                diff = (new_pred != y_U_keep)
                n_diff = int(diff.sum())
                if n_diff == 0:
                    break
                y_U_keep[diff] = new_pred[diff]
                swaps_in_step += n_diff
                y_train = np.hstack([y_L, y_U_keep])
                clf.fit(X_train, y_train, sample_weight=weights)

            n_sv = int(np.sum(clf.n_support_))
            self.history_.append({
                "C_U": float(C_U),
                "n_support": n_sv,
                "swaps": swaps_in_step,
            })

            if C_U >= c_u_max:
                break
            C_U = min(C_U * 2.0, c_u_max)

        self._clf = clf
        self.n_support_ = clf.n_support_
        self.total_support_vectors_ = int(np.sum(clf.n_support_))
        self._is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return hard class predictions."""
        X_s = self._scaler.transform(X)
        return self._clf.predict(X_s)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Return calibrated class probability estimates via softmax over decision function scores.
        """
        X_s = self._scaler.transform(X)
        scores = self._clf.decision_function(X_s)
        if scores.ndim == 1:
            scores = np.column_stack([-scores, scores])

        n_classes = len(self._clf.classes_)
        if n_classes < 5 or not np.array_equal(self._clf.classes_, np.arange(5)):
            aligned = np.full((len(X), 5), -1e9, dtype=float)
            for idx, c in enumerate(self._clf.classes_):
                if 0 <= c < 5:
                    aligned[:, c] = scores[:, idx]
            scores = aligned

        scores = scores - scores.max(axis=1, keepdims=True)
        exp_s = np.exp(scores)
        return exp_s / exp_s.sum(axis=1, keepdims=True)
