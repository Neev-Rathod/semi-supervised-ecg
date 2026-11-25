"""
wp4_cotraining_tsvm/run_wp4.py
================================
Entry point for Work Package 4: Co-Training & Transductive SVMs.

Experiments
-----------
1. Sweep η (gold fraction) for Multi-View Co-Training:
   - Compares Co-Training against supervised baselines (2-View Ensemble, Full 84D, View 1, View 2).
   - Tracks accuracy, macro F1, per-class F1, ROC-AUC, PR-AUC, and inter-view agreement rate.
2. Sweep η for Transductive SVM (TSVM):
   - Compares TSVM against supervised inductive SVM baseline.
   - Evaluates accuracy, macro F1, margin stability, support vector counts, and class imbalance effects.
3. Track and visualize inter-view agreement dynamics across co-training rounds.
4. Analyze margin stability and support vector distribution under severe class imbalance.

Usage
-----
    python run_wp4.py \\
        --features_path ../outputs/wp1/features.npz \\
        --labels_path   ../outputs/wp1/labels.npz   \\
        --out_dir       ../outputs/wp4
"""

import argparse
import sys
import time
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shared.data_utils import SUPERCLASSES, load_standard_split
from shared.metrics import evaluate_model
from wp4_cotraining_tsvm.cotraining import (
    VIEW1,
    VIEW2,
    CoTrainer,
    _align_proba,
    _make_base_clf,
)
from wp4_cotraining_tsvm.tsvm import TSVMClassifier


def parse_args():
    p = argparse.ArgumentParser(description="WP4 – Co-Training & Transductive SVMs")
    p.add_argument("--features_path", required=True, help="Path to features.npz")
    p.add_argument("--labels_path",   required=True, help="Path to labels.npz")
    p.add_argument("--out_dir",       default=str(Path("..") / "outputs" / "wp4"))
    p.add_argument("--eta_values",    default="0.02,0.05,0.10,0.20,0.50")
    p.add_argument("--seed",          type=int, default=42)
    p.add_argument("--max_records",   type=int, default=None, help="Cap unlabeled pool size")
    p.add_argument("--eval_test",     action="store_true", help="Also evaluate on test fold")
    return p.parse_args()


def subsample_gold(X_L: np.ndarray, y_L: np.ndarray, eta: float, seed: int, stratify: bool = True):
    """
    Subsample a fraction eta of the Gold Set.
    Uses stratified sampling to maintain class proportions across small eta.
    """
    n = max(5, int(eta * len(X_L)))
    if n >= len(X_L):
        return X_L.copy(), y_L.copy()

    if stratify:
        try:
            from sklearn.model_selection import train_test_split
            idx, _ = train_test_split(
                np.arange(len(X_L)),
                train_size=n,
                stratify=y_L,
                random_state=seed,
            )
            return X_L[idx], y_L[idx]
        except Exception:
            pass

    rng = np.random.default_rng(seed)
    idx = rng.choice(len(X_L), size=n, replace=False)
    return X_L[idx], y_L[idx]


class _TwoViewEnsemble:
    """Wrapper for supervised 2-view baseline (same architecture as CoTrainer, without X_U)."""

    def __init__(self, h1, h2):
        self.h1 = h1
        self.h2 = h2

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        p1 = _align_proba(self.h1, X[:, VIEW1])
        p2 = _align_proba(self.h2, X[:, VIEW2])
        return (p1 + p2) / 2.0

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.argmax(self.predict_proba(X), axis=1)


