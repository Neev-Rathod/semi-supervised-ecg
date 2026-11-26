"""
presentation/generate_wp2_figures.py
====================================
Generates high-clarity, editorial-style WP2 presentation figures in
presentation/figures/ matching the Typst palette in project_presentation.typ.
Uses exact saved WP2 outputs (noise_breakdown.csv, noise_type_comparison.csv,
ptbxl_baselines.csv) and exact synthetic counts.
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from wp2_synthetic_baselines.synthetic_generator import generate_manifold, inject_uniform_noise
from wp2_synthetic_baselines.baselines import SVMModel, DecisionTreeModel

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
WP2_OUT = ROOT / "outputs" / "wp2"
FIG_DIR = Path(__file__).resolve().parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


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
        "font.size": 10.2,
        "axes.titlesize": 11.8,
        "axes.titleweight": "bold",
        "axes.labelsize": 10.2,
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


# ── Figure 1: Why Synthetic Lab + How 5 Baselines Map to WP3/4/5 ────────────
def make_fig1_synthetic_design():
    set_editorial_style()
    fig, ax = plt.subplots(figsize=(13.6, 5.0))
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 44)
    ax.axis("off")

    ax.text(0.5, 42.2, "WP2 Design: Controlled Causal Lab & Direct Links to WP3–WP5",
            fontsize=14, fontweight="bold", color=INK)
    ax.text(0.5, 39.3, "Why we built a synthetic manifold when PTB-XL lacks ground truth for D_U — and why these 5 classifiers matter",
            fontsize=10.1, color=INK_SOFT)

    def card(x, y, w, h, fc, ec, title, subtitle="", title_col=INK, title_gap=3.3):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.35,rounding_size=0.8",
                             facecolor=fc, edgecolor=ec, linewidth=1.35)
        ax.add_patch(box)
        ax.text(x + 1.1, y + h - 1.3, title, fontsize=9.8, fontweight="bold", color=title_col, va="top")
        if subtitle:
            ax.text(x + 1.1, y + h - 1.3 - title_gap, subtitle, fontsize=8.35, color=INK_SOFT, va="top", linespacing=1.42)

    # Left Card: Synthetic 50-D Generator & Split
    card(0.6, 17.5, 45.0, 18.8, "#ffffff", COBALT,
         "1 · CONTROLLED 50-D MANIFOLD (3,000 PTS, 5 CLASSES)",
         "• 10 informative (true class signal) + 5 redundant (correlated) + 35 noise dims\n"
         "• Orthogonal QR rotation + N(0, 0.1²) jitter → signal mixed across all 50 dims\n"
         "• Clean Anchor D_L: 420 (20% train)  |  Corrupted Pool D_U: 1,680 (80% train)\n"
         "• Clean Val (450) & Test (450) — noise injected ONLY into D_U!",
         title_col=COBALT, title_gap=3.2)

    # Bottom Left: 3 Noise Injectors
    card(0.6, 2.5, 45.0, 12.6, VERMILION_BG, VERMILION,
         "2 · THREE NOISE MECHANISMS + THREE TRAINING MODES",
         "• Noise types: (1) Uniform random flips, (2) Asymmetric pairs (0↔1, 2↔3),\n"
         "  (3) Boundary-dependent Eq. 3.1: P(flip) = ε_max · exp(−γ · margin)\n"
         "• Modes: gold_only (floor) · naive_pool (trust ỹ_U) · self_training (drop ỹ_U)",
         title_col=VERMILION, title_gap=3.2)

    # Arrow connecting left to right
    ax.annotate("", xy=(49.5, 20.0), xytext=(46.2, 20.0),
                arrowprops=dict(arrowstyle="->", color=INK, lw=2.2))

    # Right Card: 5 Classifiers -> WP3/4/5 Mapping
    card(50.0, 2.5, 49.4, 33.8, "#ffffff", INK,
         "3 · WHY THESE 5 CLASSIFIERS? (EACH MAPS TO WP3–WP5)",
         "", title_col=INK, title_gap=3.2)

    rows = [
        ("Gaussian NB", "Generative density", "WP5 (EM)", "Averages out uniform flips (−6.3%), but breaks on real D_U shift", FOREST, FOREST_BG),
        ("Logistic Reg.", "Linear discriminative", "WP5 & WP3", "Literally the classifier inside EM; strong balanced PTB-XL floor", COBALT, COBALT_BG),
        ("7-NN (kNN)", "Local neighborhood", "WP3 (Graph LP)", "Collapses −27.2% under noise → proves WP3 must discard ỹ_U", VERMILION, VERMILION_BG),
        ("Decision Tree", "Unpruned vs d=5", "WP4 (Co-Train)", "Explodes to 641 leaves (−38.5%) → justifies shallow depth-4 trees", AMBER, PAPER_ALT),
        ("RBF-SVM", "Max-margin", "WP4 (TSVM)", "SVs bloat to 96% of training data → foreshadows TSVM SV growth", VIOLET, COBALT_BG),
    ]
    y0 = 28.0
    for name, fam, target, insight, col, bg in rows:
        sub = FancyBboxPatch((51.4, y0), 46.6, 4.9, boxstyle="round,pad=0.2,rounding_size=0.5",
                             facecolor=bg, edgecolor=col, linewidth=0.9)
        ax.add_patch(sub)
        ax.text(52.2, y0 + 3.4, f"{name}  [{fam}]  →  {target}", fontsize=8.8, fontweight="bold", color=col)
        ax.text(52.2, y0 + 1.1, insight, fontsize=8.2, color=INK_SOFT)
        y0 -= 6.1

    out = FIG_DIR / "wp2_fig1_synthetic_design.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)
    print(f"Saved {out}")


# ── Figure 2: 1×5 Small Multiples — Uniform Noise Breakdown ─────────────────
def make_fig2_uniform_small_multiples():
    set_editorial_style()
    df = pd.read_csv(WP2_OUT / "noise_breakdown.csv")

    # Ordered from most noise-tolerant (GNB) to most catastrophic (DT)
    clf_order = [
        ("GNB", "Gaussian NB\n(Generative: −6.3%)"),
        ("SVM", "RBF-SVM\n(Margin: −7.4%)"),
        ("LR",  "Logistic Reg.\n(Linear: −19.8%)"),
        ("kNN", "7-NN\n(Local: −27.1%)"),
        ("DT",  "Decision Tree\n(Unpruned: −38.5%)"),
    ]

    fig, axes = plt.subplots(1, 5, figsize=(14.4, 4.3), sharey=True)
    fig.patch.set_facecolor(PAPER)

    for idx, (ax, (clf, title)) in enumerate(zip(axes, clf_order)):
        sub = df[df["classifier"] == clf]
        g_gold = sub[sub["mode"] == "gold_only"].sort_values("epsilon")
        g_naiv = sub[sub["mode"] == "naive_pool"].sort_values("epsilon")
        g_self = sub[sub["mode"] == "self_training"].sort_values("epsilon")

        ax.plot(g_gold["epsilon"] * 100, g_gold["macro_f1"],
                color=COBALT, lw=2.2, marker="o", ms=5, label="gold_only (floor)")
        ax.plot(g_naiv["epsilon"] * 100, g_naiv["macro_f1"],
                color=VERMILION, lw=2.4, ls="--", marker="s", ms=5.5, label="naive_pool (uses ỹ_U)")
        ax.plot(g_self["epsilon"] * 100, g_self["macro_f1"],
                color=FOREST, lw=2.0, ls=":", marker="^", ms=5, label="self_training (ignores ỹ_U)")

        # Shade region where naive_pool falls below gold_only (harmful noise zone!)
        eps_vals = g_gold["epsilon"].values * 100
        f_g = g_gold["macro_f1"].values
        f_n = g_naiv["macro_f1"].values
        ax.fill_between(eps_vals, f_n, f_g, where=(f_n < f_g), color=VERMILION_BG, alpha=0.85, interpolate=True)
        ax.fill_between(eps_vals, f_g, f_n, where=(f_n >= f_g), color=COBALT_BG, alpha=0.55, interpolate=True)

        # Annotate endpoints
        ax.text(2, f_n[0] + 0.018, f"{f_n[0]:.2f}", fontsize=8.0, fontweight="bold", color=VERMILION)
        ax.text(58, f_n[-1] - 0.038 if clf != "DT" else f_n[-1] + 0.02,
                f"{f_n[-1]:.2f}", fontsize=8.0, fontweight="bold", color=VERMILION, ha="right")

        if clf == "GNB":
            ax.text(30, 0.525, "Self-train hurts\n(−8.3 pp!)", fontsize=7.7, color=FOREST,
                    ha="center", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.18", fc=FOREST_BG, ec=FOREST, lw=0.6))

        _clean_spines(ax)
        ax.set_title(title, fontsize=10.2, fontweight="bold", pad=8)
        ax.set_xticks([0, 15, 30, 45, 60])
        ax.set_xticklabels(["0", "15", "30", "45", "60"], fontsize=8.8)
        ax.set_xlabel("Noise ε (%)", fontsize=9.4)
        ax.set_ylim(0.30, 0.94)
        ax.grid(True, alpha=0.45)

    axes[0].set_ylabel("Validation Macro F1 (Synthetic)", fontsize=10.2)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.03),
               ncol=3, fontsize=9.5, frameon=True)
    fig.suptitle("WP2 — Uniform Label Noise Breakdown (Clean Small-Multiples View vs. 15-Line Spaghetti)",
                 fontsize=13.0, fontweight="bold", y=1.10)

    fig.tight_layout(w_pad=0.9)
    out = FIG_DIR / "wp2_fig2_uniform_breakdown_small_multiples.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)
    print(f"Saved {out}")


# ── Figure 3: Failure Mechanics — SVM SV Bloat & Decision Tree Leaves ───────
def make_fig3_failure_mechanics():
    set_editorial_style()
    X, y = generate_manifold(3000, seed=42)
    rng = np.random.default_rng(42)
    idx = rng.permutation(len(y))
    n_tr = int(0.70 * len(y))
    n_g = int(0.20 * n_tr)
    X_L, y_L = X[idx[:n_g]], y[idx[:n_g]]
    X_U, y_U = X[idx[n_g:n_tr]], y[idx[n_g:n_tr]]

    eps_list = [0.0, 0.15, 0.30, 0.45, 0.60]
    sv_gold, sv_naive = [], []
    dt_gold, dt_unpruned, dt_pruned = [], [], []

    for eps in eps_list:
        yn = inject_uniform_noise(y_U, eps, seed=42)
        sv_gold.append(SVMModel("gold_only").fit(X_L, y_L, X_U, yn).n_support_vectors_)
        sv_naive.append(SVMModel("naive_pool").fit(X_L, y_L, X_U, yn).n_support_vectors_)
        dt_gold.append(DecisionTreeModel("gold_only").fit(X_L, y_L, X_U, yn).n_leaves_)
        dt_unpruned.append(DecisionTreeModel("naive_pool").fit(X_L, y_L, X_U, yn).n_leaves_)
        dt_pruned.append(DecisionTreeModel("naive_pool", max_depth=5).fit(X_L, y_L, X_U, yn).n_leaves_)

    eps_pct = [e * 100 for e in eps_list]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 4.8))
    fig.patch.set_facecolor(PAPER)

    # Panel A: SVM Support Vectors
    ax1.axhline(2100, color=INK_MUTED, ls=":", lw=1.2, label="Total training pool (2,100 pts)")
    ax1.plot(eps_pct, sv_naive, color=VERMILION, lw=2.4, marker="s", ms=6.5, label="SVM naive_pool")
    ax1.plot(eps_pct, sv_gold, color=COBALT, lw=2.1, ls="-", marker="o", ms=6, label="SVM gold_only (N=420)")
    for x, v in zip(eps_pct, sv_naive):
        pct_tr = 100 * v / 2100
        y_off = -195 if v >= 1900 else 55
        va_align = "top" if v >= 1900 else "bottom"
        ax1.text(x, v + y_off, f"{v:,}\n({pct_tr:.0f}%)", ha="center", va=va_align,
                 fontsize=8.2, fontweight="bold", color=VERMILION)
    ax1.text(30, 440, f"gold_only flat at {sv_gold[0]} SVs", fontsize=8.6, color=COBALT, fontweight="bold")
    _clean_spines(ax1)
    ax1.set_xticks(eps_pct)
    ax1.set_ylim(200, 2380)
    ax1.set_xlabel("Uniform Noise Rate ε (%)")
    ax1.set_ylabel("Number of Support Vectors")
    ax1.set_title("A. Hidden SVM Cost: 96% of Data Becomes Support Vectors", loc="left", pad=10)
    ax1.grid(True, alpha=0.45)
    ax1.legend(loc="center right", fontsize=8.6)

    # Panel B: DT Leaves (Unpruned vs Pruned)
    ax2.plot(eps_pct, dt_unpruned, color=VERMILION, lw=2.4, marker="s", ms=6.5, label="Unpruned DT (naive_pool)")
    ax2.plot(eps_pct, dt_gold, color=INK_MUTED, lw=2.0, ls="-.", marker="^", ms=6, label="Unpruned DT (gold_only)")
    ax2.plot(eps_pct, dt_pruned, color=FOREST, lw=2.3, ls="--", marker="o", ms=6, label="Pruned DT max_depth=5 (naive_pool)")
    for x, v in zip(eps_pct, dt_unpruned):
        ax2.text(x, v + 18, f"{v}", ha="center", va="bottom", fontsize=8.4, fontweight="bold", color=VERMILION)
    ax2.text(30, 52, "Pruned locked at 32 leaves → motivates WP4 depth-4 trees",
             ha="center", fontsize=8.4, fontweight="bold", color=FOREST,
             bbox=dict(boxstyle="round,pad=0.22", fc=FOREST_BG, ec=FOREST, lw=0.7))

    _clean_spines(ax2)
    ax2.set_xticks(eps_pct)
    ax2.set_ylim(0, 720)
    ax2.set_xlabel("Uniform Noise Rate ε (%)")
    ax2.set_ylabel("Decision Tree Leaf Count")
    ax2.set_title("B. Tree Memorization: Unpruned Leaves Double (348 → 641)", loc="left", pad=10)
    ax2.grid(True, alpha=0.45)
    ax2.legend(loc="upper left", fontsize=8.5)

    fig.tight_layout(w_pad=2.2)
    out = FIG_DIR / "wp2_fig3_failure_mechanics.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)
    print(f"Saved {out}")


# ── Figure 4: Uniform vs. Asymmetric vs. Boundary-Dependent Noise ───────────
def make_fig4_three_noise_types():
    set_editorial_style()
    df = pd.read_csv(WP2_OUT / "noise_type_comparison.csv")
    df_np = df[df["mode"] == "naive_pool"]

    fig, axes = plt.subplots(1, 3, figsize=(13.6, 4.8), sharey=True)
    fig.patch.set_facecolor(PAPER)

    cols = {"GNB": FOREST, "LR": COBALT, "kNN": AMBER, "DT": VERMILION, "SVM": VIOLET}
    panels = [
        ("uniform",    "A. Uniform Random Flip\n(Spread across all 4 wrong classes)"),
        ("asymmetric", "B. Asymmetric Pair Confusion (0↔1, 2↔3)\n(Structured errors outvote truth!)"),
        ("boundary",   "C. Boundary-Dependent (Eq. 3.1, γ=2)\n(Flips concentrated on margins)"),
    ]

    for ax, (ntype, title) in zip(axes, panels):
        sub = df_np[df_np["noise_type"] == ntype]
        for clf_name in ["SVM", "kNN", "LR", "GNB", "DT"]:
            g = sub[sub["classifier"] == clf_name].sort_values("actual_flip_rate")
            ax.plot(g["actual_flip_rate"] * 100, g["macro_f1"],
                    marker="o", ms=5.5, lw=2.2, label=clf_name, color=cols[clf_name])
        _clean_spines(ax)
        ax.set_title(title, loc="left", fontsize=10.5, fontweight="bold", pad=10)
        ax.set_xlabel("Actual % of Pool Labels Flipped")
        ax.set_ylim(0.32, 0.92)
        ax.grid(True, alpha=0.45)

    axes[0].set_ylabel("Validation Macro F1 (naive_pool)")
    # Key callout in Panel B (Asymmetric cliff)
    axes[1].annotate("Structured collapse!\nSVM 0.88 → 0.53\nGNB 0.65 → 0.46",
                     xy=(48.5, 0.534), xytext=(17, 0.355),
                     fontsize=8.3, fontweight="bold", color=VERMILION,
                     bbox=dict(boxstyle="round,pad=0.25", fc=VERMILION_BG, ec=VERMILION, lw=0.8),
                     arrowprops=dict(arrowstyle="->", color=VERMILION, lw=1.2))
    # Key callout in Panel C (Boundary drops SVM below gold_only 0.813)
    axes[2].axhline(0.8133, color=VIOLET, ls=":", lw=1.2)
    axes[2].text(2, 0.824, "SVM gold_only floor (0.813)", fontsize=7.9, color=VIOLET, fontweight="bold")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.02),
               ncol=5, fontsize=9.3, frameon=True)
    fig.suptitle("WP2 — Structured Asymmetric Noise Breaks Every Model Far Worse Than Uniform Flips",
                 fontsize=12.8, fontweight="bold", y=1.09)

    fig.tight_layout(w_pad=1.4)
    out = FIG_DIR / "wp2_fig4_three_noise_types.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)
    print(f"Saved {out}")


# ── Figure 5: Real PTB-XL Supervised Baselines (Reality Check) ──────────────
def make_fig5_ptbxl_reality_check():
    set_editorial_style()
    df = pd.read_csv(WP2_OUT / "ptbxl_baselines.csv")

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(13.4, 4.9), gridspec_kw={"width_ratios": [1.02, 1.08]}
    )
    fig.patch.set_facecolor(PAPER)

    # Panel A: Dumbbell at extreme scarcity (η = 2%, 180 Gold records) — gold_only vs naive_pool
    sub2 = df[df["eta"] == 0.02]
    order = ["LR (bal)", "LR", "SVM", "SVM (bal)", "kNN", "DT", "GNB"]
    y = np.arange(len(order))[::-1]

    for yp, cname in zip(y, order):
        r = sub2[sub2["classifier"] == cname]
        fg = float(r[r["mode"] == "gold_only"]["val_macro_f1"].iloc[0])
        fn = float(r[r["mode"] == "naive_pool"]["val_macro_f1"].iloc[0])
        diff = (fn - fg) * 100
        col_line = FOREST if diff >= 0 else VERMILION
        ax1.plot([fg, fn], [yp, yp], color=col_line, lw=3.0, alpha=0.8, zorder=2)
        ax1.scatter(fg, yp, color=COBALT, s=90, zorder=4, label="gold_only (N=180)" if yp == y[0] else "")
        ax1.scatter(fn, yp, color=col_line, marker="s", s=85, zorder=4,
                    label="naive_pool (+3,968 noisy D_U)" if yp == y[0] else "")
        sign = "+" if diff >= 0 else ""
        mid = (fg + fn) / 2
        ax1.text(mid, yp + 0.21, f"{sign}{diff:.1f} pp", ha="center", va="bottom",
                 fontsize=8.3, fontweight="bold", color=col_line)

    _clean_spines(ax1)
    ax1.set_yticks(y)
    ax1.set_yticklabels(order, fontweight="bold")
    ax1.set_xlim(0.10, 0.50)
    ax1.set_ylim(-0.6, len(order) - 0.15)
    ax1.set_xlabel("PTB-XL Fold-9 Validation Macro F1 (at η = 2%, N_L = 180)")
    ax1.set_title("A. Real PTB-XL at η=2%: Pooling Helps LR/SVM, Breaks GNB", loc="left", pad=42)
    ax1.grid(axis="x", alpha=0.45)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=2, fontsize=8.3)

    # Panel B: Full η trajectory on PTB-XL (gold_only vs naive_pool for key models)
    curves = [
        ("LR (bal)", "gold_only",  COBALT,    "-",  "o", "LR (bal) gold"),
        ("LR (bal)", "naive_pool", COBALT,    "--", "s", "LR (bal) naive"),
        ("SVM",      "naive_pool", VIOLET,    "--", "s", "SVM naive"),
        ("kNN",      "naive_pool", AMBER,     "--", "s", "kNN naive"),
        ("GNB",      "gold_only",  FOREST,    "-",  "o", "GNB gold"),
        ("GNB",      "naive_pool", VERMILION, "--", "s", "GNB naive (−10 pp!)"),
    ]
    for cname, mode, col, ls, mk, lbl in curves:
        g = df[(df["classifier"] == cname) & (df["mode"] == mode)].sort_values("eta")
        ax2.plot(g["eta"] * 100, g["val_macro_f1"], color=col, ls=ls, marker=mk, ms=5.5, lw=2.1, label=lbl)

    _clean_spines(ax2)
    ax2.set_xscale("log")
    ax2.set_xticks([2, 5, 10, 20, 50, 100])
    ax2.set_xticklabels(["2%", "5%", "10%", "20%", "50%", "100%"])
    ax2.set_ylim(0.22, 0.52)
    ax2.set_xlabel("Gold Set Fraction η (% of 9,010 verified ECGs)")
    ax2.set_ylabel("PTB-XL Fold-9 Validation Macro F1")
    ax2.set_title("B. Supervised Floor Across η on Real PTB-XL", loc="left", pad=42)
    ax2.grid(True, alpha=0.45)
    ax2.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=3, fontsize=7.9, frameon=True)

    fig.tight_layout(w_pad=2.0)
    out = FIG_DIR / "wp2_fig5_ptbxl_reality_check.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)
    print(f"Saved {out}")


if __name__ == "__main__":
    make_fig1_synthetic_design()
    make_fig2_uniform_small_multiples()
    make_fig3_failure_mechanics()
    make_fig4_three_noise_types()
    make_fig5_ptbxl_reality_check()
    print("All WP2 presentation figures generated!")
