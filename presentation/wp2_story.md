# WP2 Presentation Story & Speaker Guide: Synthetic Lab & Noise Baselines (3 Slides)

**Owner:** Shaurya Suman (WP2) · **Course:** BITS F464 Machine Learning  
**Budget:** 3 Slides (tightened to Q2 + WP3/4/5 defense only) · **Visuals:** [`presentation/figures/`](./figures/)

> **Core Takeaway:** Because real hospital $\mathcal{D}_U$ lacks true ground truth $T_{\text{true}}$ and a controllable noise dial $\varepsilon$, WP2 pairs a **50-D causal synthetic lab** with **3 noise injectors** and **5 supervised baselines** (plus real PTB-XL verification)—proving **Q2**: structured pair confusion breaks every model where uniform flips don't, naive self-training self-contaminates, and margin/tree bloat motivates WP4–WP5.

---

### Slide 1 — Controlled Causal Lab, 5 Model Families & Uniform Breakdown
**Visual:** [`figures/wp2_fig2_uniform_breakdown_small_multiples.png`](./figures/wp2_fig2_uniform_breakdown_small_multiples.png)

* **Why a 50-D synthetic manifold + why these 5 models?**
  PTB-XL hides true $\mathcal{D}_U$ labels ($T_{\text{true}}$ is unknown), so WP2 constructs `3,000` orthogonal-rotated samples (`10` informative + `5` correlated redundant + `35` noise dims, `420` Gold / `1,680` corrupted Pool / `450` Val / `450` Test). Each baseline maps directly to downstream WPs: **Gaussian NB** (generative → WP5), **LogReg** (linear → WP5 base + WP3 baseline), **7-NN** (local → WP3), **Decision Tree** (variance → WP4 depth-4 trees), **RBF-SVM** (max-margin → WP4 TSVM).
* **Uniform Noise Results ($\varepsilon: 0 \to 60\%$ on $\mathcal{D}_U$ only) & Failure Mechanics:**
  * **High-variance models shatter first:** Unpruned **Decision Tree** collapses `−38.5%` (`0.582 → 0.358`, leaves swell `348 → 641` memorizing noise; capping `max_depth=5` prevents bloat—applied directly in WP4!). **7-NN** drops `−27.1%` (`0.817 → 0.595`), crossing below `gold_only` at $\varepsilon \approx 32\%$.
  * **Margin cost behind SVM resilience:** RBF-SVM drops only `−7.4%` under uniform flips, yet support vectors bloat from `1,318` (`63%`) to **`2,015` (`96%` of train)**—previewing WP4 TSVM's SV growth.
  * **Single-view `self_training` backfires (`GNB −8.3 pp`):** Ignoring $\tilde{y}_U$ and pseudo-labeling own `>90%` confidence predictions poisons poorly calibrated GNB (`0.648 → 0.565`), justifying **WP4's dual-view cross-consistency**.

---

### Slide 2 — [Q2] The Crucial Twist: Uniform vs. Asymmetric & Boundary Noise
**Visual:** [`figures/wp2_fig4_three_noise_types.png`](./figures/wp2_fig4_three_noise_types.png)

* **Comparing all 3 mathematical noise channels by actual `%` of $\mathcal{D}_U$ flipped:**
  1. **Uniform Flips (`Panel A`):** Noise spreads across 4 wrong classes, leaving the true class with the plurality vote even at `60.2%` flips (`SVM = 0.814`, `LR = 0.610`).
  2. **Asymmetric Pair Confusion `0↔1, 2↔3` (`Panel B` — hospital-like bias!):** At just `48.5%` actual flips ($p=0.60$), **every single model crashes**: `SVM` plunges `0.879 → 0.534`, `LR` falls `0.761 → 0.440`, and `GNB` collapses `0.649 → 0.464`. Concentrated pair flips overwhelm plurality voting.
  3. **Boundary Noise Eq. 3.1 (`Panel C`):** Flipping points near decision boundaries ($\gamma=2$) drops `SVM-naive_pool` (`0.794`) below `gold_only` (`0.813`) by `40%` flips—sooner than uniform noise.
* **Direct Bridge to WP5:** Structured confusion cannot be solved by regularization or thresholding alone—we **must explicitly model a full $C \times C$ confusion channel $T$** (WP5), tested on WP2's exact asymmetric generator.

---

### Slide 3 — Reality Check on Real PTB-XL (`9,010` Gold + `3,968` Untrusted)
**Visual:** [`figures/wp2_fig5_ptbxl_reality_check.png`](./figures/wp2_fig5_ptbxl_reality_check.png)

* **What changes under real class imbalance (`62.5% NORM`) and `28% MI` machine shift?**
  1. **`GNB` flips from "resilient" (`−6.3%`) to worst-hit (`−9.7 pp`):** Real `naive_pool` **`GNB` crashes at $\eta=2\%$ (`0.362 → 0.265`)** and stays crushed everywhere because `28% MI` hospital over-diagnosis corrupts generative priors and class variances.
  2. **Supervised Bar Established:** With class weighting, **`LR (balanced)`** climbs from `0.403` ($\eta=2\%$) to **`0.494` val (`0.466` test)** at $\eta=100\%$, overtaking `naive_pool` (`0.489`) once Gold abundance removes the need for noisy hospital labels.
  3. **Naive `self_training` still lags on ECGs** (e.g., `kNN` drops `0.216 → 0.143` at $\eta=2\%$), handing WP3–WP5 an unambiguous baseline benchmark to beat.

---

## Defense Notes (If Asked in Q&A)
* **"Why corrupt only $\mathcal{D}_U$ and not $\mathcal{D}_L$ or validation?"** $\mathcal{D}_L$ models cardiologist verification (trusted anchor); validation tests true performance. Only hospital auto-reports ($\mathcal{D}_U$) vary in reliability $\varepsilon$.
* **"Aren't 50-D Gaussian clusters too clean compared to PTB-XL?"** Deliberately so: removing class imbalance and ECG feature overlap isolates pure label-noise laws in Slides 1–2, then Slide 3 tests real PTB-XL (`outputs/wp2/ptbxl_baselines.csv`) to expose what `28% MI` skew adds on top. *(Additional reference plots kept in figures/: `wp2_fig1_synthetic_design.png`, `wp2_fig3_failure_mechanics.png`.)*
