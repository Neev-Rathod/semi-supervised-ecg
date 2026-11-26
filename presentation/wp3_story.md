# WP3 Presentation Story & Speaker Guide: Harmonic Graph Label Propagation (3 Slides)

**Owner:** Pratyush Somani (WP3) · **Course:** BITS F464 Machine Learning  
**Budget:** 3 Slides (strictly Q1/Q3 + SSL comparison) · **Visuals:** [`presentation/figures/`](./figures/)

> **Core Takeaway:** WP3 tests **Approach 1 ("Discard $\tilde{y}_U$ via Pure Graph Geometry")** by diffusing cardiologist Gold labels across a Gaussian-weighted $k$-NN graph (**900 grid fits**). Resolving WP1's metric hypothesis, `PCA=5, k=3, Euclidean` proves cleanest (`0.312` val / `0.309` test at $\eta=10\%$), **yet pure diffusion lags simple linear/SVM baselines by `0.09–0.13` F1**—confirming WP1's disease-overlap warning and directly motivating WP4 and WP5.

---

### Slide 1 — Harmonic Graph SSL & Why `PCA = 5, k = 3` Resolves the Mahalanobis Paradox
**Visual:** [`figures/wp3_fig1_metric_and_k.png`](./figures/wp3_fig1_metric_and_k.png)

* **Method (Zhu et al., Eq. 4.2):**
  Completely discard noisy machine labels $\tilde{y}_U$, build a mutual/symmetric $k$-NN similarity graph over $\mathcal{D}_L \cup \mathcal{D}_U$, and solve the closed-form harmonic linear system $(D_{UU} - W_{UU}) F_U = W_{UL} Y_L$.
* **What 900 grid runs (`distance × PCA × k × η`) reveal:**
  1. **Resolves WP1 vs. WP3 Mahalanobis (`Panel A`):** WP1 computed $\hat{\Sigma}$ on all `12,978` training ECGs (`2.2×` ARI); WP3 estimates $\hat{\Sigma}_L^{-1}$ strictly from scarce Gold anchors ($\eta=2\text{–}50\%$). On raw 84-D vectors, noisy matrix inversion collapses Mahalanobis (`0.211`), recovering **only at `PCA=5`** (`0.290` vs Euclidean `0.294`).
  2. **Neighborhood blurring (`Panel B`):** Small, tight graphs (`k=3`, `1.3–2.0` components, `<6` unreachable nodes) outperform wide graphs (`k=3: 0.299 → k=20: 0.245` mean) because extra edges cross class boundaries.

---

### Slide 2 — Held-Out Test (Fold 10): Graph LP vs. Same-Space Gold $k$-NN & Supervised Baselines
**Visual:** [`figures/wp3_fig2_test_comparison.png`](./figures/wp3_fig2_test_comparison.png)

* **Two decisive scientific controls (`PCA=5, k=3` on untouched Fold 10 test):**
  1. **No transductive lift over identical-space Gold $k$-NN (`Panel B`):** Comparing Graph LP against a simple $k$-NN classifier fit on the *exact same* `PCA=5` Gold subset gives `0.258 vs 0.306` ($\eta=2\%$), `0.309 vs 0.328` ($\eta=10\%$), and `0.352 vs 0.348` ($\eta=50\%$). Unlabeled ECG neighbors do **not** sharpen class boundaries here.
  2. **Supervised Baselines win by `+0.09 to +0.13` F1 (`Panel A`):** Balanced `SVM-RBF` (`0.352 → 0.471`) and `LogReg (bal)` (`0.335 → 0.457`) vastly outperform Graph LP (`0.258 → 0.352`) at every scarcity level—and even **unweighted LogReg** (`0.341 → 0.429`) beats Graph LP cleanly.

---

### Slide 3 — Diagnosis & Pivot: Why Pure Geometry Fails on ECGs (Setting Up WP4 & WP5)
**Visual:** [`figures/wp3_fig3_class_collapse.png`](./figures/wp3_fig3_class_collapse.png)

* **Class-level failure analysis at $\eta=10\%$ (`901` Gold records):**
  Unweighted LogReg beats Graph LP on **all 5 classes** (`NORM 0.775 vs 0.720`), with the worst collapse on minority/ischemic classes **`STTC` (`0.106 vs 0.262`)** and **`MI` (`0.181 vs 0.260`)**.
* **Why is this negative result scientifically crucial (Answering Q3)?**
  1. **Validates WP1's prediction:** ECG superclasses do **not** form separated clusters (`k`-Means purity `~0.58`), so smoothing labels across nearest neighbors floods `STTC`/`MI`/`HYP` with majority `NORM` (`~55%`).
  2. **Eliminates Approach 1 cleanly:** Simply throwing away $\tilde{y}_U$ and relying on unsupervised distance smoothness cannot beat clean linear hyperplanes—we must either exploit **cross-view/margin structure (WP4)** or **model & invert the hospital noise channel $\tilde{y}_U$ (WP5)**.

---

## Defense Notes (If Asked in Q&A)
* **"Why didn't you evaluate on raw 84-D with tuned weights?"** Raw 84-D LP (`k=3..20`) was run in the 900-fit grid (`euclidean PCA=0` averaged `0.266`, peaking at `0.361` at $\eta=50\%$—still `0.06–0.12` below unweighted LogReg).
* **"Why was Class-Mass Normalization (`CMN`) omitted from final test controls?"** A matched 60-run ablation showed CMN added mean ΔF1 `+0.0014`—negligible compared to the `~0.10` supervised gap.
