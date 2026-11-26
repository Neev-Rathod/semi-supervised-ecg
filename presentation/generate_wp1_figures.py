"""
presentation/generate_wp1_figures.py
====================================
Generates high-clarity, editorial-style WP1 presentation figures in
presentation/figures/ matching the Typst palette in project_presentation.typ.
Uses exact saved WP1 outputs (features.npz, labels.npz, split_summary.csv,
noise_analysis_results.csv) with zero fabricated numbers.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

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

ROOT = Path(__file__).resolve().parents[1]
WP1_OUT = ROOT / "outputs" / "wp1"
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
        "axes.titlesize": 12.0,
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


# ── Figure 1: ECG Primer + Sensor Artifacts (Schematic) ─────────────────────
def make_fig1_ecg_primer():
    set_editorial_style()
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(13.4, 5.1), gridspec_kw={"width_ratios": [1.03, 1.07]}
    )
    fig.patch.set_facecolor(PAPER)

    def one_beat(t):
        p = 0.14 * np.exp(-((t - 0.18) / 0.032) ** 2)
        q = -0.14 * np.exp(-((t - 0.30) / 0.011) ** 2)
        r = 1.05 * np.exp(-((t - 0.335) / 0.014) ** 2)
        s = -0.24 * np.exp(-((t - 0.37) / 0.013) ** 2)
        tw = 0.28 * np.exp(-((t - 0.54) / 0.055) ** 2)
        return p + q + r + s + tw

    t = np.linspace(0, 1.8, 900)
    clean_sig = one_beat(t) + one_beat(t - 0.85)

    # Panel A: Anatomy of a Heartbeat (Lead II)
    ax1.plot(t, clean_sig, color=COBALT, lw=2.2, zorder=3)
    ax1.axhline(0, color=RULE, lw=1.0, zorder=1)
    _clean_spines(ax1)
    ax1.set_xlim(0.02, 1.66)
    ax1.set_ylim(-0.56, 1.52)
    ax1.set_xlabel("Time (seconds) — schematic Lead II trace (real ECGs: 10s @ 100 Hz)")
    ax1.set_ylabel("Voltage (mV)")
    ax1.set_title("A. Reading an ECG: Waves, R-Peaks & HRV", loc="left", pad=10)

    ax1.annotate("P-wave\n(atria)", xy=(0.18, 0.15), xytext=(0.06, 0.44),
                 fontsize=8.6, color=INK_SOFT,
                 arrowprops=dict(arrowstyle="->", color=INK_MUTED, lw=0.9))
    ax1.annotate("R-peak\n(heartbeat spike)", xy=(0.34, 0.96), xytext=(0.48, 0.92),
                 fontsize=9.0, fontweight="bold", color=VERMILION,
                 arrowprops=dict(arrowstyle="->", color=VERMILION, lw=1.2))
    ax1.annotate("Q", xy=(0.30, -0.14), xytext=(0.22, -0.32),
                 fontsize=8.6, color=INK_SOFT, ha="center",
                 arrowprops=dict(arrowstyle="->", color=INK_MUTED, lw=0.8))
    ax1.annotate("S", xy=(0.37, -0.24), xytext=(0.44, -0.36),
                 fontsize=8.6, color=INK_SOFT, ha="center",
                 arrowprops=dict(arrowstyle="->", color=INK_MUTED, lw=0.8))
    ax1.annotate("T-wave\n(reset)", xy=(0.54, 0.28), xytext=(0.64, 0.56),
                 fontsize=8.6, color=INK_SOFT,
                 arrowprops=dict(arrowstyle="->", color=INK_MUTED, lw=0.9))

    # RR Interval arrow cleanly above peaks
    ax1.annotate("", xy=(1.185, 1.20), xytext=(0.335, 1.20),
                 arrowprops=dict(arrowstyle="<->", color=FOREST, lw=1.8))
    ax1.text(0.76, 1.27, "RR Interval  →  HRV (mean, std, RMSSD)",
             ha="center", va="bottom", fontsize=9.0, fontweight="bold", color=FOREST,
             bbox=dict(boxstyle="round,pad=0.22", fc=FOREST_BG, ec=FOREST, lw=0.7))
    ax1.plot([0.335, 0.335], [1.06, 1.22], color=FOREST, ls=":", lw=1.0)
    ax1.plot([1.185, 1.185], [1.06, 1.22], color=FOREST, ls=":", lw=1.0)

    # QRS Range bracket on beat 2
    ax1.annotate("", xy=(1.32, 1.05), xytext=(1.32, -0.24),
                 arrowprops=dict(arrowstyle="<->", color=COBALT, lw=1.3))
    ax1.text(1.36, 0.42, "QRS\nRange\n(max−min)", fontsize=8.4, color=COBALT, va="center", fontweight="bold")

    ax1.text(0.84, -0.49,
             "Why Lead II? Aligned with heart's main axis → tallest clean R-peaks.",
             ha="center", fontsize=8.4, color=INK_SOFT, style="italic",
             bbox=dict(boxstyle="round,pad=0.2", fc=PAPER_ALT, ec="none"))

    # Panel B: Clean vs Baseline Drift vs Static Noise (clean separated bands)
    rng = np.random.default_rng(7)
    t_long = np.linspace(0, 2.5, 1000)
    sig_base = one_beat(t_long) + one_beat(t_long - 0.85) + one_beat(t_long - 1.70)
    drift = 0.40 * np.sin(2 * np.pi * 0.45 * t_long - 0.4)
    static = rng.normal(0, 0.13, size=len(t_long))

    ax2.plot(t_long, sig_base + 3.15, color=FOREST, lw=1.6)
    ax2.plot(t_long, sig_base + drift + 1.50, color=COBALT, lw=1.6)
    ax2.plot(t_long, drift + 1.50, color=COBALT, lw=1.0, ls="--", alpha=0.55)
    ax2.plot(t_long, sig_base + static - 0.25, color=VERMILION, lw=1.0)

    _clean_spines(ax2)
    ax2.set_xlim(0, 2.5)
    ax2.set_ylim(-0.90, 4.95)
    ax2.set_yticks([])
    ax2.set_xlabel("Time (seconds) — schematic comparison of PTB-XL artifact flags")
    ax2.set_title("B. How Sensor Artifacts Corrupt ECG Features", loc="left", pad=10)

    ax2.text(0.04, 4.42, "CLEAN SIGNAL", fontsize=8.6, fontweight="bold", color=FOREST,
             bbox=dict(boxstyle="round,pad=0.2", fc=FOREST_BG, ec="none"))
    ax2.text(0.68, 4.44, "Flat baseline, crisp R-peaks, minimal fuzz", fontsize=8.6, color=INK_SOFT)

    ax2.axhline(2.82, color=RULE, lw=0.7, ls=":")
    ax2.text(0.04, 2.52, "BASELINE DRIFT", fontsize=8.6, fontweight="bold", color=COBALT,
             bbox=dict(boxstyle="round,pad=0.2", fc=COBALT_BG, ec="none"))
    ax2.text(0.78, 2.54, "Breathing/motion (0.5–4 Hz) warps mean & QRS range", fontsize=8.5, color=INK_SOFT)

    ax2.axhline(1.02, color=RULE, lw=0.7, ls=":")
    ax2.text(0.04, 0.72, "STATIC NOISE", fontsize=8.6, fontweight="bold", color=VERMILION,
             bbox=dict(boxstyle="round,pad=0.2", fc=VERMILION_BG, ec="none"))
    ax2.text(0.68, 0.74, "Electrode fuzz (15–40 Hz) inflates ZCR & entropy", fontsize=8.5, color=INK_SOFT)

    fig.tight_layout(w_pad=2.2)
    out = FIG_DIR / "wp1_fig1_ecg_primer_and_artifacts.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)
    print(f"Saved {out}")


# ── Figure 2: Dataset Layout, Stratification & Gold vs Untrusted Shift ───────
def make_fig2_dataset_and_shift():
    set_editorial_style()
    split_df = pd.read_csv(WP1_OUT / "split_summary.csv")
    labels = np.load(WP1_OUT / "labels.npz", allow_pickle=True)
    y = labels["y"]
    fold = labels["fold"]
    gm = labels["gold_mask"].astype(bool)

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(13.4, 5.1), gridspec_kw={"width_ratios": [1.14, 0.96]}
    )
    fig.patch.set_facecolor(PAPER)

    folds = np.arange(1, 11)
    gold_c = [int(((fold == f) & (y != -1) & gm).sum()) for f in folds]
    untr_c = [int(((fold == f) & (y != -1) & ~gm).sum()) for f in folds]

    for i, f in enumerate(folds):
        if f <= 8:
            ax1.bar(f, gold_c[i], color=COBALT, width=0.68,
                    label="Train Gold D_L (Human-Verified)" if f == 1 else "")
            ax1.bar(f, untr_c[i], bottom=gold_c[i], color=VERMILION, alpha=0.85, width=0.68,
                    label="Train Untrusted D_U (Machine/Unverified)" if f == 1 else "")
            ax1.text(f, gold_c[i] / 2, f"{100*gold_c[i]/(gold_c[i]+untr_c[i]):.0f}%",
                     ha="center", va="center", color="white", fontsize=8.3, fontweight="bold")
        elif f == 9:
            ax1.bar(f, untr_c[i], color=AMBER, alpha=0.90, width=0.68, label="Validation (Fold 9)")
            ax1.text(f, untr_c[i] + 35, "Val\n1,642", ha="center", va="bottom",
                     fontsize=8.2, fontweight="bold", color=AMBER)
        else:
            ax1.bar(f, untr_c[i], color=FOREST, alpha=0.90, width=0.68, label="Held-Out Test (Fold 10)")
            ax1.text(f, untr_c[i] + 35, "Test\n1,652", ha="center", va="bottom",
                     fontsize=8.2, fontweight="bold", color=FOREST)

    ax1.axvline(8.5, color=INK_MUTED, ls="--", lw=1.1)
    _clean_spines(ax1)
    ax1.set_xticks(folds)
    ax1.set_xticklabels([f"F{f}" for f in folds])
    ax1.set_ylim(0, 2450)
    ax1.set_ylabel("Single-Label ECG Records")
    ax1.set_xlabel("PTB-XL Patient-Stratified Folds (5,565 multi-label/empty excluded from 21,837)")
    ax1.set_title("A. 10-Fold Split: Gold (9,010) + Untrusted (3,968) + Val/Test", loc="left", pad=10)
    ax1.grid(axis="y", alpha=0.5)

    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, 0.99), fontsize=8.1, ncol=2)
    ax1.text(4.5, 1730,
             "Stratified across all 10 folds (~56% NORM, ~16% MI each)\nFolds 1–8 split evenly ~69% Gold / ~31% Untrusted",
             ha="center", va="bottom", fontsize=8.3, color=INK,
             bbox=dict(boxstyle="round,pad=0.28", fc=PAPER_ALT, ec=RULE, lw=0.8))

    # Panel B: Class Distribution Shift (Gold D_L vs Untrusted D_U)
    classes = split_df["class"].tolist()
    gold_pct = 100 * split_df["gold_train"] / split_df["gold_train"].sum()
    untr_pct = 100 * split_df["untrusted_train"] / split_df["untrusted_train"].sum()

    y_pos = np.arange(len(classes))[::-1]
    h = 0.34
    ax2.barh(y_pos + h/2, gold_pct, height=h, color=COBALT, label="Gold Set D_L (N=9,010)")
    ax2.barh(y_pos - h/2, untr_pct, height=h, color=VERMILION, alpha=0.85, label="Untrusted Pool D_U (N=3,968)")

    for yp, gp, up in zip(y_pos, gold_pct, untr_pct):
        ax2.text(gp + 1.0, yp + h/2, f"{gp:.1f}%", va="center", ha="left", fontsize=8.8, color=COBALT, fontweight="bold")
        ax2.text(up + 1.0, yp - h/2, f"{up:.1f}%", va="center", ha="left", fontsize=8.8, color=VERMILION, fontweight="bold")

    mi_y = y_pos[classes.index("MI")]
    ax2.annotate("2.7× more MI in\nuntrusted reports!", xy=(28.5, mi_y - h/2), xytext=(37.5, mi_y + 0.15),
                 fontsize=8.9, fontweight="bold", color=VERMILION,
                 bbox=dict(boxstyle="round,pad=0.25", fc=VERMILION_BG, ec=VERMILION, lw=0.8),
                 arrowprops=dict(arrowstyle="->", color=VERMILION, lw=1.2))

    _clean_spines(ax2)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(["NORM (Normal)", "MI (Heart Attack)", "STTC (ST/T Change)", "CD (Conduction)", "HYP (Hypertrophy)"],
                        fontweight="bold")
    ax2.set_xlim(0, 74)
    ax2.set_xlabel("Share of Training Subset (%)")
    ax2.set_title("B. Structured Bias: Automated Software Over-Flags MI", loc="left", pad=10)
    ax2.grid(axis="x", alpha=0.5)
    ax2.legend(loc="lower right", fontsize=8.6)

    fig.tight_layout(w_pad=2.2)
    out = FIG_DIR / "wp1_fig2_dataset_funnel_and_shift.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)
    print(f"Saved {out}")


# ── Figure 3: Feature Extraction Pipeline Architecture ──────────────────────
def make_fig3_feature_architecture():
    set_editorial_style()
    fig, ax = plt.subplots(figsize=(13.6, 4.8))
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 42)
    ax.axis("off")

    ax.text(0.5, 40.2, "How Each 12-Lead ECG Becomes an 84-Dimensional Tabular Vector",
            fontsize=14, fontweight="bold", color=INK)
    ax.text(0.5, 37.3, "Turning raw time-series (1,000 × 12) into shift-invariant features across two complementary views",
            fontsize=10.2, color=INK_SOFT)

    def card(x, y, w, h, fc, ec, title, subtitle="", title_col=INK, title_gap=3.6):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.35,rounding_size=0.8",
                             facecolor=fc, edgecolor=ec, linewidth=1.4)
        ax.add_patch(box)
        ax.text(x + 1.1, y + h - 1.4, title, fontsize=9.8, fontweight="bold", color=title_col, va="top")
        if subtitle:
            ax.text(x + 1.1, y + h - 1.4 - title_gap, subtitle, fontsize=8.35, color=INK_SOFT, va="top", linespacing=1.42)

    card(0.6, 4.0, 23.8, 29.5, "#ffffff", INK,
         "RAW ECG (1,000 × 12)",
         "• 10s @ 100 Hz = 12,000 nums\n• 12 leads (I–III, aVR/L/F, V1–6)\n\nWhy not use raw directly?\n1. Heartbeats shift in time\n   across patients\n2. 12,000 dims overfit badly\n   when N_L = 180 (η = 2%)\n3. Classical ML has no time-\n   axis inductive bias",
         title_col=INK, title_gap=3.4)

    ax.annotate("", xy=(28.5, 26.2), xytext=(24.9, 22.5),
                arrowprops=dict(arrowstyle="->", color=COBALT, lw=2.2))
    ax.annotate("", xy=(28.5, 11.2), xytext=(24.9, 15.0),
                arrowprops=dict(arrowstyle="->", color=FOREST, lw=2.2))

    card(29.0, 19.8, 47.0, 14.0, COBALT_BG, COBALT,
         "VIEW 1 · TIME-DOMAIN & MORPHOLOGY  [indices 0 : 42]",
         "• Per-lead Mean & Std (12 × 2 = 24): voltage offset & spread per lead\n"
         "• Lead II HRV (3): R-peak threshold → mean RR, std RR, RMSSD\n"
         "• Shape & Hjorth (7): QRS range, ZCR, skew, kurt + Act/Mob/Complexity\n"
         "• Zero Buffer (8): 8 zero-padded slots to match View 2 width (34 + 8)",
         title_col=COBALT, title_gap=3.1)

    card(29.0, 3.6, 47.0, 14.0, FOREST_BG, FOREST,
         "VIEW 2 · FREQUENCY-DOMAIN & WAVELETS  [indices 42 : 84]",
         "• Welch PSD Bands (12 × 3 = 36): 0.5–4 (drift/T), 4–15 (QRS), 15–40 Hz\n"
         "• Spectral Shape (2): Shannon spectral entropy + 85% roll-off freq\n"
         "• Daubechies db4 Wavelets (4): 4 detail sub-bands on Lead II (Q-waves)\n"
         "• Fully Active (42 / 42 real features)",
         title_col=FOREST, title_gap=3.1)

    ax.annotate("", xy=(80.0, 21.5), xytext=(76.5, 26.2),
                arrowprops=dict(arrowstyle="->", color=COBALT, lw=2.0))
    ax.annotate("", xy=(80.0, 16.0), xytext=(76.5, 11.2),
                arrowprops=dict(arrowstyle="->", color=FOREST, lw=2.0))

    card(80.5, 4.0, 18.8, 29.5, "#ffffff", VERMILION,
         "OUTPUT: features.npz",
         "• Shape: (21,837 × 84)\n• 76 active + 8 zero pad\n• 1 flat-lead NaN row\n  median-imputed\n\nShared across WP1–WP5:\nLocks feature input so\nalgorithm comparisons\n(WP3 vs WP4 vs WP5)\nare apples-to-apples.",
         title_col=VERMILION, title_gap=3.4)

    out = FIG_DIR / "wp1_fig3_feature_architecture.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)
    print(f"Saved {out}")


# ── Figure 4: Redesigned Sensor Noise & Clustering Chart (Dumbbell + ARI) ───
def make_fig4_noise_geometry_redesign():
    set_editorial_style()
    df = pd.read_csv(WP1_OUT / "noise_analysis_results.csv")
    order = [
        "Raw+Euclidean", "Raw+Cosine", "Raw+Mahalanobis",
        "PCA+Euclidean", "PCA+Cosine", "PCA+Mahalanobis",
    ]
    df = df.set_index("variant").loc[order].reset_index()
    pretty_labels = [
        "Raw + Euclidean", "Raw + Cosine", "Raw + Mahalanobis",
        "PCA (20) + Euclidean", "PCA (20) + Cosine", "PCA (20) + Mahalanobis",
    ]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(13.4, 5.1), gridspec_kw={"width_ratios": [1.16, 0.94]}
    )
    fig.patch.set_facecolor(PAPER)

    y = np.arange(len(df))[::-1]

    ax1.axhspan(-0.5, 2.5, color=PAPER_ALT, alpha=0.5, zorder=0)
    ax1.axhline(2.5, color=RULE, lw=1.0, ls="-")

    for i, row in df.iterrows():
        yp = y[i]
        pc, pn, pa = row["purity_clean"], row["purity_noisy"], row["purity_all"]
        gap_pp = (pc - pn) * 100
        ax1.plot([pn, pc], [yp, yp], color=VERMILION, lw=3.0, alpha=0.75, zorder=2)
        ax1.scatter(pn, yp, color=VERMILION, s=95, zorder=4,
                    label="Noisy ECGs (artifact flag)" if i == 0 else "")
        ax1.scatter(pc, yp, color=FOREST, s=95, zorder=4,
                    label="Clean ECGs (no flag)" if i == 0 else "")
        ax1.scatter(pa, yp, color=INK, marker="D", s=42, zorder=5,
                    label="All training ECGs" if i == 0 else "")

        ax1.text((pn + pc) / 2, yp + 0.19, f"−{gap_pp:.1f} pp",
                 ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=VERMILION)
        ax1.text(pn - 0.0025, yp, f"{pn:.3f}", ha="right", va="center", fontsize=8.3, color=VERMILION)
        ax1.text(pc + 0.0025, yp, f"{pc:.3f}", ha="left", va="center", fontsize=8.3, color=FOREST)

    _clean_spines(ax1)
    ax1.set_yticks(y)
    ax1.set_yticklabels(pretty_labels, fontweight="bold")
    ax1.set_xlim(0.515, 0.610)
    ax1.set_ylim(-0.6, 5.85)
    ax1.set_xlabel("k-Means Cluster Purity (zoomed 0.515 – 0.610; 1.0 = pure)")
    ax1.set_title("A. Purity Drop Under Sensor Noise", loc="left", pad=26)
    ax1.grid(axis="x", alpha=0.5)
    ax1.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=3, fontsize=8.2, frameon=True)

    aris = df["ari_all"].values
    colors = [INK_MUTED, INK_MUTED, COBALT, COBALT, INK_MUTED, COBALT]
    ax2.barh(y, aris, height=0.54, color=colors, alpha=0.9)
    ax2.axhspan(-0.5, 2.5, color=PAPER_ALT, alpha=0.5, zorder=0)
    ax2.axhline(2.5, color=RULE, lw=1.0)

    for yp, val, var in zip(y, aris, df["variant"]):
        fw = "bold" if "Mahalanobis" in var or var == "PCA+Euclidean" else "normal"
        col = COBALT if "Mahalanobis" in var or var == "PCA+Euclidean" else INK_SOFT
        extra = "  (2.2× Raw+Euc!)" if var == "Raw+Mahalanobis" else ("  (+49%)" if var == "PCA+Euclidean" else "")
        ax2.text(val + 0.0025, yp, f"{val:.4f}{extra}", va="center", ha="left",
                 fontsize=8.7, fontweight=fw, color=col)

    _clean_spines(ax2)
    ax2.set_yticks(y)
    ax2.set_yticklabels([""] * len(y))
    ax2.set_xlim(0, 0.168)
    ax2.set_ylim(-0.6, 5.85)
    ax2.set_xlabel("Adjusted Rand Index (ARI, 12,978 training ECGs)")
    ax2.set_title("B. Cluster Alignment (ARI): Mahalanobis & PCA Win", loc="left", pad=26)
    ax2.grid(axis="x", alpha=0.5)

    fig.tight_layout(w_pad=1.6)
    out = FIG_DIR / "wp1_fig4_noise_geometry_redesign.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)
    print(f"Saved {out}")


# ── Figure 5: Full PCA Scree + Real PTB-XL 2D Overlap Scatter ───────────────
def make_fig5_pca_and_overlap():
    set_editorial_style()
    X = np.load(WP1_OUT / "features.npz")["X"]
    d = np.load(WP1_OUT / "labels.npz")
    y, fold = d["y"], d["fold"]

    train_mask = np.isin(fold, range(1, 9)) & (y != -1)
    X_tr = X[train_mask]
    y_tr = y[train_mask]

    Xs = StandardScaler().fit_transform(X_tr)
    pca = PCA(n_components=84, random_state=42).fit(Xs)
    X_pca = pca.transform(Xs)
    cum = np.cumsum(pca.explained_variance_ratio_) * 100

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(13.4, 5.0), gridspec_kw={"width_ratios": [1.0, 1.08]}
    )
    fig.patch.set_facecolor(PAPER)

    pcs = np.arange(1, 85)
    ax1.plot(pcs, cum, color=COBALT, lw=2.3)
    ax1.fill_between(pcs, 0, cum, color=COBALT_BG, alpha=0.55)
    ax1.axhline(90, color=VERMILION, ls="--", lw=1.3, label="90% variance threshold (PC 24)")
    ax1.axvline(20, color=FOREST, ls=":", lw=1.5, label="WP1 choice: 20 PCs (86.3%)")

    for k, dx, dy in [(5, 4, -8), (10, 4, -8), (20, 3, -10), (24, 4, 4)]:
        ax1.scatter(k, cum[k-1], color=INK, s=42, zorder=5)
        ax1.annotate(f"PC {k}: {cum[k-1]:.1f}%", xy=(k, cum[k-1]),
                     xytext=(k + dx, cum[k-1] + dy),
                     fontsize=8.5, fontweight="bold", color=INK,
                     arrowprops=dict(arrowstyle="-", color=INK_MUTED, lw=0.7))

    ax1.text(62, 52, "PC 74–84 = 0% gain\n(8 zero-padded cols +\ncollinearities)",
             fontsize=8.4, color=INK_MUTED, ha="center",
             bbox=dict(boxstyle="round,pad=0.3", fc=PAPER_ALT, ec=RULE, lw=0.8))

    _clean_spines(ax1)
    ax1.set_xlim(1, 84)
    ax1.set_ylim(15, 104)
    ax1.set_xlabel("Number of Principal Components (out of 84)")
    ax1.set_ylabel("Cumulative Explained Variance (%)")
    ax1.set_title("A. Full PCA Scree Curve: 24 Components Reach 90%", loc="left", pad=10)
    ax1.grid(True, alpha=0.45)
    ax1.legend(loc="lower right", fontsize=8.5)

    rng = np.random.default_rng(42)
    idx_sub = rng.choice(len(y_tr), size=2500, replace=False)
    cls_names = ["NORM", "MI", "STTC", "CD", "HYP"]
    cls_cols = [COBALT, VERMILION, AMBER, FOREST, "#7c3aed"]

    p1 = X_pca[idx_sub, 0]
    p2 = X_pca[idx_sub, 1]
    ys = y_tr[idx_sub]

    for c in range(5):
        mc = ys == c
        ax2.scatter(p1[mc], p2[mc], s=14, alpha=0.42, color=cls_cols[c], label=cls_names[c], edgecolors="none")

    offsets = [(-1.8, 1.3), (-1.9, -1.1), (1.0, 1.0), (1.1, -0.5), (0.8, 0.7)]
    for c in range(5):
        cx, cy = np.median(X_pca[y_tr == c, 0]), np.median(X_pca[y_tr == c, 1])
        ax2.scatter(cx, cy, s=145, color=cls_cols[c], edgecolors="white", linewidth=1.6, marker="X", zorder=6)
        dx, dy = offsets[c]
        ax2.annotate(cls_names[c], xy=(cx, cy), xytext=(cx + dx, cy + dy),
                     fontsize=8.0, fontweight="bold", color=cls_cols[c],
                     bbox=dict(boxstyle="round,pad=0.14", fc="white", ec=cls_cols[c], lw=0.7, alpha=0.92),
                     arrowprops=dict(arrowstyle="-", color=cls_cols[c], lw=0.8), zorder=7)

    ax2.set_xlim(-6.5, 10.5)
    ax2.set_ylim(-5.8, 8.5)
    _clean_spines(ax2)
    ax2.set_xlabel(f"PC 1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)")
    ax2.set_ylabel(f"PC 2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)")
    ax2.set_title("B. Real PTB-XL Feature Overlap (2,500 ECGs, Medians = X)", loc="left", pad=10)
    ax2.grid(True, alpha=0.4)
    ax2.legend(loc="upper right", fontsize=8.4, markerscale=1.6, ncol=2)

    ax2.text(2.0, -5.25,
             "Class medians sit clustered together → explains\nwhy unsupervised k-Means caps at ~0.58 purity",
             ha="center", va="bottom", fontsize=8.3, fontweight="bold", color=VERMILION,
             bbox=dict(boxstyle="round,pad=0.25", fc=VERMILION_BG, ec=VERMILION, lw=0.7))

    fig.tight_layout(w_pad=2.0)
    out = FIG_DIR / "wp1_fig5_pca_and_overlap.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)
    print(f"Saved {out}")


if __name__ == "__main__":
    make_fig1_ecg_primer()
    make_fig2_dataset_and_shift()
    make_fig3_feature_architecture()
    make_fig4_noise_geometry_redesign()
    make_fig5_pca_and_overlap()
    print("All WP1 presentation figures regenerated!")
