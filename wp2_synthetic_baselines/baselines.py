"""
wp2_synthetic_baselines/baselines.py
======================================
Implements the five supervised baseline classifiers (Proposal §4.2).

Each classifier is wrapped in a thin class that inherits BaseSSLModel so it
plugs into WP5's evaluation suite.

Classifiers
-----------
1. GaussianNaiveBayes
2. LogisticRegressionModel
3. KNNClassifierModel
4. DecisionTreeModel
5. SVMModel

Training modes (each class supports all three):
  gold_only     – fit on D_L only
  naive_pool    – fit on D_L ∪ D_U, treating noisy labels as clean
  self_training – iterative self-labelling from D_L
"""

import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.base import clone

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.base_model import BaseSSLModel


# ── Helper: self-training loop ────────────────────────────────────────────

def self_training_fit(
    base_clf,
    X_L: np.ndarray,
    y_L: np.ndarray,
    X_U: np.ndarray,
    threshold: float = 0.90,
    max_iter: int = 20,
):
    """
    Generic self-training wrapper.
    In each round, adds unlabeled samples with max predicted probability
    above `threshold` to the labeled pool.
    Returns the fitted classifier.
    """
    X_labeled = X_L.copy()
    y_labeled = y_L.copy()
    X_unlabeled = X_U.copy()

    clf = clone(base_clf)

    for _ in range(max_iter):
        if len(X_unlabeled) == 0:
            break

        # 1. Fit on current labeled pool
        clf.fit(X_labeled, y_labeled)

        # 2. Predict probabilities on remaining unlabeled data
        proba = clf.predict_proba(X_unlabeled)
        max_proba = proba.max(axis=1)
        pred_labels = proba.argmax(axis=1)

        # 3. Identify rows where max probability > threshold
        confident_mask = max_proba > threshold
        if not np.any(confident_mask):
            break

        # 4. Move confident samples to the labeled pool
        X_labeled = np.vstack([X_labeled, X_unlabeled[confident_mask]])
        y_labeled = np.hstack([y_labeled, pred_labels[confident_mask]])
        X_unlabeled = X_unlabeled[~confident_mask]

    # Final fit on the full labeled pool
    clf.fit(X_labeled, y_labeled)
    return clf


# ── 1. Gaussian Naïve Bayes ────────────────────────────────────────────────

class GaussianNaiveBayes(BaseSSLModel):
    """Gaussian Naïve Bayes with three training modes."""

    def __init__(self, mode: str = "gold_only"):
        super().__init__(name=f"GNB-{mode}")
        assert mode in ("gold_only", "naive_pool", "self_training")
        self.mode = mode
        self._clf = GaussianNB()

    def fit(self, X_L, y_L, X_U, y_U_noisy=None):
        if self.mode == "gold_only":
            self._clf.fit(X_L, y_L)
        elif self.mode == "naive_pool":
            X_all = np.vstack([X_L, X_U])
            y_all = np.hstack([y_L, y_U_noisy])
            self._clf.fit(X_all, y_all)
        elif self.mode == "self_training":
            self._clf = self_training_fit(self._clf, X_L, y_L, X_U)
        self._is_fitted = True
        return self

    def predict(self, X):
        return self._clf.predict(X)

    def predict_proba(self, X):
        return self._clf.predict_proba(X)


# ── 2. Logistic Regression ─────────────────────────────────────────────────

class LogisticRegressionModel(BaseSSLModel):

    def __init__(self, mode: str = "gold_only", C: float = 1.0, class_weight=None):
        suffix = "-bal" if class_weight == "balanced" else ""
        super().__init__(name=f"LR{suffix}-{mode}")
        self.mode = mode
        self._clf = Pipeline([
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(
                C=C, max_iter=1000, solver="lbfgs",
                class_weight=class_weight, random_state=42,
            )),
        ])

    def fit(self, X_L, y_L, X_U, y_U_noisy=None):
        if self.mode == "gold_only":
            self._clf.fit(X_L, y_L)
        elif self.mode == "naive_pool":
            X_all = np.vstack([X_L, X_U])
            y_all = np.hstack([y_L, y_U_noisy])
            self._clf.fit(X_all, y_all)
        elif self.mode == "self_training":
            self._clf = self_training_fit(self._clf, X_L, y_L, X_U)
        self._is_fitted = True
        return self

    def predict(self, X):
        return self._clf.predict(X)

    def predict_proba(self, X):
        return self._clf.predict_proba(X)


