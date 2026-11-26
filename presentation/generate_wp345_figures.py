"""
presentation/generate_wp345_figures.py
======================================
Generates crisp, editorial-style WP3, WP4, and WP5 presentation figures in
presentation/figures/ matching the Typst palette in project_presentation.typ.
All quantitative plots read directly from exact saved CSVs in outputs/wp3,
outputs/wp4, and outputs/wp5.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ── Editorial Palette (matches project_presentation.typ) ────────────────────
PAPER        = "#f6f3ec"
PAPER_ALT    = "#ece7dc"
INK          = "#18181b"
INK_SOFT     = "#3f3f46"
INK_MUTED    = "#71717a"
RULE         = "#d4cfc2"
VERMILION    = "#b91c1c"
VERMILION_BG = "#f9eaea"
COBALT       = "#1d4ed8"
COBALT_BG    = "#eaf0fa"
FOREST       = "#166534"
FOREST_BG    = "#e9f4ec"
AMBER        = "#b45309"
VIOLET       = "#6d28d9"

ROOT = Path(__file__).resolve().parents[1]
WP3_OUT = ROOT / "outputs" / "wp3"
WP4_OUT = ROOT / "outputs" / "wp4"
WP5_OUT = ROOT / "outputs" / "wp5"
FIG_DIR = Path(__file__).resolve().parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

CLASSES = ["NORM", "MI", "STTC", "CD", "HYP"]


def set_editorial_style():
    plt.rcParams.update({
        "figure.facecolor": PAPER,
        "axes.facecolor": "#ffffff",
        "axes.edgecolor": RULE,
        "axes.linewidth": 0.9,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "text.color": INK,
        "xtick.color": INK_SOFT,
        "ytick.color": INK_SOFT,
        "font.family": "sans-serif",
        "font.sans-serif": ["Liberation Sans", "DejaVu Sans"],
        "font.size": 10.0,
        "axes.titlesize": 11.4,
        "axes.titleweight": "bold",
        "axes.labelsize": 10.0,
        "grid.color": RULE,
        "grid.linestyle": "--",
        "grid.linewidth": 0.6,
        "legend.frameon": True,
        "legend.facecolor": "#ffffff",
        "legend.edgecolor": RULE,
    })


def _clean_spines(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


# ═════════════════════════════════════════════════════════════════════════════
# WP3 FIGURES (Graph-Based Harmonic Label Propagation)
# ═════════════════════════════════════════════════════════════════════════════

def make_wp3_fig1_metric_and_k():
    """Distance x PCA interaction (Mahalanobis collapse at PCA=0) + k blurring."""
    set_editorial_style()
    df = pd.read_csv(WP3_OUT / "wp3_results_summary.csv")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.6, 5.0))
    fig.patch.set_facecolor(PAPER)
    plt.subplots_adjust(left=0.06, right=0.97, top=0.79, bottom=0.14, wspace=0.25)

    fig.text(0.03, 0.94, "WP3 Geometry Ablation (900 Fits): Why PCA = 5 & Small k = 3 Win",
             fontsize=13.8, fontweight="bold", color=INK)
    fig.text(0.03, 0.885, "Harmonic LP resolves WP1's Mahalanobis contradiction: scarce Gold sets cannot invert an 84 x 84 covariance matrix cleanly",
             fontsize=10.0, color=INK_SOFT)

    # Panel A: Distance x PCA (mean across k and eta)
    pca_vals = [0, 5, 10, 20, 40]
    pca_labels = ["Raw\n(84-D)", "PCA 5", "PCA 10", "PCA 20", "PCA 40"]
    xpos = np.arange(len(pca_vals))

    styles = [
        ("euclidean",   "Euclidean",   COBALT,    "o-",  2.6),
        ("cosine",      "Cosine",      AMBER,     "s--", 2.1),
        ("mahalanobis", "Mahalanobis", VERMILION, "^-",  2.4),
    ]
    piv = df.groupby(["distance", "n_pca"])["macro_f1"].mean().unstack()
    for dist, label, col, fmt, lw in styles:
        vals = [piv.loc[dist, p] for p in pca_vals]
        ax1.plot(xpos, vals, fmt, color=col, lw=lw, markersize=6.8, label=label)

    # Annotate key points cleanly
    e5 = piv.loc["euclidean", 5]
    m0 = piv.loc["mahalanobis", 0]
    m5 = piv.loc["mahalanobis", 5]
    ax1.annotate(f"Peak mean: {e5:.3f}\n(Euclidean, PCA=5)",
                 xy=(1, e5), xytext=(1.55, e5 + 0.014),
                 fontsize=8.7, fontweight="bold", color=COBALT,
                 arrowprops=dict(arrowstyle="->", color=COBALT, lw=1.2))
    ax1.annotate(f"Collapsed at 84-D: {m0:.3f}\n(noisy Sigma_L^-1)",
                 xy=(0, m0), xytext=(0.45, m0 + 0.012),
                 fontsize=8.7, fontweight="bold", color=VERMILION,
                 arrowprops=dict(arrowstyle="->", color=VERMILION, lw=1.2))
    ax1.annotate(f"Recovers at 5-D\n({m5:.3f})",
                 xy=(1, m5), xytext=(1.55, m5 - 0.048),
                 fontsize=8.5, color=VERMILION,
                 arrowprops=dict(arrowstyle="->", color=VERMILION, lw=1.1))

    ax1.set_xticks(xpos)
    ax1.set_xticklabels(pca_labels)
    ax1.set_ylim(0.195, 0.325)
    ax1.set_ylabel("Mean Val Macro F1 (across k and eta)")
    ax1.set_title("A. Metric x Dimensionality Tradeoff", loc="left", pad=10)
    ax1.grid(True, alpha=0.55)
    ax1.legend(loc="upper right", fontsize=9.0)
    _clean_spines(ax1)

    # Panel B: Effect of k across eta for Euclidean (PCA=5 vs mean over PCA)
    k_vals = [3, 5, 10, 20]
    sub_euc = df[df["distance"] == "euclidean"]
    mean_by_k = [sub_euc[sub_euc["k"] == k]["macro_f1"].mean() for k in k_vals]
    pca5_by_k = [sub_euc[(sub_euc["k"] == k) & (sub_euc["n_pca"] == 5)]["macro_f1"].mean() for k in k_vals]

    w = 0.34
    kx = np.arange(len(k_vals))
    b1 = ax2.bar(kx - w/2, pca5_by_k, width=w, color=COBALT, label="Euclidean, PCA = 5")
    b2 = ax2.bar(kx + w/2, mean_by_k, width=w, color="#93c5fd", edgecolor=COBALT, linewidth=0.8, label="Euclidean, All PCA Avg")

    for rect, v in zip(b1, pca5_by_k):
        ax2.text(rect.get_x() + rect.get_width()/2, v + 0.004, f"{v:.3f}",
                 ha="center", va="bottom", fontsize=8.6, fontweight="bold", color=COBALT)
    for rect, v in zip(b2, mean_by_k):
        ax2.text(rect.get_x() + rect.get_width()/2, v + 0.004, f"{v:.3f}",
                 ha="center", va="bottom", fontsize=8.5, color=INK_SOFT)

    ax2.text(0.97, 0.80, "Larger k connects dissimilar ECGs\nand washes out rare MI / STTC / HYP\n(-0.054 drop from k=3 to k=20)",
             transform=ax2.transAxes, ha="right", fontsize=8.6, color=INK_SOFT,
             bbox=dict(boxstyle="round,pad=0.35", facecolor=PAPER_ALT, edgecolor=RULE))

    ax2.set_xticks(kx)
    ax2.set_xticklabels([f"k = {k}" for k in k_vals])
    ax2.set_ylim(0.20, 0.355)
    ax2.set_ylabel("Mean Val Macro F1")
    ax2.set_title("B. Neighborhood Blurring as k Grows", loc="left", pad=10)
    ax2.grid(True, axis="y", alpha=0.55)
    ax2.legend(loc="lower left", fontsize=8.8)
    _clean_spines(ax2)

    out = FIG_DIR / "wp3_fig1_metric_and_k.png"
    fig.savefig(out, dpi=220, facecolor=PAPER, bbox_inches="tight")
    plt.close(fig)
    print("Saved", out)


def make_wp3_fig2_test_comparison():
    """Held-out Fold 10 Test: Graph LP vs Same-Space Gold kNN vs Supervised Baselines."""
    set_editorial_style()
    ctrl_t = pd.read_csv(WP3_OUT / "control_test.csv").sort_values("eta")
    base_t = pd.read_csv(WP3_OUT / "gold_baselines_test.csv")
    bm = base_t.groupby(["model", "eta"])["macro_f1"].mean().unstack()

    etas = ctrl_t["eta"].values
    x = np.arange(len(etas))
    xlabels = [f"{int(e*100)}%\n({int(round(9010*e))})" for e in etas]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.6, 5.0), gridspec_kw={"width_ratios": [1.35, 1.0]})
    fig.patch.set_facecolor(PAPER)
    plt.subplots_adjust(left=0.06, right=0.97, top=0.79, bottom=0.15, wspace=0.25)

    fig.text(0.03, 0.94, "WP3 Held-Out Test (Fold 10): Graph LP vs. Supervised Baselines",
             fontsize=13.8, fontweight="bold", color=INK)
    fig.text(0.03, 0.885, "Adding 3,968 unlabeled nodes gives zero consistent edge over Gold-only kNN, while linear/SVM classifiers win cleanly",
             fontsize=10.0, color=INK_SOFT)

    # Panel A: Curves across eta
    series = [
        (bm.loc["SVM-RBF (balanced)"].values,  "SVM-RBF (bal, Gold-only)", FOREST,    "o-",  2.5),
        (bm.loc["LogReg (balanced)"].values,   "LogReg (bal, Gold-only)",  COBALT,    "s-",  2.3),
        (bm.loc["LogReg (unweighted)"].values, "LogReg (unweighted, Gold)", "#64748b", "d--", 1.9),
        (ctrl_t["knn_f1"].values,              "Gold-only kNN (PCA5, k=3)", AMBER,    "^:",  2.1),
        (ctrl_t["graph_f1"].values,            "Graph LP (PCA5, k=3)",      VERMILION,"o-",  2.7),
        (bm.loc["k-NN (k=5)"].values,          "5-NN (Raw 84-D, Gold)",     INK_MUTED, "v:",  1.6),
    ]
    for y, lbl, col, fmt, lw in series:
        ax1.plot(x, y, fmt, color=col, lw=lw, markersize=6.2, label=lbl)

    # Shaded gap between Balanced SVM and Graph LP
    ax1.fill_between(x, ctrl_t["graph_f1"].values, bm.loc["SVM-RBF (balanced)"].values,
                     color=VERMILION_BG, alpha=0.55)
    ax1.text(2.05, 0.372, "+0.09 to +0.13\nSupervised Gap",
             ha="center", fontsize=8.8, fontweight="bold", color=VERMILION,
             bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor=VERMILION, alpha=0.9))

    ax1.set_xticks(x)
    ax1.set_xticklabels(xlabels)
    ax1.set_xlabel("Labeled Fraction eta (N_L Gold Records)")
    ax1.set_ylabel("Fold-10 Test Macro F1 (3-seed mean)")
    ax1.set_ylim(0.19, 0.50)
    ax1.set_title("A. Test Macro F1 Across Scarcity Levels", loc="left", pad=10)
    ax1.grid(True, alpha=0.55)
    ax1.legend(loc="upper left", fontsize=8.3, ncol=2)
    _clean_spines(ax1)

    # Panel B: Paired gain of Graph LP vs identical-space Gold kNN (Control Val & Test)
    ctrl_v = pd.read_csv(WP3_OUT / "control_val.csv").sort_values("eta")
    w = 0.34
    b_val = ax2.bar(x - w/2, ctrl_v["gain"].values, width=w, color="#94a3b8", label="Val (Fold 9)")
    b_tst = ax2.bar(x + w/2, ctrl_t["gain"].values, width=w, color=VERMILION, label="Test (Fold 10)")
    ax2.axhline(0, color=INK, lw=1.1)

    for rect, v in zip(b_tst, ctrl_t["gain"].values):
        offset = 0.0025 if v >= 0 else -0.0030
        va = "bottom" if v >= 0 else "top"
        ax2.text(rect.get_x() + rect.get_width()/2, v + offset, f"{v:+.3f}",
                 ha="center", va=va, fontsize=8.2, fontweight="bold",
                 color=FOREST if v > 0 else VERMILION)

    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{int(e*100)}%" for e in etas])
    ax2.set_xlabel("Labeled Fraction eta")
    ax2.set_ylabel("Delta Macro F1 (Graph LP minus Gold kNN)")
    ax2.set_ylim(-0.058, 0.025)
    ax2.set_title("B. Same-Embedding Control (PCA=5, k=3)", loc="left", pad=10)
    ax2.grid(True, axis="y", alpha=0.55)
    ax2.legend(loc="lower right", fontsize=8.8)
    _clean_spines(ax2)

    out = FIG_DIR / "wp3_fig2_test_comparison.png"
    fig.savefig(out, dpi=220, facecolor=PAPER, bbox_inches="tight")
    plt.close(fig)
    print("Saved", out)


def make_wp3_fig3_class_collapse():
    """Per-class F1 breakdown at eta=10% explaining WHY pure neighbor diffusion fails."""
    set_editorial_style()
    raw = pd.read_csv(WP3_OUT / "wp3_results_raw.csv")
    bv = pd.read_csv(WP3_OUT / "gold_baselines.csv")

    lp10 = raw[(raw["distance"] == "euclidean") & (raw["n_pca"] == 5) &
               (raw["k"] == 3) & (raw["eta"] == 0.10)][[f"f1_{c}" for c in CLASSES]].mean()
    b10 = bv[bv["eta"] == 0.10].groupby("model")[[f"f1_{c}" for c in CLASSES]].mean()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.6, 4.9), gridspec_kw={"width_ratios": [1.55, 1.0]})
    fig.patch.set_facecolor(PAPER)
    plt.subplots_adjust(left=0.06, right=0.97, top=0.79, bottom=0.14, wspace=0.22)

    fig.text(0.03, 0.94, "Why Graph LP Fails on PTB-XL: Rare-Class Dilution in Overlapping Space",
             fontsize=13.8, fontweight="bold", color=INK)
    fig.text(0.03, 0.885, "Per-class Validation F1 at eta = 10% (N_L = 901 Gold records): even unweighted LogReg beats Graph LP on all 5 classes",
             fontsize=10.0, color=INK_SOFT)

    x = np.arange(len(CLASSES))
    w = 0.20
    bars_cfg = [
        ("Graph LP (PCA5, k=3)",   lp10.values,                             VERMILION),
        ("LogReg (unweighted)",    b10.loc["LogReg (unweighted)"].values,   "#64748b"),
        ("LogReg (balanced)",      b10.loc["LogReg (balanced)"].values,     COBALT),
        ("SVM-RBF (balanced)",     b10.loc["SVM-RBF (balanced)"].values,    FOREST),
    ]
    for i, (lbl, vals, col) in enumerate(bars_cfg):
        offset = (i - 1.5) * w
        rects = ax1.bar(x + offset, vals, width=w, color=col, label=lbl)
        if i in (0, 3):
            for r, v in zip(rects, vals):
                ax1.text(r.get_x() + r.get_width()/2, v + 0.012, f"{v:.2f}",
                         ha="center", va="bottom", fontsize=7.9, fontweight="bold", color=col)

    ax1.annotate("STTC & MI washed out\nby nearby NORM nodes\n(0.106 & 0.181 F1)",
                 xy=(2 - 1.5*w, lp10["f1_STTC"] + 0.05), xytext=(1.55, 0.56),
                 fontsize=8.6, fontweight="bold", color=VERMILION,
                 arrowprops=dict(arrowstyle="->", color=VERMILION, lw=1.2),
                 bbox=dict(boxstyle="round,pad=0.3", facecolor=VERMILION_BG, edgecolor=VERMILION))

    ax1.set_xticks(x)
    ax1.set_xticklabels(["NORM\n(~55%)", "MI\n(~15%)", "STTC\n(~15%)", "CD\n(~11%)", "HYP\n(~3%)"])
    ax1.set_ylabel("Validation Macro / Per-Class F1")
    ax1.set_ylim(0, 0.88)
    ax1.set_title("A. Per-Class F1 Comparison at eta = 10%", loc="left", pad=10)
    ax1.grid(True, axis="y", alpha=0.55)
    ax1.legend(loc="upper right", fontsize=8.4)
    _clean_spines(ax1)

    # Panel B: Synthesis Verdict Card connecting WP1 -> WP3 -> WP4/WP5
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)

    cards = [
        (7.15, 2.35, PAPER_ALT, RULE, INK,
         "1. Confirms WP1's Prediction",
         "5 ECG diseases overlap heavily (k-Means purity ~0.58).\nNeighbors frequently hold different class labels."),
        (3.85, 2.45, VERMILION_BG, VERMILION, VERMILION,
         "2. Why Harmonic Diffusion Struggles",
         "Graph LP assumes clean manifolds and discards y_tilde_U.\nMajority NORM (~55%) floods into STTC (0.106) and MI (0.181)."),
        (0.45, 2.55, COBALT_BG, COBALT, COBALT,
         "3. Direct Pivot to WP4 & WP5",
         "Approach 1 (pure geometry) is eliminated.\nNext: discriminative views/margins (WP4) & noise modeling (WP5)."),
    ]
    for y0, h, bg, ec, tc, title, body in cards:
        box = FancyBboxPatch((0.2, y0), 9.5, h, boxstyle="round,pad=0.16",
                             facecolor=bg, edgecolor=ec, linewidth=1.3)
        ax2.add_patch(box)
        ax2.text(0.55, y0 + h - 0.55, title, fontsize=10.3, fontweight="bold", color=tc)
        ax2.text(0.55, y0 + 0.35, body, fontsize=9.0, color=INK_SOFT, linespacing=1.35)

    out = FIG_DIR / "wp3_fig3_class_collapse.png"
    fig.savefig(out, dpi=220, facecolor=PAPER, bbox_inches="tight")
    plt.close(fig)
    print("Saved", out)


# ═════════════════════════════════════════════════════════════════════════════
# WP4 FIGURES (Multi-View Co-Training & Transductive SVM)
# ═════════════════════════════════════════════════════════════════════════════

def make_wp4_fig1_cotraining_curves():
    """Co-Training Val/Test curves vs 2-View Base & Full-84D Base + Gain bars."""
    set_editorial_style()
    co = pd.read_csv(WP4_OUT / "cotraining_eta_sweep.csv").sort_values("eta")
    etas = co["eta"].values
    x = np.arange(len(etas))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.6, 5.0), gridspec_kw={"width_ratios": [1.35, 1.0]})
    fig.patch.set_facecolor(PAPER)
    plt.subplots_adjust(left=0.06, right=0.97, top=0.79, bottom=0.15, wspace=0.26)

    fig.text(0.03, 0.94, "WP4 Dual-View Co-Training: Strong Gains Under Scarcity, Saturation at 50%",
             fontsize=13.8, fontweight="bold", color=INK)
    fig.text(0.03, 0.885, "HistGradientBoosting (depth=4, non-contradictory pseudo-labels >=0.72, w=0.35) shines when Gold <= 901 records",
             fontsize=10.0, color=INK_SOFT)

    ax1.plot(x, co["cotrain_macro_f1"],      "o-",  color=COBALT,    lw=2.7, ms=6.8, label="Co-Training (Val, View 1+2)")
    ax1.plot(x, co["test_cotrain_macro_f1"], "o--", color="#60a5fa", lw=2.0, ms=5.5, label="Co-Training (Held-out Test)")
    ax1.plot(x, co["base_2v_macro_f1"],      "s--", color=VERMILION, lw=2.1, ms=6.0, label="2-View Supervised Base (Val)")
    ax1.plot(x, co["base_full_macro_f1"],    "^-",  color=FOREST,    lw=2.1, ms=6.0, label="Full-84D Supervised Base (Val)")
    ax1.plot(x, co["base_v2_macro_f1"],      "d:",  color=AMBER,     lw=1.7, ms=5.2, label="View 2 Only (Val)")
    ax1.plot(x, co["base_v1_macro_f1"],      "v:",  color=INK_MUTED, lw=1.7, ms=5.2, label="View 1 Only (Val)")

    # Highlight scarce win region
    ax1.axvspan(-0.25, 2.2, color=COBALT_BG, alpha=0.45)
    ax1.text(1.0, 0.493, "Scarcity Sweet Spot (eta <= 10%)", ha="center",
             fontsize=8.8, fontweight="bold", color=COBALT)

    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{int(e*100)}%\n({int(g)})" for e, g in zip(etas, co["n_gold"])])
    ax1.set_xlabel("Labeled Fraction eta (N_L Gold Records)")
    ax1.set_ylabel("Macro F1")
    ax1.set_ylim(0.25, 0.535)
    ax1.set_title("A. Co-Training vs. Supervised Reference Curves", loc="left", pad=10)
    ax1.grid(True, alpha=0.55)
    ax1.legend(loc="lower right", fontsize=8.0, ncol=2)
    _clean_spines(ax1)

    # Panel B: Delta Macro F1 over 2-View Base and Full-84D Base
    w = 0.34
    g2v = co["f1_gain_over_2v"].values
    gfu = co["f1_gain_over_full"].values
    b1 = ax2.bar(x - 0.19, g2v, width=w, color=COBALT, label="vs. 2-View Base")
    b2 = ax2.bar(x + 0.19, gfu, width=w, color=[FOREST if v >= 0 else VERMILION for v in gfu], label="vs. Full-84D Base")
    ax2.axhline(0, color=INK, lw=1.1)

    for r, v in zip(b1, g2v):
        va = "bottom" if v >= 0 else "top"
        dy = 0.002 if v >= 0 else -0.0025
        ax2.text(r.get_x() + r.get_width()/2, v + dy, f"{v:+.3f}", ha="center", va=va,
                 fontsize=7.5, fontweight="bold", color=COBALT)
    for r, v in zip(b2, gfu):
        va = "bottom" if v >= 0 else "top"
        dy = 0.002 if v >= 0 else -0.0025
        ax2.text(r.get_x() + r.get_width()/2, v + dy, f"{v:+.3f}", ha="center", va=va,
                 fontsize=7.5, fontweight="bold", color=FOREST if v >= 0 else VERMILION)

    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{int(e*100)}%" for e in etas])
    ax2.set_xlabel("Labeled Fraction eta")
    ax2.set_ylabel("Macro F1 Gain (Val)")
    ax2.set_ylim(-0.062, 0.088)
    ax2.set_title("B. Co-Training Net Lift Across eta", loc="left", pad=10)
    ax2.grid(True, axis="y", alpha=0.55)
    ax2.legend(loc="upper right", fontsize=8.5)
    _clean_spines(ax2)

    out = FIG_DIR / "wp4_fig1_cotraining_curves.png"
    fig.savefig(out, dpi=220, facecolor=PAPER, bbox_inches="tight")
    plt.close(fig)
    print("Saved", out)


def make_wp4_fig2_cotraining_diagnostics():
    """Per-class F1 boost at eta=5% + Inter-view Agreement & View 2 Dominance."""
    set_editorial_style()
    co = pd.read_csv(WP4_OUT / "cotraining_eta_sweep.csv").sort_values("eta")
    row5 = co[co["eta"] == 0.05].iloc[0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.6, 4.9), gridspec_kw={"width_ratios": [1.25, 1.0]})
    fig.patch.set_facecolor(PAPER)
    plt.subplots_adjust(left=0.06, right=0.97, top=0.79, bottom=0.14, wspace=0.25)

    fig.text(0.03, 0.94, "Inside Co-Training: Where Gains Come From (eta = 5% & View Complementarity)",
             fontsize=13.8, fontweight="bold", color=INK)
    fig.text(0.03, 0.885, "Rare arrhythmias benefit most at eta = 5%, while ~22% cross-view disagreement keeps the two learners complementary",
             fontsize=10.0, color=INK_SOFT)

    # Panel A: Per-class F1 at eta=5% (CoTrain vs 2-View Base)
    x = np.arange(len(CLASSES))
    w = 0.34
    base_cls = [row5[f"base_f1_{c}"] for c in CLASSES]
    co_cls   = [row5[f"cotrain_f1_{c}"] for c in CLASSES]

    b1 = ax1.bar(x - w/2, base_cls, width=w, color="#94a3b8", label="2-View Base (eta=5%)")
    b2 = ax1.bar(x + w/2, co_cls,   width=w, color=COBALT,    label="Co-Training (eta=5%)")

    for i, (bv, cv) in enumerate(zip(base_cls, co_cls)):
        diff = cv - bv
        ax1.text(i + w/2, cv + 0.015, f"{cv:.2f}\n({diff:+.2f})",
                 ha="center", va="bottom", fontsize=8.1, fontweight="bold",
                 color=FOREST if diff > 0.02 else INK_SOFT)

    ax1.set_xticks(x)
    ax1.set_xticklabels(CLASSES)
    ax1.set_ylabel("Validation Per-Class F1 (eta = 5%)")
    ax1.set_ylim(0, 0.92)
    ax1.set_title("A. Per-Class Lift at eta = 5% (450 Gold Records)", loc="left", pad=10)
    ax1.grid(True, axis="y", alpha=0.55)
    ax1.legend(loc="upper right", fontsize=8.8)
    _clean_spines(ax1)

    # Panel B: View 1 vs View 2 + Final Agreement across eta
    ex = np.arange(len(co))
    ax2.plot(ex, co["base_v2_macro_f1"], "s-", color=AMBER,  lw=2.3, ms=6.2, label="View 2 (Freq/Wavelet)")
    ax2.plot(ex, co["base_v1_macro_f1"], "v-", color=VIOLET, lw=2.3, ms=6.2, label="View 1 (Time/Morph)")
    ax2.fill_between(ex, co["base_v1_macro_f1"], co["base_v2_macro_f1"], color="#fef3c7", alpha=0.6)

    ax2_twin = ax2.twinx()
    ax2_twin.plot(ex, co["cotrain_final_agreement"] * 100.0, "o--", color=INK_SOFT, lw=1.8, ms=5.5,
                  label="Cross-View Agreement (%)")
    ax2_twin.set_ylabel("Final Round View Agreement (%)", color=INK_SOFT)
    ax2_twin.set_ylim(55, 95)
    ax2_twin.spines["top"].set_visible(False)

    ax2.text(1.15, 0.472, "View 2 leads by +6 to +8 pp\n(wavelets catch local Q/T waves)",
             ha="center", fontsize=8.4, fontweight="bold", color=AMBER,
             bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor=AMBER))

    ax2.set_xticks(ex)
    ax2.set_xticklabels([f"{int(e*100)}%" for e in co["eta"]])
    ax2.set_xlabel("Labeled Fraction eta")
    ax2.set_ylabel("Single-View Macro F1")
    ax2.set_ylim(0.24, 0.52)
    ax2.set_title("B. View 2 Dominance & ~78% Agreement", loc="left", pad=10)
    ax2.grid(True, alpha=0.55)

    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="lower right", fontsize=8.0)
    ax2.spines["top"].set_visible(False)

    out = FIG_DIR / "wp4_fig2_cotraining_diagnostics.png"
    fig.savefig(out, dpi=220, facecolor=PAPER, bbox_inches="tight")
    plt.close(fig)
    print("Saved", out)


def make_wp4_fig3_tsvm_results():
    """TSVM vs Balanced RBF-SVM across eta + Support Vector inflation check."""
    set_editorial_style()
    ts = pd.read_csv(WP4_OUT / "tsvm_eta_sweep.csv").sort_values("eta")
    etas = ts["eta"].values
    x = np.arange(len(etas))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.6, 4.9), gridspec_kw={"width_ratios": [1.3, 1.0]})
    fig.patch.set_facecolor(PAPER)
    plt.subplots_adjust(left=0.06, right=0.97, top=0.79, bottom=0.14, wspace=0.25)

    fig.text(0.03, 0.94, "WP4 Transductive SVM: Steady Margin Lift + Support Vector Cost",
             fontsize=13.8, fontweight="bold", color=INK)
    fig.text(0.03, 0.885, "Keeping top 35% margin-confident pool records (1,389 / 3,968) with bounded C_U (0.05 -> 0.30) lifts RBF-SVM everywhere",
             fontsize=10.0, color=INK_SOFT)

    # Panel A: Val & Test Macro F1
    ax1.plot(x, ts["tsvm_macro_f1"],      "o-",  color=FOREST,    lw=2.6, ms=6.8, label="TSVM (Val)")
    ax1.plot(x, ts["test_tsvm_macro_f1"], "o--", color="#4ade80", lw=2.0, ms=5.5, label="TSVM (Held-out Test)")
    ax1.plot(x, ts["base_svm_macro_f1"],  "s--", color=INK_SOFT,  lw=2.1, ms=6.0, label="Base Bal RBF-SVM (Val)")

    for i in (2, 3):  # highlight eta=10%, 20%
        v = ts.iloc[i]["tsvm_macro_f1"]
        g = ts.iloc[i]["f1_gain_over_base"]
        ax1.annotate(f"+{g:.3f}\n({v:.3f})", xy=(i, v), xytext=(i - 0.15, v + 0.018),
                     ha="center", fontsize=8.4, fontweight="bold", color=FOREST,
                     arrowprops=dict(arrowstyle="->", color=FOREST, lw=1.1))

    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{int(e*100)}%\n({int(g)})" for e, g in zip(etas, ts["n_gold"])])
    ax1.set_xlabel("Labeled Fraction eta (N_L Gold Records)")
    ax1.set_ylabel("Macro F1")
    ax1.set_ylim(0.34, 0.54)
    ax1.set_title("A. TSVM Beats Balanced SVM at All eta (Peak +0.031)", loc="left", pad=10)
    ax1.grid(True, alpha=0.55)
    ax1.legend(loc="upper left", fontsize=8.7)
    _clean_spines(ax1)

    # Panel B: Support Vector Inflation (connects back to WP2 Slide 1/3 insight!)
    w = 0.34
    b1 = ax2.bar(x - w/2, ts["base_svm_total_sv"], width=w, color="#94a3b8", label="Base SVM SVs")
    b2 = ax2.bar(x + w/2, ts["tsvm_total_sv"],     width=w, color=AMBER,     label="TSVM Total SVs")

    for r, v in zip(b1, ts["base_svm_total_sv"]):
        ax2.text(r.get_x() + r.get_width()/2, v + 70, f"{int(v):,}", ha="center", va="bottom",
                 fontsize=7.6, color=INK_SOFT)
    for r, v in zip(b2, ts["tsvm_total_sv"]):
        ax2.text(r.get_x() + r.get_width()/2, v + 70, f"{int(v):,}", ha="center", va="bottom",
                 fontsize=7.8, fontweight="bold", color=AMBER)

    ax2.text(0.05, 0.72, "Adding pseudo-labeled margin points\nexplains SV growth (predicted by WP2)\n— C_U <= 0.30 keeps it bounded.",
             transform=ax2.transAxes, fontsize=8.4, color=INK_SOFT,
             bbox=dict(boxstyle="round,pad=0.3", facecolor=PAPER_ALT, edgecolor=RULE))

    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{int(e*100)}%" for e in etas])
    ax2.set_xlabel("Labeled Fraction eta")
    ax2.set_ylabel("Total Support Vectors")
    ax2.set_ylim(0, 5100)
    ax2.set_title("B. Support Vector Growth Across eta", loc="left", pad=10)
    ax2.grid(True, axis="y", alpha=0.55)
    ax2.legend(loc="upper left", fontsize=8.7)
    _clean_spines(ax2)

    out = FIG_DIR / "wp4_fig3_tsvm_results.png"
    fig.savefig(out, dpi=220, facecolor=PAPER, bbox_inches="tight")
    plt.close(fig)
    print("Saved", out)


# ═════════════════════════════════════════════════════════════════════════════
# WP5 FIGURES (Latent Noise Channel EM & Clinical Audit)
# ═════════════════════════════════════════════════════════════════════════════

def make_wp5_fig1_em_recovery():
    """EM Algorithm schematic + Synthetic Frobenius T-matrix recovery curve."""
    set_editorial_style()
    frob = pd.read_csv(WP5_OUT / "frobenius_recovery.csv").sort_values("n_pool")

    fig, (ax_sch, ax2) = plt.subplots(1, 2, figsize=(13.6, 4.9), gridspec_kw={"width_ratios": [1.15, 1.0]})
    fig.patch.set_facecolor(PAPER)
    plt.subplots_adjust(left=0.04, right=0.97, top=0.79, bottom=0.14, wspace=0.22)

    fig.text(0.03, 0.94, "WP5 LatentNoiseEM: Learning & Inverting the Hospital Confusion Channel T",
             fontsize=13.8, fontweight="bold", color=INK)
    fig.text(0.03, 0.885, "Instead of throwing away 3,968 machine labels (WP3/WP4), EM jointly learns classifier theta and confusion matrix T",
             fontsize=10.0, color=INK_SOFT)

    # Panel A: Clean EM Schematic
    ax_sch.set_facecolor(PAPER)
    ax_sch.set_xlim(0, 10)
    ax_sch.set_ylim(0, 10)
    ax_sch.axis("off")
    ax_sch.set_title("A. Anchored EM Loop (Seeded on Clean Gold Set)", loc="left", pad=8)

    boxes = [
        (0.3, 6.9, 9.3, 2.3, FOREST_BG, FOREST,
         "1. Anchor Initialization (Gold D_L)",
         "Fit balanced Logistic Regression theta^(0) strictly on clean D_L.\nAnchor T^(0) near identity using Dirichlet/Laplace prior alpha = 1.0."),
        (0.3, 3.7, 9.3, 2.3, COBALT_BG, COBALT,
         "2. E-Step: Posterior Class Probabilities on D_U",
         "Combine feature likelihood P(y=c | x_i; theta) with channel entry\nT_{c, y_tilde}:  gamma_{i,c}  propto  P(y=c | x_i; theta) * T_{c, y_tilde_i}"),
        (0.3, 0.5, 9.3, 2.3, VERMILION_BG, VERMILION,
         "3. M-Step: Refit Weighted Classifier + Update T",
         "Update T_{c,j} = (sum gamma_{i,c}[y_tilde=j] + alpha) /\n(sum gamma_{i,c} + K*alpha); refit theta on Gold + soft D_U."),
    ]
    for x0, y0, w, h, bg, ec, title, desc in boxes:
        ax_sch.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0.2",
                                        facecolor=bg, edgecolor=ec, linewidth=1.4))
        ax_sch.text(x0 + 0.32, y0 + h - 0.55, title, fontsize=10.0, fontweight="bold", color=ec)
        ax_sch.text(x0 + 0.32, y0 + 0.28, desc, fontsize=8.5, color=INK_SOFT, linespacing=1.28)

    ax_sch.annotate("", xy=(4.95, 6.1), xytext=(4.95, 6.8),
                    arrowprops=dict(arrowstyle="->", color=INK, lw=1.6))
    ax_sch.annotate("", xy=(4.95, 2.9), xytext=(4.95, 3.6),
                    arrowprops=dict(arrowstyle="->", color=INK, lw=1.6))

    # Panel B: Synthetic Frobenius recovery curve (from WP2 asymmetric generator)
    px = np.arange(len(frob))
    ax2.plot(px, frob["frobenius_error"], "o-", color=COBALT, lw=2.6, ms=7.0, label="||T_hat - T_true||_F")
    ax2.fill_between(px, 0, frob["frobenius_error"], color=COBALT_BG, alpha=0.55)

    for i, row in frob.iterrows():
        dy = 0.015 if i != 2 else 0.022
        ax2.text(i, row["frobenius_error"] + dy, f"{row['frobenius_error']:.3f}",
                 ha="center", va="bottom", fontsize=8.8, fontweight="bold", color=COBALT)

    ax2.text(0.45, 0.72, "Verified against WP2 ground truth:\n500 Gold + Asymmetric T_true\nError drops -63% by n_pool = 2,000",
             transform=ax2.transAxes, fontsize=8.6, color=INK_SOFT,
             bbox=dict(boxstyle="round,pad=0.32", facecolor="#ffffff", edgecolor=RULE))

    ax2.set_xticks(px)
    ax2.set_xticklabels([f"{int(n):,}" for n in frob["n_pool"]])
    ax2.set_xlabel("Untrusted Pool Size n_pool (Fixed 500 Gold)")
    ax2.set_ylabel("Frobenius Error ||T_hat - T_true||_F")
    ax2.set_ylim(0.05, 0.43)
    ax2.set_title("B. Synthetic T-Matrix Recovery Validation", loc="left", pad=10)
    ax2.grid(True, alpha=0.55)
    _clean_spines(ax2)

    out = FIG_DIR / "wp5_fig1_em_recovery.png"
    fig.savefig(out, dpi=220, facecolor=PAPER, bbox_inches="tight")
    plt.close(fig)
    print("Saved", out)


def make_wp5_fig2_discard_vs_correct():
    """Discard vs Correct across 20 (eta, epsilon) cells + honest note on WP4 upgrade."""
    set_editorial_style()
    df = pd.read_csv(WP5_OUT / "discard_vs_correct.csv")
    co_wp4 = pd.read_csv(WP4_OUT / "cotraining_eta_sweep.csv").sort_values("eta")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.6, 5.1), gridspec_kw={"width_ratios": [1.18, 1.0]})
    fig.patch.set_facecolor(PAPER)
    plt.subplots_adjust(left=0.06, right=0.97, top=0.79, bottom=0.16, wspace=0.28)

    fig.text(0.03, 0.94, "Q3 Verdict: Correcting y_tilde_U (EM) vs. Discarding It (Graph LP & Co-Train)",
             fontsize=13.8, fontweight="bold", color=INK)
    fig.text(0.03, 0.885, "EM wins all 20/20 (eta, eps) benchmark cells (0.411-0.462), leading strongest under severe scarcity (eta = 2%)",
             fontsize=10.0, color=INK_SOFT)

    # Panel A: Curves at eps=0 and eps=0.45 vs WP5 baselines + WP4 updated HistGBT CoTrain ref
    etas = sorted(df["eta"].unique())
    x = np.arange(len(etas))

    em0   = df[(df["method"] == "EM") & (df["epsilon"] == 0.0)].sort_values("eta")["macro_f1"].values
    em45  = df[(df["method"] == "EM") & (df["epsilon"] == 0.45)].sort_values("eta")["macro_f1"].values
    co0   = df[(df["method"] == "CoTrain") & (df["epsilon"] == 0.0)].sort_values("eta")["macro_f1"].values
    glp0  = df[(df["method"] == "GraphLP") & (df["epsilon"] == 0.0)].sort_values("eta")["macro_f1"].values
    co_up = co_wp4["cotrain_macro_f1"].values

    ax1.plot(x, em0,   "o-",  color=VERMILION, lw=2.7, ms=6.8, label="EM (Correct, eps = 0%)")
    ax1.plot(x, em45,  "o--", color="#ef4444", lw=2.1, ms=5.8, label="EM (Correct, +45% extra noise)")
    ax1.plot(x, co_up, "^:",  color=FOREST,    lw=2.1, ms=6.0, label="WP4 Co-Train (updated HistGBT ref)*")
    ax1.plot(x, co0,   "s--", color=AMBER,     lw=1.9, ms=5.5, label="Co-Train in WP5 grid (LogReg)")
    ax1.plot(x, glp0,  "d-.", color=COBALT,    lw=2.0, ms=5.8, label="Graph LP in WP5 grid")

    ax1.annotate("0.462 vs 0.365 (HistGBT)\nat 180 Gold records!",
                 xy=(0, em0[0]), xytext=(0.45, 0.488),
                 fontsize=8.5, fontweight="bold", color=VERMILION,
                 arrowprops=dict(arrowstyle="->", color=VERMILION, lw=1.2))

    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{int(e*100)}%" for e in etas])
    ax1.set_xlabel("Labeled Fraction eta")
    ax1.set_ylabel("Validation Macro F1")
    ax1.set_ylim(0.15, 0.525)
    ax1.set_title("A. Correct vs. Discard Across Gold Scarcity", loc="left", pad=10)
    ax1.grid(True, alpha=0.55)
    ax1.legend(loc="lower right", fontsize=7.9)
    _clean_spines(ax1)

    # Panel B: 5 x 4 Advantage Heatmap (EM minus best WP5 discard baseline in discard_vs_correct.csv)
    eps_vals = sorted(df["epsilon"].unique())
    piv_em = df[df["method"] == "EM"].pivot(index="eta", columns="epsilon", values="macro_f1")
    piv_co = df[df["method"] == "CoTrain"].pivot(index="eta", columns="epsilon", values="macro_f1")
    piv_gl = df[df["method"] == "GraphLP"].pivot(index="eta", columns="epsilon", values="macro_f1")
    best_discard = np.maximum(piv_co.values, piv_gl.values)
    adv = piv_em.values - best_discard  # shape (5, 4)

    im = ax2.imshow(adv, cmap="YlGn", aspect="auto", vmin=0.04, vmax=0.14)
    ax2.set_xticks(range(len(eps_vals)))
    ax2.set_xticklabels([f"+{int(ep*100)}%" for ep in eps_vals])
    ax2.set_yticks(range(len(etas)))
    ax2.set_yticklabels([f"{int(et*100)}%" for et in etas])
    ax2.set_xlabel("Extra Symmetric Corruption eps on D_U")
    ax2.set_ylabel("Labeled Fraction eta")
    ax2.set_title("B. EM Advantage Heatmap (WP5 Benchmark)", loc="left", pad=10)

    for i in range(len(etas)):
        for j in range(len(eps_vals)):
            v = adv[i, j]
            em_v = piv_em.values[i, j]
            tcol = "#ffffff" if v > 0.095 else INK
            ax2.text(j, i, f"+{v:.3f}\n({em_v:.3f})", ha="center", va="center",
                     fontsize=8.2, fontweight="bold", color=tcol)

    cbar = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    cbar.set_label("EM - Best WP5 Baseline (Macro F1)", fontsize=8.6)

    fig.text(0.03, 0.015,
             "*Transparency note: WP5's saved grid used WP4's initial LogReg CoTrainer (0.326-0.355). WP4 later upgraded CoTrainer to HistGBT (0.365-0.470), matching/beating EM only at eta=50%.",
             fontsize=8.1, color=INK_MUTED, style="italic")

    out = FIG_DIR / "wp5_fig2_discard_vs_correct.png"
    fig.savefig(out, dpi=220, facecolor=PAPER, bbox_inches="tight")
    plt.close(fig)
    print("Saved", out)


def make_wp5_fig3_clinical_audit():
    """Clinical Audit: 5x5 T_hat Heatmap + Top Systematic Hospital Software Biases."""
    set_editorial_style()
    t_df = pd.read_csv(WP5_OUT / "T_hat.csv", index_col=0)
    T = t_df.loc[CLASSES, CLASSES].values

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.6, 5.1), gridspec_kw={"width_ratios": [1.12, 1.0]})
    fig.patch.set_facecolor(PAPER)
    plt.subplots_adjust(left=0.07, right=0.97, top=0.79, bottom=0.14, wspace=0.30)

    fig.text(0.03, 0.94, "Q4 Clinical Audit: Learned Confusion Matrix T_hat Across 3,968 Hospital Records",
             fontsize=13.8, fontweight="bold", color=INK)
    fig.text(0.03, 0.885, "Converges in 39 EM iterations and solves WP1's opening mystery: software over-alarms MI by 9.4% on NORM & 9.2% on STTC",
             fontsize=10.0, color=INK_SOFT)

    # Panel A: 5x5 T_hat heatmap
    im = ax1.imshow(T, cmap="Blues", aspect="auto", vmin=0.0, vmax=1.0)
    ax1.set_xticks(range(5))
    ax1.set_xticklabels(CLASSES)
    ax1.set_yticks(range(5))
    ax1.set_yticklabels(CLASSES)
    ax1.set_xlabel("Observed Machine Label y_tilde")
    ax1.set_ylabel("Latent True Disease y")
    ax1.set_title("A. Estimated Channel Matrix T_hat (Row Sum = 1)", loc="left", pad=10)

    for r in range(5):
        for c in range(5):
            v = T[r, c]
            tcol = "#ffffff" if v > 0.45 else (VERMILION if (r != c and v >= 0.06) else INK)
            fw = "bold" if (r == c or v >= 0.06) else "normal"
            ax1.text(c, r, f"{v:.3f}", ha="center", va="center", fontsize=8.8, fontweight=fw, color=tcol)

    # Highlight the 2 biggest off-diagonal alarms
    for (r_idx, c_idx) in [(0, 1), (2, 1), (4, 0)]:
        ax1.add_patch(plt.Rectangle((c_idx - 0.48, r_idx - 0.48), 0.96, 0.96,
                                    fill=False, edgecolor=VERMILION, lw=2.0))

    cbar = fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
    cbar.set_label("P(y_tilde | y)", fontsize=8.8)

    # Panel B: Top off-diagonal biases + Diagonal trust bars
    off_pairs = [
        ("NORM -> MI", T[0, 1], VERMILION),
        ("STTC -> MI", T[2, 1], VERMILION),
        ("HYP -> NORM", T[4, 0], AMBER),
        ("HYP -> CD",   T[4, 3], AMBER),
        ("HYP -> MI",   T[4, 1], INK_MUTED),
        ("HYP -> STTC", T[4, 2], INK_MUTED),
    ]
    labels = [p[0] for p in off_pairs][::-1]
    vals   = [p[1] * 100.0 for p in off_pairs][::-1]
    cols   = [p[2] for p in off_pairs][::-1]
    yp = np.arange(len(labels))

    bars = ax2.barh(yp, vals, height=0.58, color=cols)
    for b, v, col in zip(bars, vals, cols):
        ax2.text(v + 0.25, b.get_y() + b.get_height()/2, f"{v:.2f}%",
                 va="center", ha="left", fontsize=9.0, fontweight="bold", color=col)

    ax2.text(0.51, 0.08,
             "Diagonal Trust Rate:\n"
             f"CD = {T[3,3]*100:.1f}%   MI = {T[1,1]*100:.1f}%\n"
             f"STTC = {T[2,2]*100:.1f}% NORM = {T[0,0]*100:.1f}%\n"
             f"HYP = {T[4,4]*100:.1f}% (weakest)",
             transform=ax2.transAxes, fontsize=8.4, color=INK_SOFT, linespacing=1.35,
             bbox=dict(boxstyle="round,pad=0.32", facecolor=PAPER_ALT, edgecolor=RULE))

    ax2.set_yticks(yp)
    ax2.set_yticklabels(labels)
    ax2.set_xlabel("Off-Diagonal Flip Probability (%)")
    ax2.set_xlim(0, 12.8)
    ax2.set_title("B. Top Hospital Software Misdiagnoses", loc="left", pad=10)
    ax2.grid(True, axis="x", alpha=0.55)
    _clean_spines(ax2)

    out = FIG_DIR / "wp5_fig3_clinical_audit.png"
    fig.savefig(out, dpi=220, facecolor=PAPER, bbox_inches="tight")
    plt.close(fig)
    print("Saved", out)


if __name__ == "__main__":
    make_wp3_fig1_metric_and_k()
    make_wp3_fig2_test_comparison()
    make_wp3_fig3_class_collapse()
    make_wp4_fig1_cotraining_curves()
    make_wp4_fig2_cotraining_diagnostics()
    make_wp4_fig3_tsvm_results()
    make_wp5_fig1_em_recovery()
    make_wp5_fig2_discard_vs_correct()
    make_wp5_fig3_clinical_audit()
    print("All WP3-WP5 figures generated cleanly.")