def run_eta_sweep_cotraining(
    X_L_full: np.ndarray,
    y_L_full: np.ndarray,
    X_U: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    eta_values: list[float],
    out_dir: Path,
    seed: int = 42,
    X_test: np.ndarray | None = None,
    y_test: np.ndarray | None = None,
) -> tuple[pd.DataFrame, dict[float, list[dict]]]:
    """Sweep eta (gold fraction) for Co-Training vs Supervised Baselines."""
    print("\n" + "=" * 68)
    print("  EXPERIMENT 1: Co-Training η Sweep & View Agreement Analysis")
    print("=" * 68)

    rows = []
    agreement_curves = {}

    for eta in eta_values:
        t0 = time.time()
        X_L, y_L = subsample_gold(X_L_full, y_L_full, eta, seed=seed)
        n_gold = len(X_L)

        # 1. Supervised Full-84D Baseline (Gold-only)
        base_full = _make_base_clf(random_state=seed)
        base_full.fit(X_L, y_L)
        res_base_full = evaluate_model(base_full, X_val, y_val)
        acc_base_full = float(accuracy_score(y_val, base_full.predict(X_val)))

        # 2. Supervised View 1, View 2, and 2-View Ensemble Baselines (Gold-only)
        base_v1 = _make_base_clf(random_state=seed)
        base_v1.fit(X_L[:, VIEW1], y_L)
        res_base_v1 = evaluate_model(base_v1, X_val[:, VIEW1], y_val)

        base_v2 = _make_base_clf(random_state=seed)
        base_v2.fit(X_L[:, VIEW2], y_L)
        res_base_v2 = evaluate_model(base_v2, X_val[:, VIEW2], y_val)

        base_2v = _TwoViewEnsemble(base_v1, base_v2)
        res_base_2v = evaluate_model(base_2v, X_val, y_val)
        acc_base_2v = float(accuracy_score(y_val, base_2v.predict(X_val)))

        # 3. Multi-View Co-Training
        cotrainer = CoTrainer(
            n_rounds=12,
            p=10,
            threshold=0.72,
            pseudo_weight=0.35,
            non_contradict=True,
            random_state=seed,
        )
        cotrainer.fit(X_L, y_L, X_U)
        res_cotrain = evaluate_model(cotrainer, X_val, y_val)
        acc_cotrain = float(accuracy_score(y_val, cotrainer.predict(X_val)))
        final_agreement = cotrainer.compute_agreement(X_U)
        agreement_curves[eta] = cotrainer.history_

        row = {
            "eta": eta,
            "n_gold": n_gold,
            "n_unlabeled": len(X_U),
            "cotrain_accuracy": round(acc_cotrain, 4),
            "cotrain_macro_f1": res_cotrain["macro_f1"],
            "cotrain_roc_auc": res_cotrain["roc_auc"],
            "cotrain_pr_auc": res_cotrain["pr_auc"],
            "cotrain_final_agreement": round(final_agreement, 4),
            "cotrain_rounds_run": len(cotrainer.history_),
            "base_2v_accuracy": round(acc_base_2v, 4),
            "base_2v_macro_f1": res_base_2v["macro_f1"],
            "base_full_accuracy": round(acc_base_full, 4),
            "base_full_macro_f1": res_base_full["macro_f1"],
            "base_full_roc_auc": res_base_full["roc_auc"],
            "base_full_pr_auc": res_base_full["pr_auc"],
            "base_v1_macro_f1": res_base_v1["macro_f1"],
            "base_v2_macro_f1": res_base_v2["macro_f1"],
            "acc_gain_over_2v": round(acc_cotrain - acc_base_2v, 4),
            "f1_gain_over_2v": round(res_cotrain["macro_f1"] - res_base_2v["macro_f1"], 4),
            "f1_gain_over_full": round(res_cotrain["macro_f1"] - res_base_full["macro_f1"], 4),
        }

        for cls in SUPERCLASSES:
            row[f"cotrain_f1_{cls}"] = res_cotrain["per_class_f1"].get(cls, 0.0)
            row[f"base_f1_{cls}"] = res_base_2v["per_class_f1"].get(cls, 0.0)

        if X_test is not None and y_test is not None:
            res_test = evaluate_model(cotrainer, X_test, y_test)
            row["test_cotrain_accuracy"] = round(float(accuracy_score(y_test, cotrainer.predict(X_test))), 4)
            row["test_cotrain_macro_f1"] = res_test["macro_f1"]
            row["test_cotrain_roc_auc"] = res_test["roc_auc"]

        rows.append(row)
        elapsed = time.time() - t0
        print(
            f"  [Co-Training] η={eta:4.2f} ({n_gold:4d} gold) | "
            f"Base2V Acc={acc_base_2v:.4f} F1={res_base_2v['macro_f1']:.4f} | "
            f"CoTrain Acc={acc_cotrain:.4f} ({row['acc_gain_over_2v']:+.4f}) "
            f"F1={res_cotrain['macro_f1']:.4f} ({row['f1_gain_over_2v']:+.4f}) | "
            f"Agr={final_agreement:.3f} | {elapsed:.1f}s"
        )

    df = pd.DataFrame(rows)
    csv_path = out_dir / "cotraining_eta_sweep.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n[WP4] Saved Co-Training sweep results to: {csv_path}")

    plot_f1_vs_eta_cotraining(df, out_dir)
    plot_view_agreement(agreement_curves, out_dir)

    return df, agreement_curves


