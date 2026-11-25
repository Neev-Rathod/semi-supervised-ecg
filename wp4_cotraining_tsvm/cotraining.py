"""
wp4_cotraining_tsvm/cotraining.py
==================================
Implements Multi-View Co-Training (Proposal §4.4).

The two views are defined by WP1's feature layout:
  View 1 → feature indices 0:42  (time-domain / morphological)
  View 2 → feature indices 42:84 (frequency-domain / wavelet)

Algorithm (Blum & Mitchell 1998, with non-contradiction & confidence weighting)
------------------------------------------------------------------------------
1. Train classifier h1 on (X_L[:, V1], y_L) and h2 on (X_L[:, V2], y_L) with weight 1.0.
2. Each round:
   a. h1 picks up to top-p unlabeled samples per class with prob >= threshold
      that do NOT contradict h2 (h2's argmax prediction == c).
   b. Add those to h2's labeled pool with confidence-scaled weight (pseudo_weight * conf).
   c. h2 does the same for h1 symmetrically.
3. Repeat for T rounds or until no new samples are added.
"""

import warnings
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.base_model import BaseSSLModel

# View index slices (from WP1 feature layout)
VIEW1 = slice(0, 42)
VIEW2 = slice(42, 84)


def _make_base_clf(random_state: int = 42, class_weight=None):
    """Default base classifier for each view: regularized HistGradientBoosting."""
    return HistGradientBoostingClassifier(
        max_iter=100,
        learning_rate=0.06,
        max_depth=4,
        min_samples_leaf=10,
        l2_regularization=1.0,
        class_weight=class_weight,
        random_state=random_state,
    )


def _fit_with_optional_weight(clf, X: np.ndarray, y: np.ndarray, sample_weight: np.ndarray):
    """Fit estimator, passing sample_weight if supported."""
    try:
        clf.fit(X, y, sample_weight=sample_weight)
    except TypeError:
        clf.fit(X, y)


def _align_proba(clf, X: np.ndarray, n_classes: int = 5) -> np.ndarray:
    """Safely obtain probability estimates aligned to classes 0..n_classes-1."""
    raw_proba = clf.predict_proba(X)
    classes = getattr(clf, "classes_", None)
    if classes is None and hasattr(clf, "named_steps"):
        for step in reversed(list(clf.named_steps.values())):
            if hasattr(step, "classes_"):
                classes = step.classes_
                break

    if classes is not None and len(classes) == n_classes and np.array_equal(classes, np.arange(n_classes)):
        return raw_proba

    aligned = np.zeros((len(X), n_classes), dtype=float)
    if classes is not None:
        for col_idx, c in enumerate(classes):
            if 0 <= c < n_classes:
                aligned[:, c] = raw_proba[:, col_idx]
    return aligned


