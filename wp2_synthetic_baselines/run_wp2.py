"""
wp2_synthetic_baselines/run_wp2.py
====================================
Entry point for Work Package 2.

What this script does
---------------------
1. Synthetic mode (`--mode synthetic`):
   - Generates the 5-class synthetic manifold (3,000 samples, 50 dims).
   - Sweeps uniform noise ε ∈ [0, 0.60] across 5 classifiers × 3 modes:
     saves `noise_breakdown.csv`, `f1_vs_epsilon.png`,
     `svm_support_vectors.png`, and `tree_depth_vs_epsilon.png`.
   - Compares all THREE noise injectors (Uniform, Asymmetric, Boundary-Dependent
     Eq. 3.1) across severity levels and actual flip rates:
     saves `noise_type_comparison.csv` and `noise_types_comparison.png`.

2. PTB-XL mode (`--mode ptbxl`):
   - Loads WP1 features (`features.npz`, `labels.npz`).
   - Sweeps gold-set scarcity η ∈ {0.02, 0.05, 0.10, 0.20, 0.50, 1.00}
     against the real untrusted hospital pool D_U (no artificial corruption)
     for all 5 classifiers × 3 modes (plus balanced LR/SVM reference):
     saves `ptbxl_baselines.csv` and `ptbxl_baselines.png`.

3. All mode (`--mode all`): runs both synthetic and PTB-XL evaluations.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wp2_synthetic_baselines.synthetic_generator import (
    generate_manifold,
    inject_uniform_noise,
    inject_asymmetric_noise,
    inject_boundary_noise,
)
from wp2_synthetic_baselines.baselines import (
    GaussianNaiveBayes, LogisticRegressionModel,
    KNNClassifierModel, DecisionTreeModel, SVMModel,
)
from shared.data_utils import load_standard_split
from shared.metrics import evaluate_model


EPSILON_DEFAULT = [0.0, 0.15, 0.30, 0.45, 0.60]
ETA_DEFAULT     = [0.02, 0.05, 0.10, 0.20, 0.50, 1.00]
MODES_TRAIN     = ["gold_only", "naive_pool", "self_training"]


def parse_args():
    p = argparse.ArgumentParser(description="WP2 – Synthetic Generator & Supervised Baselines")
    p.add_argument("--mode",          default="synthetic", choices=["synthetic", "ptbxl", "all"])
    p.add_argument("--features_path", default=None)
    p.add_argument("--labels_path",   default=None)
    p.add_argument("--out_dir",       default=str(Path("..") / "outputs" / "wp2"))
    p.add_argument("--epsilon_values",default="0,0.15,0.30,0.45,0.60")
    p.add_argument("--eta_values",    default="0.02,0.05,0.10,0.20,0.50,1.00")
    p.add_argument("--seed",          type=int, default=42)
    return p.parse_args()


# ── Classifier constructors ──────────────────────────────────────────────

CLF_CLASSES = {
    "GNB": GaussianNaiveBayes,
    "LR":  LogisticRegressionModel,
    "kNN": KNNClassifierModel,
    "DT":  lambda mode: DecisionTreeModel(mode=mode, max_depth=None),
    "SVM": SVMModel,
}


def _make_clf(name: str, mode: str, class_weight=None):
    """Construct a fresh classifier instance by name and training mode."""
    if name == "DT":
        return DecisionTreeModel(mode=mode, max_depth=None, class_weight=class_weight)
    if name == "LR":
        return LogisticRegressionModel(mode=mode, class_weight=class_weight)
    if name == "SVM":
        return SVMModel(mode=mode, class_weight=class_weight)
    cls = CLF_CLASSES[name]
    return cls(mode=mode)


def _make_pair_confusion_T(p: float, n_classes: int = 5) -> np.ndarray:
    """Build asymmetric transition matrix confusing pairs (0,1) and (2,3) with rate p."""
    T = np.eye(n_classes)
    T[0, 0] = 1.0 - p; T[0, 1] = p
    T[1, 1] = 1.0 - p; T[1, 0] = p
    T[2, 2] = 1.0 - p; T[2, 3] = p
    T[3, 3] = 1.0 - p; T[3, 2] = p
    return T


# ── Experiment 1: Uniform Noise Breakdown (Synthetic) ────────────────────

def run_breakdown_analysis(
    X_L, y_L,
    X_U, y_U_clean,
    X_val, y_val,
    epsilon_values: list[float],
    out_dir: Path,
    seed: int = 42,
):
    """
    For each epsilon value, inject uniform noise into y_U_clean, train each
    model in each mode, and record macro F1 on the validation set.
    Save results CSV, F1-vs-epsilon plot, SVM support vector plot, and
    decision tree depth plot.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    clf_names = ["GNB", "LR", "kNN", "DT", "SVM"]
    rows = []
    svm_sv_records = []
    dt_records = []

    total_runs = len(epsilon_values) * len(clf_names) * len(MODES_TRAIN)
    run_count = 0

    for eps in epsilon_values:
        y_U_noisy = inject_uniform_noise(y_U_clean, eps, seed=seed)

        for clf_name in clf_names:
            for mode in MODES_TRAIN:
                run_count += 1
                label = f"{clf_name}-{mode}"
                print(f"  [{run_count}/{total_runs}] ε={eps:.2f}  {label} ...", end=" ", flush=True)

                clf = _make_clf(clf_name, mode)
                try:
                    clf.fit(X_L, y_L, X_U, y_U_noisy)
                    results = evaluate_model(clf, X_val, y_val)
                    macro_f1 = results["macro_f1"]
                    roc_auc = results["roc_auc"]
                    pr_auc = results["pr_auc"]
                except Exception as e:
                    print(f"FAILED ({e})")
                    macro_f1 = float("nan")
                    roc_auc = float("nan")
                    pr_auc = float("nan")

                rows.append({
                    "epsilon": eps,
                    "classifier": clf_name,
                    "mode": mode,
                    "label": label,
                    "macro_f1": macro_f1,
                    "roc_auc": roc_auc,
                    "pr_auc": pr_auc,
                })

                if clf_name == "SVM" and getattr(clf, "n_support_vectors_", None) is not None:
                    svm_sv_records.append({
                        "epsilon": eps,
                        "mode": mode,
                        "n_support_vectors": clf.n_support_vectors_,
                    })

                if clf_name == "DT" and getattr(clf, "tree_depth_", None) is not None:
                    dt_records.append({
                        "epsilon": eps,
                        "mode": mode,
                        "max_depth_param": "unpruned",
                        "tree_depth": clf.tree_depth_,
                        "n_leaves": clf.n_leaves_,
                    })

                print(f"F1={macro_f1:.4f}")

    # Pruned DT (max_depth=5) comparison
    print("\n── Pruned Decision Tree (max_depth=5) analysis ──")
    for eps in epsilon_values:
        y_U_noisy = inject_uniform_noise(y_U_clean, eps, seed=seed)
        for mode in MODES_TRAIN:
            label = f"DT(d=5)-{mode}"
            print(f"  ε={eps:.2f}  {label} ...", end=" ", flush=True)
            clf = DecisionTreeModel(mode=mode, max_depth=5)
            try:
                clf.fit(X_L, y_L, X_U, y_U_noisy)
                dt_records.append({
                    "epsilon": eps,
                    "mode": mode,
                    "max_depth_param": "pruned(d=5)",
                    "tree_depth": clf.tree_depth_,
                    "n_leaves": clf.n_leaves_,
                })
                print(f"depth={clf.tree_depth_}, leaves={clf.n_leaves_}")
            except Exception as e:
                print(f"FAILED ({e})")

    df = pd.DataFrame(rows)
    csv_path = out_dir / "noise_breakdown.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n[WP2] Saved results to {csv_path}")

    _plot_f1_vs_epsilon(df, out_dir)
    if svm_sv_records:
        _plot_svm_support_vectors(svm_sv_records, out_dir)
    if dt_records:
        _plot_tree_depth(dt_records, out_dir)

    return df