def run_eta_sweep_tsvm(
    X_L_full: np.ndarray,
    y_L_full: np.ndarray,
    X_U: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    eta_values: list[float],
    out_dir: Path,
    seed: int = 42,
    X_test: np.ndarray | None = None,
    y_test: np.ndarray | None = None,
) -> pd.DataFrame:
    """Sweep eta (gold fraction) for TSVM vs Inductive Supervised SVM."""
    print("\n" + "=" * 68)
    print("  EXPERIMENT 2: TSVM η Sweep & Margin Stability Analysis")
    print("=" * 68)

    rows = []
    sv_breakdowns = []

    for eta in eta_values:
        t0 = time.time()
        X_L, y_L = subsample_gold(X_L_full, y_L_full, eta, seed=seed)
        n_gold = len(X_L)

        # 1. Inductive Supervised SVM Baseline (scaler fit on Gold Set X_L only)
        scaler_base = StandardScaler()
        X_L_b = scaler_base.fit_transform(X_L)
        base_svm = SVC(
            C=1.0,
            kernel="rbf",
            class_weight="balanced",
            decision_function_shape="ovr",
            random_state=seed,
        )
        base_svm.fit(X_L_b, y_L)

        class SVMWrapper:
            def __init__(self, clf, sc):
                self.clf = clf
                self.sc = sc
            def predict(self, X):
                return self.clf.predict(self.sc.transform(X))
            def predict_proba(self, X):
                sc = self.clf.decision_function(self.sc.transform(X))
                if sc.ndim == 1:
                    sc = np.column_stack([-sc, sc])
                n_c = len(self.clf.classes_)
                if n_c < 5 or not np.array_equal(self.clf.classes_, np.arange(5)):
                    aligned = np.full((len(X), 5), -1e9, dtype=float)
                    for i, c in enumerate(self.clf.classes_):
                        if 0 <= c < 5:
                            aligned[:, c] = sc[:, i]
                    sc = aligned
                sc = sc - sc.max(axis=1, keepdims=True)
                ex = np.exp(sc)
                return ex / ex.sum(axis=1, keepdims=True)

        base_wrapper = SVMWrapper(base_svm, scaler_base)
        res_base_svm = evaluate_model(base_wrapper, X_val, y_val)
        acc_base_svm = float(accuracy_score(y_val, base_wrapper.predict(X_val)))
        base_sv_count = int(np.sum(base_svm.n_support_))

        # 2. Transductive SVM (margin-filtered + confidence-weighted + C_U annealing)
        tsvm = TSVMClassifier(
            C_L=2.0,
            C_U=0.05,
            C_U_max=0.30,
            margin_percentile=65.0,
            kernel="rbf",
            max_iter=3,
            class_weight="balanced",
            random_state=seed,
        )
        tsvm.fit(X_L, y_L, X_U)
        res_tsvm = evaluate_model(tsvm, X_val, y_val)
        acc_tsvm = float(accuracy_score(y_val, tsvm.predict(X_val)))
        tsvm_sv_count = tsvm.total_support_vectors_

        row = {
            "eta": eta,
            "n_gold": n_gold,
            "n_unlabeled": len(X_U),
            "n_unlabeled_kept": tsvm.n_unlabeled_kept_,
            "tsvm_accuracy": round(acc_tsvm, 4),
            "tsvm_macro_f1": res_tsvm["macro_f1"],
            "tsvm_roc_auc": res_tsvm["roc_auc"],
            "tsvm_pr_auc": res_tsvm["pr_auc"],
            "tsvm_total_sv": tsvm_sv_count,
            "base_svm_accuracy": round(acc_base_svm, 4),
            "base_svm_macro_f1": res_base_svm["macro_f1"],
            "base_svm_roc_auc": res_base_svm["roc_auc"],
            "base_svm_pr_auc": res_base_svm["pr_auc"],
            "base_svm_total_sv": base_sv_count,
            "acc_gain_over_base": round(acc_tsvm - acc_base_svm, 4),
            "f1_gain_over_base": round(res_tsvm["macro_f1"] - res_base_svm["macro_f1"], 4),
        }

        for i, cls in enumerate(SUPERCLASSES):
            n_sv_c = int(tsvm.n_support_[i]) if i < len(tsvm.n_support_) else 0
            row[f"tsvm_sv_{cls}"] = n_sv_c
            row[f"tsvm_f1_{cls}"] = res_tsvm["per_class_f1"].get(cls, 0.0)
            row[f"base_f1_{cls}"] = res_base_svm["per_class_f1"].get(cls, 0.0)

        if X_test is not None and y_test is not None:
            res_test = evaluate_model(tsvm, X_test, y_test)
            row["test_tsvm_accuracy"] = round(float(accuracy_score(y_test, tsvm.predict(X_test))), 4)
            row["test_tsvm_macro_f1"] = res_test["macro_f1"]
            row["test_tsvm_roc_auc"] = res_test["roc_auc"]

        rows.append(row)
        sv_breakdowns.append({
            "eta": eta,
            "tsvm_n_support": tsvm.n_support_,
            "base_n_support": base_svm.n_support_,
        })

        elapsed = time.time() - t0
        print(
            f"  [TSVM]        η={eta:4.2f} ({n_gold:4d} gold) | "
            f"BaseSVM Acc={acc_base_svm:.4f} F1={res_base_svm['macro_f1']:.4f} | "
            f"TSVM Acc={acc_tsvm:.4f} ({row['acc_gain_over_base']:+.4f}) "
            f"F1={res_tsvm['macro_f1']:.4f} ({row['f1_gain_over_base']:+.4f}) | "
            f"SVs={tsvm_sv_count} | {elapsed:.1f}s"
        )

    df = pd.DataFrame(rows)
    csv_path = out_dir / "tsvm_eta_sweep.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n[WP4] Saved TSVM sweep results to: {csv_path}")

    plot_f1_vs_eta_tsvm(df, out_dir)
    plot_margin_stability_imbalance(df, sv_breakdowns, out_dir)

    return df