# ── 3. k-NN ───────────────────────────────────────────────────────────────

class KNNClassifierModel(BaseSSLModel):

    def __init__(self, mode: str = "gold_only", k: int = 7):
        super().__init__(name=f"kNN(k={k})-{mode}")
        self.mode = mode
        self._clf = Pipeline([
            ("scaler", StandardScaler()),
            ("knn", KNeighborsClassifier(n_neighbors=k)),
        ])

    def fit(self, X_L, y_L, X_U, y_U_noisy=None):
        if self.mode == "gold_only":
            self._clf.fit(X_L, y_L)
        elif self.mode == "naive_pool":
            X_all = np.vstack([X_L, X_U])
            y_all = np.hstack([y_L, y_U_noisy])
            self._clf.fit(X_all, y_all)
        elif self.mode == "self_training":
            self._clf = self_training_fit(self._clf, X_L, y_L, X_U)
        self._is_fitted = True
        return self

    def predict(self, X):
        return self._clf.predict(X)

    def predict_proba(self, X):
        return self._clf.predict_proba(X)


# ── 4. Decision Tree ──────────────────────────────────────────────────────

class DecisionTreeModel(BaseSSLModel):

    def __init__(self, mode: str = "gold_only",
                 max_depth: int | None = None, class_weight=None):
        suffix = "-bal" if class_weight == "balanced" else ""
        super().__init__(name=f"DT(depth={max_depth}){suffix}-{mode}")
        self.mode = mode
        self.max_depth_param = max_depth
        self._clf = DecisionTreeClassifier(
            max_depth=max_depth, class_weight=class_weight, random_state=42
        )
        self.tree_depth_ = None
        self.n_leaves_ = None

    def fit(self, X_L, y_L, X_U, y_U_noisy=None):
        if self.mode == "gold_only":
            self._clf.fit(X_L, y_L)
        elif self.mode == "naive_pool":
            X_all = np.vstack([X_L, X_U])
            y_all = np.hstack([y_L, y_U_noisy])
            self._clf.fit(X_all, y_all)
        elif self.mode == "self_training":
            self._clf = self_training_fit(self._clf, X_L, y_L, X_U)
        self.tree_depth_ = self._clf.get_depth()
        self.n_leaves_ = self._clf.get_n_leaves()
        self._is_fitted = True
        return self

    def predict(self, X):
        return self._clf.predict(X)

    def predict_proba(self, X):
        return self._clf.predict_proba(X)


# ── 5. SVM ────────────────────────────────────────────────────────────────

class SVMModel(BaseSSLModel):

    def __init__(self, mode: str = "gold_only", C: float = 1.0, class_weight=None):
        suffix = "-bal" if class_weight == "balanced" else ""
        super().__init__(name=f"SVM(C={C}){suffix}-{mode}")
        self.mode = mode
        base_svc = SVC(
            C=C, kernel="rbf", class_weight=class_weight,
            cache_size=500, random_state=42,
        )
        # CalibratedClassifierCV(..., ensemble=False) fits 1 final SVC + 3-fold Platt scaling
        self._clf = Pipeline([
            ("scaler", StandardScaler()),
            ("svm", CalibratedClassifierCV(base_svc, cv=3, ensemble=False)),
        ])
        self.n_support_vectors_ = None

    def fit(self, X_L, y_L, X_U, y_U_noisy=None):
        if self.mode == "gold_only":
            self._clf.fit(X_L, y_L)
        elif self.mode == "naive_pool":
            X_all = np.vstack([X_L, X_U])
            y_all = np.hstack([y_L, y_U_noisy])
            self._clf.fit(X_all, y_all)
        elif self.mode == "self_training":
            self._clf = self_training_fit(
                self._clf, X_L, y_L, X_U,
                threshold=0.95, max_iter=5,
            )

        svm_step = self._clf.named_steps.get("svm", self._clf)
        if hasattr(svm_step, "calibrated_classifiers_") and svm_step.calibrated_classifiers_:
            est = svm_step.calibrated_classifiers_[0].estimator
            if hasattr(est, "n_support_"):
                self.n_support_vectors_ = int(est.n_support_.sum())
        elif hasattr(svm_step, "n_support_"):
            self.n_support_vectors_ = int(svm_step.n_support_.sum())
        else:
            self.n_support_vectors_ = None
        self._is_fitted = True
        return self

    def predict(self, X):
        return self._clf.predict(X)

    def predict_proba(self, X):
        return self._clf.predict_proba(X)