# ── Experiment 2: All 3 Noise Types Comparison (Synthetic) ───────────────

def run_noise_type_comparison(
    X_L, y_L,
    X_U, y_U_clean,
    X_val, y_val,
    out_dir: Path,
    seed: int = 42,
):
    """
    Compare Uniform, Asymmetric (pair confusion 0↔1, 2↔3), and Boundary-Dependent
    (Proposal Eq. 3.1) label noise across all 5 classifiers (naive_pool + gold_only
    floor + self_training).
    """
    out_dir = Path(out_dir)
    clf_names = ["GNB", "LR", "kNN", "DT", "SVM"]

    schedules = [
        ("uniform",    [0.0, 0.15, 0.30, 0.45, 0.60]),
        ("asymmetric", [0.0, 0.15, 0.30, 0.45, 0.60]),
        ("boundary",   [0.0, 0.25, 0.50, 0.75, 1.00]),
    ]

    rows = []
    print("\n[WP2] Running 3-Noise-Type Comparison (Uniform vs. Asymmetric vs. Boundary) ...")

    # Fit gold_only and self_training baselines once (invariant to y_U_noisy)
    baseline_cache = {}
    for clf_name in clf_names:
        for mode in ("gold_only", "self_training"):
            clf = _make_clf(clf_name, mode)
            clf.fit(X_L, y_L, X_U, None)
            baseline_cache[(clf_name, mode)] = evaluate_model(clf, X_val, y_val)

    for noise_type, params in schedules:
        for param in params:
            if noise_type == "uniform":
                y_U_noisy = inject_uniform_noise(y_U_clean, param, seed=seed)
            elif noise_type == "asymmetric":
                T = _make_pair_confusion_T(param)
                y_U_noisy = inject_asymmetric_noise(y_U_clean, T=T, seed=seed)
            else:
                y_U_noisy = inject_boundary_noise(
                    y_U_clean, X_U, epsilon_max=param, gamma=2.0, seed=seed
                )

            actual_flip = float((y_U_noisy != y_U_clean).mean())
            print(f"  {noise_type:10s} param={param:.2f} (actual flip={actual_flip:.1%})")

            for clf_name in clf_names:
                # naive_pool depends on y_U_noisy
                clf = _make_clf(clf_name, "naive_pool")
                clf.fit(X_L, y_L, X_U, y_U_noisy)
                res_np = evaluate_model(clf, X_val, y_val)

                for mode, res in [
                    ("naive_pool", res_np),
                    ("gold_only", baseline_cache[(clf_name, "gold_only")]),
                    ("self_training", baseline_cache[(clf_name, "self_training")]),
                ]:
                    rows.append({
                        "noise_type": noise_type,
                        "severity_param": param,
                        "actual_flip_rate": round(actual_flip, 4),
                        "classifier": clf_name,
                        "mode": mode,
                        "macro_f1": res["macro_f1"],
                        "roc_auc": res["roc_auc"],
                        "pr_auc": res["pr_auc"],
                    })

    df = pd.DataFrame(rows)
    csv_path = out_dir / "noise_type_comparison.csv"
    df.to_csv(csv_path, index=False)
    print(f"[WP2] Saved 3-noise comparison to {csv_path}")

    _plot_noise_types_comparison(df, out_dir)
    return df