def plot_f1_vs_eta_cotraining(df: pd.DataFrame, out_dir: Path):
    """Plot Macro F1 & Accuracy vs Gold Fraction (η) for Co-Training and Baselines."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
    eta_pct = df["eta"] * 100

    # Macro F1
    ax1.plot(eta_pct, df["cotrain_macro_f1"], marker="o", linewidth=2.5, color="#1f77b4", label="Co-Training (Two-View SSL)")
    ax1.plot(eta_pct, df["base_2v_macro_f1"], marker="s", linewidth=2.0, linestyle="--", color="#2ca02c", label="Supervised 2-View Baseline (Gold)")
    ax1.plot(eta_pct, df["base_full_macro_f1"], marker="D", linewidth=1.6, linestyle="-.", color="#17becf", alpha=0.85, label="Supervised Full-84D Baseline (Gold)")
    ax1.plot(eta_pct, df["base_v1_macro_f1"], marker="^", linewidth=1.4, linestyle=":", color="#ff7f0e", alpha=0.8, label="View 1 Only (Temporal)")
    ax1.plot(eta_pct, df["base_v2_macro_f1"], marker="v", linewidth=1.4, linestyle=":", color="#9467bd", alpha=0.8, label="View 2 Only (Spectral)")
    ax1.set_title("Co-Training: Macro F1 vs. Gold Fraction (η)", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Gold Label Fraction η (%)", fontsize=10)
    ax1.set_ylabel("Macro F1 Score (Validation)", fontsize=10)
    ax1.set_xticks(eta_pct)
    ax1.set_xticklabels([f"{v:.0f}%" for v in eta_pct])
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(frameon=True, fontsize=8.5, loc="lower right")

    # Accuracy
    ax2.plot(eta_pct, df["cotrain_accuracy"] * 100, marker="o", linewidth=2.5, color="#1f77b4", label="Co-Training (Two-View SSL)")
    ax2.plot(eta_pct, df["base_2v_accuracy"] * 100, marker="s", linewidth=2.0, linestyle="--", color="#2ca02c", label="Supervised 2-View Baseline (Gold)")
    ax2.plot(eta_pct, df["base_full_accuracy"] * 100, marker="D", linewidth=1.6, linestyle="-.", color="#17becf", alpha=0.85, label="Supervised Full-84D Baseline (Gold)")
    ax2.set_title("Co-Training: Accuracy vs. Gold Fraction (η)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Gold Label Fraction η (%)", fontsize=10)
    ax2.set_ylabel("Accuracy (%)", fontsize=10)
    ax2.set_xticks(eta_pct)
    ax2.set_xticklabels([f"{v:.0f}%" for v in eta_pct])
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(frameon=True, fontsize=8.5, loc="lower right")

    plt.tight_layout()
    plot_path = out_dir / "f1_vs_eta_cotraining.png"
    plt.savefig(plot_path)
    plt.close(fig)
    print(f"[WP4] Generated plot: {plot_path}")


def plot_view_agreement(curves: dict[float, list[dict]], out_dir: Path):
    """Plot Inter-View Agreement Rate across Co-Training Iteration Rounds."""
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

    colors = ["#d62728", "#ff7f0e", "#2ca02c", "#1f77b4", "#9467bd"]
    for i, (eta, history) in enumerate(curves.items()):
        if not history:
            continue
        rounds = [h["round"] for h in history]
        agreements = [h["agreement"] * 100 for h in history]
        color = colors[i % len(colors)]
        ax.plot(
            rounds, agreements,
            marker="o", markersize=4, linewidth=2, color=color,
            label=f"η = {eta*100:.0f}% ({history[0].get('pool1_size', 0)} gold)",
        )

    ax.set_title("Inter-View Classifier Agreement Dynamics Across Rounds", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Co-Training Round (Iteration)", fontsize=11)
    ax.set_ylabel("Inter-View Agreement Rate on Untrusted Pool (%)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(frameon=True, fontsize=10, loc="lower right")

    plt.tight_layout()
    plot_path = out_dir / "view_agreement.png"
    plt.savefig(plot_path)
    plt.close(fig)
    print(f"[WP4] Generated plot: {plot_path}")


def plot_f1_vs_eta_tsvm(df: pd.DataFrame, out_dir: Path):
    """Plot Macro F1 & Accuracy vs Gold Fraction (η) for TSVM vs Supervised SVM."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
    eta_pct = df["eta"] * 100

    # Macro F1 + SVs
    l1 = ax1.plot(eta_pct, df["tsvm_macro_f1"], marker="o", linewidth=2.5, color="#d62728", label="Transductive SVM (TSVM)")
    l2 = ax1.plot(eta_pct, df["base_svm_macro_f1"], marker="s", linewidth=2.0, linestyle="--", color="#1f77b4", label="Supervised SVM Baseline (Gold)")
    ax1.set_title("TSVM: Macro F1 vs. Gold Fraction (η)", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Gold Label Fraction η (%)", fontsize=10)
    ax1.set_ylabel("Macro F1 Score (Validation)", fontsize=10)
    ax1.set_xticks(eta_pct)
    ax1.set_xticklabels([f"{v:.0f}%" for v in eta_pct])
    ax1.grid(True, linestyle="--", alpha=0.5)

    ax1_twin = ax1.twinx()
    l3 = ax1_twin.plot(eta_pct, df["tsvm_total_sv"], marker="^", linewidth=1.6, linestyle=":", color="#7f7f7f", alpha=0.85, label="TSVM Support Vectors")
    ax1_twin.set_ylabel("Total Support Vectors", fontsize=10, color="#7f7f7f")
    ax1_twin.tick_params(axis="y", labelcolor="#7f7f7f")

    lines = l1 + l2 + l3
    ax1.legend(lines, [l.get_label() for l in lines], frameon=True, fontsize=8.5, loc="lower right")

    # Accuracy
    ax2.plot(eta_pct, df["tsvm_accuracy"] * 100, marker="o", linewidth=2.5, color="#d62728", label="Transductive SVM (TSVM)")
    ax2.plot(eta_pct, df["base_svm_accuracy"] * 100, marker="s", linewidth=2.0, linestyle="--", color="#1f77b4", label="Supervised SVM Baseline (Gold)")
    ax2.set_title("TSVM: Accuracy vs. Gold Fraction (η)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Gold Label Fraction η (%)", fontsize=10)
    ax2.set_ylabel("Accuracy (%)", fontsize=10)
    ax2.set_xticks(eta_pct)
    ax2.set_xticklabels([f"{v:.0f}%" for v in eta_pct])
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(frameon=True, fontsize=9, loc="lower right")

    plt.tight_layout()
    plot_path = out_dir / "f1_vs_eta_tsvm.png"
    plt.savefig(plot_path)
    plt.close(fig)
    print(f"[WP4] Generated plot: {plot_path}")


def plot_margin_stability_imbalance(df: pd.DataFrame, sv_breakdowns: list[dict], out_dir: Path):
    """Analyze and visualize margin stability and support vector distribution under class imbalance."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    colors = ["#2ca02c", "#d62728", "#1f77b4", "#ff7f0e", "#9467bd"]
    eta_pct = df["eta"] * 100

    for i, cls in enumerate(SUPERCLASSES):
        col_name = f"tsvm_sv_{cls}"
        if col_name in df.columns:
            ax1.plot(eta_pct, df[col_name], marker="o", linewidth=2.0, color=colors[i], label=f"{cls}")

    ax1.set_title("TSVM Support Vectors per Superclass vs. η", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Gold Label Fraction η (%)", fontsize=10)
    ax1.set_ylabel("Number of Support Vectors", fontsize=10)
    ax1.set_xticks(eta_pct)
    ax1.set_xticklabels([f"{v:.0f}%" for v in eta_pct])
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(title="Superclass", frameon=True, fontsize=9)

    rep_row = df[df["eta"] == 0.10]
    if rep_row.empty:
        rep_row = df.iloc[len(df) // 2 : len(df) // 2 + 1]

    r = rep_row.iloc[0]
    x = np.arange(len(SUPERCLASSES))
    width = 0.35

    tsvm_f1s = [r.get(f"tsvm_f1_{cls}", 0.0) for cls in SUPERCLASSES]
    base_f1s = [r.get(f"base_f1_{cls}", 0.0) for cls in SUPERCLASSES]

    ax2.bar(x - width/2, base_f1s, width, label="Supervised SVM", color="#1f77b4", alpha=0.85)
    ax2.bar(x + width/2, tsvm_f1s, width, label="TSVM", color="#d62728", alpha=0.85)

    ax2.set_title(f"Per-Class F1 Breakdown under Class Imbalance (η = {r['eta']*100:.0f}%)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("ECG Superclass", fontsize=10)
    ax2.set_ylabel("F1 Score", fontsize=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(SUPERCLASSES, fontsize=10)
    ax2.set_ylim(0, 1.0)
    ax2.grid(True, linestyle="--", alpha=0.5, axis="y")
    ax2.legend(frameon=True, fontsize=10)

    frequencies = ["NORM (62.5%)", "MI (10.4%)", "STTC (13.9%)", "CD (9.9%)", "HYP (3.3%)"]
    for i, freq in enumerate(frequencies):
        ax2.text(i, 0.03, freq, ha="center", fontsize=7.5, rotation=90, color="white", fontweight="bold")

    plt.tight_layout()
    plot_path = out_dir / "margin_stability_imbalance.png"
    plt.savefig(plot_path)
    plt.close(fig)
    print(f"[WP4] Generated plot: {plot_path}")


def main():
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "#" * 68)
    print("  BITS F464: ML Project - WP4 Co-Training & Transductive SVMs")
    print("#" * 68)

    split = load_standard_split(args.features_path, args.labels_path, None)
    X_L_full = split["X_train_L"]
    y_L_full = split["y_train_L"]
    X_U      = split["X_train_U"]
    X_val    = split["X_val"]
    y_val    = split["y_val"]
    X_test   = split["X_test"] if args.eval_test else None
    y_test   = split["y_test"] if args.eval_test else None

    if args.max_records is not None and args.max_records < len(X_U):
        rng = np.random.default_rng(args.seed)
        sub_u = rng.choice(len(X_U), size=args.max_records, replace=False)
        X_U = X_U[sub_u]

    eta_values = [float(v) for v in args.eta_values.split(",")]

    print(f"[WP4] Loaded dataset:")
    print(f"[WP4]   Gold Set (D_L)     : {len(X_L_full):5d} records (84 features)")
    print(f"[WP4]   Untrusted Pool(D_U): {len(X_U):5d} records")
    print(f"[WP4]   Validation Set     : {len(X_val):5d} records")
    if args.eval_test:
        print(f"[WP4]   Test Set           : {len(X_test):5d} records")
    print(f"[WP4]   Gold Fractions (η) : {eta_values}")

    cotrain_df, _ = run_eta_sweep_cotraining(
        X_L_full=X_L_full, y_L_full=y_L_full, X_U=X_U,
        X_val=X_val, y_val=y_val, eta_values=eta_values,
        out_dir=out_dir, seed=args.seed, X_test=X_test, y_test=y_test,
    )

    tsvm_df = run_eta_sweep_tsvm(
        X_L_full=X_L_full, y_L_full=y_L_full, X_U=X_U,
        X_val=X_val, y_val=y_val, eta_values=eta_values,
        out_dir=out_dir, seed=args.seed, X_test=X_test, y_test=y_test,
    )

    print("\n" + "=" * 96)
    print("  WP4 SUMMARY RESULTS TABLE: Accuracy & Macro F1 vs. Gold Fraction (η)")
    print("=" * 96)
    print(
        f"{'η (%)':<7} {'Gold':<6} | "
        f"{'Base2V(Acc/F1)':<16} {'CoTrain(Acc/F1)':<17} {'Δ(Acc/F1)':<15} | "
        f"{'BaseSVM(Acc/F1)':<17} {'TSVM(Acc/F1)':<16} {'Δ(Acc/F1)':<15}"
    )
    print("-" * 96)
    for eta in eta_values:
        c = cotrain_df[cotrain_df["eta"] == eta].iloc[0]
        t = tsvm_df[tsvm_df["eta"] == eta].iloc[0]
        print(
            f"{eta*100:<6.1f}% {int(c['n_gold']):<6d} | "
            f"{c['base_2v_accuracy']:.3f}/{c['base_2v_macro_f1']:.3f}      "
            f"{c['cotrain_accuracy']:.3f}/{c['cotrain_macro_f1']:.3f}       "
            f"{c['acc_gain_over_2v']:+.3f}/{c['f1_gain_over_2v']:+.3f}   | "
            f"{t['base_svm_accuracy']:.3f}/{t['base_svm_macro_f1']:.3f}       "
            f"{t['tsvm_accuracy']:.3f}/{t['tsvm_macro_f1']:.3f}      "
            f"{t['acc_gain_over_base']:+.3f}/{t['f1_gain_over_base']:+.3f}"
        )
    print("=" * 96)
    print(f"[WP4] All deliverables written to directory: {out_dir}\n")


if __name__ == "__main__":
    main()