class CoTrainer(BaseSSLModel):
    """
    Two-view Co-Training classifier with non-contradiction filtering and
    confidence-weighted pseudo-labels.

    Parameters
    ----------
    n_rounds       : number of co-training iterations
    p              : max number of samples to add per class per round
    threshold      : minimum confidence to add a sample
    pseudo_weight  : base weight for pseudo-labeled samples relative to gold (1.0)
    non_contradict : if True, only add samples where the other view does not contradict
    base_clf_fn    : callable that returns a fresh sklearn estimator (optional)
    class_weight   : class weights for base classifier (e.g. 'balanced' or None)
    random_state   : random seed for reproducibility
    """

    def __init__(
        self,
        n_rounds: int = 12,
        p: int = 10,
        threshold: float = 0.72,
        pseudo_weight: float = 0.35,
        non_contradict: bool = True,
        base_clf_fn=None,
        class_weight=None,
        random_state: int = 42,
    ):
        super().__init__(name=f"CoTrainer(r={n_rounds},p={p},t={threshold})")
        self.n_rounds       = n_rounds
        self.p              = p
        self.threshold      = threshold
        self.pseudo_weight  = pseudo_weight
        self.non_contradict = non_contradict
        self.class_weight   = class_weight
        self.random_state   = random_state
        self._clf_fn        = base_clf_fn or (
            lambda: _make_base_clf(random_state=self.random_state, class_weight=self.class_weight)
        )
        self._h1 = None
        self._h2 = None
        self.history_ = []

    def fit(self, X_L: np.ndarray, y_L: np.ndarray, X_U: np.ndarray, y_U_noisy: np.ndarray | None = None):
        """
        Train two classifiers via co-training.
        y_U_noisy is ignored (co-training discards untrusted labels).
        """
        warnings.filterwarnings("ignore", category=UserWarning)

        X_L1 = X_L[:, VIEW1].copy()
        X_L2 = X_L[:, VIEW2].copy()
        X_U1 = X_U[:, VIEW1].copy()
        X_U2 = X_U[:, VIEW2].copy()

        L1_X, L1_y, L1_w = X_L1, y_L.copy(), np.ones(len(X_L), dtype=float)
        L2_X, L2_y, L2_w = X_L2, y_L.copy(), np.ones(len(X_L), dtype=float)

        remaining = np.arange(len(X_U))

        self._h1 = self._clf_fn()
        self._h2 = self._clf_fn()
        self.history_ = []

        n_classes = max(5, len(np.unique(y_L)) if len(y_L) > 0 else 5)

        for r in range(self.n_rounds):
            if len(remaining) == 0:
                break

            _fit_with_optional_weight(self._h1, L1_X, L1_y, L1_w)
            _fit_with_optional_weight(self._h2, L2_X, L2_y, L2_w)

            # Record inter-view agreement rate on the full X_U pool
            prob_all_1 = _align_proba(self._h1, X_U[:, VIEW1], n_classes)
            prob_all_2 = _align_proba(self._h2, X_U[:, VIEW2], n_classes)
            pred_all_1 = np.argmax(prob_all_1, axis=1)
            pred_all_2 = np.argmax(prob_all_2, axis=1)
            agreement  = float((pred_all_1 == pred_all_2).mean())

            # Evaluate probabilities on remaining unlabeled samples
            proba1 = _align_proba(self._h1, X_U1[remaining], n_classes)
            proba2 = _align_proba(self._h2, X_U2[remaining], n_classes)
            pred1  = np.argmax(proba1, axis=1)
            pred2  = np.argmax(proba2, axis=1)

            add_L2_idx, add_L2_y, add_L2_w = [], [], []
            add_L1_idx, add_L1_y, add_L1_w = [], [], []

            # h1 (View 1) selects high-confidence samples for L2 (View 2)
            for c in range(n_classes):
                conf = proba1[:, c]
                mask = conf >= self.threshold
                if self.non_contradict:
                    mask = mask & (pred2 == c)
                cand = np.where(mask)[0]
                if len(cand) > 0:
                    top_idx = cand[np.argsort(conf[cand])[-self.p:][::-1]]
                    for local_i in top_idx:
                        add_L2_idx.append(remaining[local_i])
                        add_L2_y.append(c)
                        add_L2_w.append(self.pseudo_weight * float(conf[local_i]))

            # h2 (View 2) selects high-confidence samples for L1 (View 1)
            for c in range(n_classes):
                conf = proba2[:, c]
                mask = conf >= self.threshold
                if self.non_contradict:
                    mask = mask & (pred1 == c)
                cand = np.where(mask)[0]
                if len(cand) > 0:
                    top_idx = cand[np.argsort(conf[cand])[-self.p:][::-1]]
                    for local_i in top_idx:
                        add_L1_idx.append(remaining[local_i])
                        add_L1_y.append(c)
                        add_L1_w.append(self.pseudo_weight * float(conf[local_i]))

            added_all = list(set(add_L2_idx + add_L1_idx))

            self.history_.append({
                "round": r + 1,
                "agreement": agreement,
                "added_h1": len(add_L2_idx),
                "added_h2": len(add_L1_idx),
                "total_added": len(added_all),
                "pool1_size": len(L1_y),
                "pool2_size": len(L2_y),
                "remaining": len(remaining),
            })

            if len(added_all) == 0:
                break

            if add_L2_idx:
                L2_X = np.vstack([L2_X, X_U[add_L2_idx, VIEW2]])
                L2_y = np.append(L2_y, add_L2_y)
                L2_w = np.append(L2_w, add_L2_w)

            if add_L1_idx:
                L1_X = np.vstack([L1_X, X_U[add_L1_idx, VIEW1]])
                L1_y = np.append(L1_y, add_L1_y)
                L1_w = np.append(L1_w, add_L1_w)

            remaining = np.setdiff1d(remaining, added_all)

        # Final fit of h1 and h2 on full enriched pools
        _fit_with_optional_weight(self._h1, L1_X, L1_y, L1_w)
        _fit_with_optional_weight(self._h2, L2_X, L2_y, L2_w)
        self._is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Return hard class predictions using averaged ensemble probabilities."""
        proba = self.predict_proba(X)
        return np.argmax(proba, axis=1)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Average the probability estimates from both views."""
        p1 = _align_proba(self._h1, X[:, VIEW1])
        p2 = _align_proba(self._h2, X[:, VIEW2])
        return (p1 + p2) / 2.0

    def compute_agreement(self, X: np.ndarray) -> float:
        """Compute the inter-view agreement rate on feature matrix X."""
        p1 = np.argmax(_align_proba(self._h1, X[:, VIEW1]), axis=1)
        p2 = np.argmax(_align_proba(self._h2, X[:, VIEW2]), axis=1)
        return float((p1 == p2).mean())