# ── Experiment 3: Real PTB-XL 3-Mode Baselines across Gold Scarcity η ────

def run_ptbxl_baselines(
    X_L, y_L,
    X_U, y_U_noisy,
    X_val, y_val,
    X_test, y_test,
    eta_values: list[float],
    out_dir: Path,
    seed: int = 42,
):
    """
    Evaluate WP2's 5 supervised baselines in all 3 modes on real PTB-XL data
    across gold scarcity fractions η ∈ {0.02, 0.05, 0.10, 0.20, 0.50, 1.00},
    plus balanced LR/SVM variants for direct comparison with WP3–WP5.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    specs = [
        ("GNB",       None),
        ("LR",        None),
        ("LR (bal)",  "balanced"),
        ("kNN",       None),
        ("DT",        None),
        ("SVM",       None),
        ("SVM (bal)", "balanced"),
    ]

    rows = []
    print("\n[WP2] Running PTB-XL Supervised Baselines across gold scarcity η ...")

    for eta in eta_values:
        if eta >= 1.0:
            X_L_sub, y_L_sub = X_L, y_L
        else:
            X_L_sub, _, y_L_sub, _ = train_test_split(
                X_L, y_L, train_size=eta, stratify=y_L, random_state=seed
            )

        n_gold = len(y_L_sub)
        print(f"  η={eta:.2f} (n_gold={n_gold}, n_untrusted={len(y_U_noisy)})")

        for clf_label, cw in specs:
            base_name = clf_label.split(" ")[0]
            modes = MODES_TRAIN if cw is None else ["gold_only", "naive_pool"]

            for mode in modes:
                clf = _make_clf(base_name, mode, class_weight=cw)
                clf.fit(X_L_sub, y_L_sub, X_U, y_U_noisy)
                res_val  = evaluate_model(clf, X_val, y_val)
                res_test = evaluate_model(clf, X_test, y_test)
                print(
                    f"    {clf_label:9s} | {mode:13s} | "
                    f"val_F1={res_val['macro_f1']:.4f} | test_F1={res_test['macro_f1']:.4f}",
                    flush=True,
                )
                rows.append({
                    "eta": eta,
                    "n_gold": n_gold,
                    "classifier": clf_label,
                    "mode": mode,
                    "val_macro_f1": res_val["macro_f1"],
                    "val_roc_auc":  res_val["roc_auc"],
                    "val_pr_auc":   res_val["pr_auc"],
                    "test_macro_f1": res_test["macro_f1"],
                    "test_roc_auc":  res_test["roc_auc"],
                    "test_pr_auc":   res_test["pr_auc"],
                })

    df = pd.DataFrame(rows)
    csv_path = out_dir / "ptbxl_baselines.csv"
    df.to_csv(csv_path, index=False)
    print(f"[WP2] Saved PTB-XL baselines to {csv_path}")

    _plot_ptbxl_baselines(df, out_dir)
    return df


# ── Plotting functions ───────────────────────────────────────────────────

def _plot_f1_vs_epsilon(df: pd.DataFrame, out_dir: Path):
    """Main comparison plot: Macro F1 vs ε for each model/mode combination."""
    sns.set_theme(style="whitegrid", font_scale=1.1)
    fig, ax = plt.subplots(figsize=(12, 7))

    mode_styles = {
        "gold_only":     {"linestyle": "-",  "marker": "o"},
        "naive_pool":    {"linestyle": "--", "marker": "s"},
        "self_training": {"linestyle": ":",  "marker": "^"},
    }
    clf_colors = {
        "GNB": "#1f77b4",
        "LR":  "#ff7f0e",
        "kNN": "#2ca02c",
        "DT":  "#d62728",
        "SVM": "#9467bd",
    }

    for _, grp in df.groupby("label"):
        clf_name = grp["classifier"].iloc[0]
        mode = grp["mode"].iloc[0]
        ax.plot(
            grp["epsilon"], grp["macro_f1"],
            label=grp["label"].iloc[0],
            color=clf_colors.get(clf_name),
            linewidth=2, markersize=6,
            **mode_styles.get(mode, {}),
        )

    ax.set_xlabel("Noise Rate ε (uniform)", fontsize=13)
    ax.set_ylabel("Macro F1 (validation)", fontsize=13)
    ax.set_title("WP2 — Supervised Breakdown: Macro F1 vs. Noise Rate ε", fontsize=14, fontweight="bold")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8, ncol=1, frameon=True)
    ax.set_ylim(bottom=0)
    ax.set_xticks(df["epsilon"].unique())

    fig.tight_layout()
    path = out_dir / "f1_vs_epsilon.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[WP2] Saved {path}")


def _plot_svm_support_vectors(records: list[dict], out_dir: Path):
    """SVM support vector count vs. ε (shows margin corruption)."""
    sns.set_theme(style="whitegrid", font_scale=1.1)
    df_sv = pd.DataFrame(records)
    fig, ax = plt.subplots(figsize=(9, 6))

    mode_markers = {"gold_only": "o", "naive_pool": "s", "self_training": "^"}
    mode_styles = {"gold_only": "-", "naive_pool": "--", "self_training": ":"}

    for mode, grp in df_sv.groupby("mode"):
        grp_sorted = grp.sort_values("epsilon")
        ax.plot(
            grp_sorted["epsilon"], grp_sorted["n_support_vectors"],
            label=f"SVM-{mode}",
            marker=mode_markers.get(mode, "o"),
            linestyle=mode_styles.get(mode, "-"),
            linewidth=2, markersize=7,
        )

    ax.set_xlabel("Noise Rate ε", fontsize=13)
    ax.set_ylabel("Number of Support Vectors", fontsize=13)
    ax.set_title("WP2 — SVM Support Vector Inflation vs. Noise Rate", fontsize=14, fontweight="bold")
    ax.legend(fontsize=10)
    ax.set_xticks(df_sv["epsilon"].unique())

    fig.tight_layout()
    path = out_dir / "svm_support_vectors.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[WP2] Saved {path}")


def _plot_tree_depth(records: list[dict], out_dir: Path):
    """Decision tree depth and leaf count vs. ε for unpruned vs. pruned."""
    sns.set_theme(style="whitegrid", font_scale=1.1)
    df_dt = pd.DataFrame(records)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for col, ylabel, title, ax in [
        ("tree_depth", "Tree Depth", "Tree Depth vs. ε", axes[0]),
        ("n_leaves", "Number of Leaves", "Leaf Count vs. ε", axes[1]),
    ]:
        for (variant, mode), grp in df_dt.groupby(["max_depth_param", "mode"]):
            if mode == "naive_pool":
                g = grp.sort_values("epsilon")
                ax.plot(
                    g["epsilon"], g[col],
                    label=f"{variant} ({mode})",
                    marker="o" if "unpruned" in str(variant) else "s",
                    linestyle="-" if "unpruned" in str(variant) else "--",
                    linewidth=2, markersize=7,
                )
            elif mode == "gold_only" and variant == "unpruned":
                g = grp.sort_values("epsilon")
                ax.plot(
                    g["epsilon"], g[col],
                    label=f"{variant} ({mode})",
                    marker="^", linestyle="-.", linewidth=2, markersize=7, color="gray",
                )
        ax.set_xlabel("Noise Rate ε", fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.legend(fontsize=9)

    fig.suptitle("WP2 — Decision Tree Overfitting Analysis", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    path = out_dir / "tree_depth_vs_epsilon.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[WP2] Saved {path}")


def _plot_noise_types_comparison(df: pd.DataFrame, out_dir: Path):
    """Compare naive_pool Macro F1 across Uniform, Asymmetric, and Boundary noise."""
    sns.set_theme(style="whitegrid", font_scale=1.05)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    clf_colors = {"GNB": "#1f77b4", "LR": "#ff7f0e", "kNN": "#2ca02c", "DT": "#d62728", "SVM": "#9467bd"}
    titles = {
        "uniform":    "Uniform Random Flip",
        "asymmetric": "Asymmetric Pair Confusion (0↔1, 2↔3)",
        "boundary":   "Boundary-Dependent (Eq. 3.1, γ=2)",
    }

    df_np = df[df["mode"] == "naive_pool"]
    for ax, ntype in zip(axes, ["uniform", "asymmetric", "boundary"]):
        sub = df_np[df_np["noise_type"] == ntype]
        for clf_name, grp in sub.groupby("classifier"):
            g = grp.sort_values("actual_flip_rate")
            ax.plot(g["actual_flip_rate"] * 100, g["macro_f1"],
                    marker="o", linewidth=2, label=clf_name, color=clf_colors.get(clf_name))
        ax.set_title(titles[ntype], fontweight="bold")
        ax.set_xlabel("Actual % of Pool Labels Flipped")
        ax.set_ylim(0.30, 0.92)
        ax.grid(True, alpha=0.5)
    axes[0].set_ylabel("Validation Macro F1 (naive_pool)")
    axes[2].legend(loc="lower left", fontsize=9)
    fig.suptitle("WP2 — Supervised Breakdown Across All 3 Noise Mechanisms", fontsize=14, fontweight="bold")
    fig.tight_layout()
    path = out_dir / "noise_types_comparison.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[WP2] Saved {path}")


def _plot_ptbxl_baselines(df: pd.DataFrame, out_dir: Path):
    """Compare gold_only vs naive_pool vs self_training on real PTB-XL across η."""
    sns.set_theme(style="whitegrid", font_scale=1.05)
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), sharey=True)
    clf_colors = {
        "GNB": "#1f77b4", "LR": "#ff7f0e", "LR (bal)": "#d97706",
        "kNN": "#2ca02c", "DT": "#d62728", "SVM": "#9467bd", "SVM (bal)": "#6d28d9",
    }

    for ax, mode, title in [
        (axes[0], "gold_only",  "Gold Set Only (D_L)"),
        (axes[1], "naive_pool", "Naive Pool (D_L ∪ real noisy D_U)"),
    ]:
        sub = df[df["mode"] == mode]
        for clf_name, grp in sub.groupby("classifier"):
            g = grp.sort_values("eta")
            ls = "--" if "(bal)" in clf_name else "-"
            ax.plot(g["eta"] * 100, g["val_macro_f1"],
                    marker="o", linestyle=ls, linewidth=2,
                    label=clf_name, color=clf_colors.get(clf_name))
        ax.set_title(title, fontweight="bold")
        ax.set_xlabel("Gold Fraction η (%)")
        ax.set_xscale("log")
        ax.set_xticks([2, 5, 10, 20, 50, 100])
        ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    axes[0].set_ylabel("Validation Macro F1 (PTB-XL Fold 9)")
    axes[1].legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    fig.suptitle("WP2 — Real PTB-XL Supervised Baselines Across Gold Scarcity η", fontsize=14, fontweight="bold")
    fig.tight_layout()
    path = out_dir / "ptbxl_baselines.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[WP2] Saved {path}")


def _resolve_ptbxl_paths(args):
    root = Path(__file__).resolve().parents[1]
    feat = Path(args.features_path) if args.features_path else (root / "outputs" / "wp1" / "features.npz")
    lab  = Path(args.labels_path)   if args.labels_path   else (root / "outputs" / "wp1" / "labels.npz")
    if not feat.exists() or not lab.exists():
        print(f"ERROR: Could not find WP1 files: {feat}, {lab}")
        sys.exit(1)
    return feat, lab


def main():
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    epsilon_values = [float(e) for e in args.epsilon_values.split(",")]
    eta_values     = [float(e) for e in args.eta_values.split(",")]

    if args.mode in ("synthetic", "all"):
        X, y = generate_manifold(n_samples=3000, seed=args.seed)
        rng = np.random.default_rng(args.seed)
        idx = rng.permutation(len(y))
        n_train = int(0.70 * len(y))
        n_val   = int(0.15 * len(y))
        idx_tr, idx_val = idx[:n_train], idx[n_train:n_train + n_val]
        n_gold = int(0.20 * n_train)
        X_L, y_L       = X[idx_tr[:n_gold]], y[idx_tr[:n_gold]]
        X_U, y_U_clean = X[idx_tr[n_gold:]], y[idx_tr[n_gold:]]
        X_val, y_val   = X[idx_val], y[idx_val]

        print(f"[WP2] Mode: synthetic (Gold={len(y_L)}, Pool={len(y_U_clean)}, Val={len(y_val)})")
        run_breakdown_analysis(X_L, y_L, X_U, y_U_clean, X_val, y_val, epsilon_values, out_dir, seed=args.seed)
        run_noise_type_comparison(X_L, y_L, X_U, y_U_clean, X_val, y_val, out_dir, seed=args.seed)

    if args.mode in ("ptbxl", "all"):
        feat_path, lab_path = _resolve_ptbxl_paths(args)
        split = load_standard_split(feat_path, lab_path, None)
        print(f"[WP2] Mode: ptbxl (Gold={len(split['y_train_L'])}, Pool={len(split['y_train_U'])}, "
              f"Val={len(split['y_val'])}, Test={len(split['y_test'])})")
        run_ptbxl_baselines(
            split["X_train_L"], split["y_train_L"],
            split["X_train_U"], split["y_train_U"],
            split["X_val"],     split["y_val"],
            split["X_test"],    split["y_test"],
            eta_values, out_dir, seed=args.seed,
        )

    print(f"\n[WP2] Done. Outputs in {out_dir}")


if __name__ == "__main__":
    main()
