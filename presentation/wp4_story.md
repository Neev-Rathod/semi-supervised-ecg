# WP4 Presentation Story & Speaker Guide: Dual-View Co-Training & Transductive SVM (3 Slides)

**Owner:** Arnav Gupta (WP4) · **Course:** BITS F464 Machine Learning  
**Budget:** 3 Slides (strictly Q3 + discriminative SSL defense) · **Visuals:** [`presentation/figures/`](./figures/)

> **Core Takeaway:** Both WP4 methods **discard noisy machine labels $\tilde{y}_U$** (Approaches 2 & 3 for **Q3**), asking whether **discriminative structure** succeeds where WP3's passive graph smoothing failed. **Co-Training** shines under acute Gold scarcity ($\eta \le 10\%$, up to `+0.071` F1 over 2-View Base and beating Full-84D at `2–5%`), while **TSVM** lifts balanced RBF-SVM at every $\eta$ (up to `+0.031` at $\eta=20\%$)—yet both leave the `3,968` hospital labels $\tilde{y}_U$ unused.

---

### Slide 1 — Dual-View Co-Training: Strong Gains Under Scarcity, Clear Saturation Ceiling
**Visual:** [`figures/wp4_fig1_cotraining_curves.png`](./figures/wp4_fig1_cotraining_curves.png)

* **Architecture built directly from WP1 & WP2 lessons:**
  Separate `HistGradientBoostingClassifier(max_depth=4)` learners (respecting WP2's depth cap) train on **View 1** (Time/HRV/Morphology, `0:42`) and **View 2** (Frequency/Wavelets, `42:84`). Up to `12` rounds pseudo-label top `10`/class unlabeled records only under **non-contradictory high confidence (`>=0.72`)** with conservative sample weight (`0.35`).
* **Two clear operating regimes (`Panel A` & `Panel B`):**
  * **Scarcity Sweet Spot ($\eta \le 10\%$):** Co-Training jumps **`+0.051` at $\eta=2\%$ (`0.315 → 0.365` val; `0.352` test)** and **`+0.071` at $\eta=5\%$ (`0.361 → 0.431` val; `0.397` test)** over the `2-View Supervised Base`—and beats the joint **`Full-84D` tree model** by `+0.020` (`2%`) and **`+0.057` (`5%`: `0.374 → 0.431`)**!
  * **Abundance Saturation ($\eta \ge 20\%$):** By `4,505` Gold records ($\eta=50\%$), `Full-84D` (`0.516`) overtakes Co-Training (`0.470`), showing pseudo-labeling cannot beat cross-view joint splits once clean labels are plentiful.

---

### Slide 2 — Inside Co-Training: Rare-Class Recovery & Why Two ECG Views Stay Complementary
**Visual:** [`figures/wp4_fig2_cotraining_diagnostics.png`](./figures/wp4_fig2_cotraining_diagnostics.png)

* **Where does the `+0.071` F1 lift at $\eta=5\%$ (`450` Gold records) actually happen? (`Panel A`)**
  Unlike WP3 Graph LP which blurred minority classes into `NORM`, Co-Training boosts **every class**, led by rare pathologies: **`HYP` nearly doubles (`0.164 → 0.306`, `+0.142`)**, **`STTC` jumps `+0.116` (`0.167 → 0.284`)**, and **`MI` climbs `+0.074` (`0.297 → 0.371`)** (`+0.152` on `MI` at $\eta=2\%$: `0.212 → 0.363`).
* **Validating Blum & Mitchell's View Independence on Real ECGs (`Panel B`):**
  * **View 2 leads by `+6 to +8 pp`** (`0.355–0.483` vs View 1 `0.277–0.405`), showing spectral bands and `db4` wavelets isolate transient abnormalities better than global time summaries.
  * Yet final-round **cross-view agreement holds near `77.4–80.5%`** (`~20–23%` genuine disagreement), keeping the two views complementary rather than collapsing into WP2's single-view echo chamber.

---

### Slide 3 — Transductive SVM (TSVM): Max-Margin Exploitation & Support Vector Cost
**Visual:** [`figures/wp4_fig3_tsvm_results.png`](./figures/wp4_fig3_tsvm_results.png)

* **Preventing WP2's margin collapse when scaling to `3,968` unlabeled ECGs:**
  Fitting balanced RBF-SVM with Joachims-style switching (3 iters) on **all** unlabeled points bloated boundaries; filtering to the **top `35%` margin-confident pool (`1,389 / 3,968`)** and annealing unlabeled weight `C_U: 0.05 → 0.30` unlocks steady gains everywhere (`Panel A`):
  * Beats balanced RBF-SVM at **all 5 $\eta$ values**, peaking at **`+0.026` ($\eta=10\%$: `0.433 → 0.458`, test `0.441`)** and **`+0.031` ($\eta=20\%$: `0.458 → 0.488`, test `0.459`)**, reaching `0.499` val / `0.474` test at $\eta=50\%$.
* **Support Vector Trade-off (`Panel B`) & Transition to WP5:**
  TSVM inflates total support vectors as expected from WP2 (`177 → 1,099` at `2%`; `848 → 1,540` at `10%`), though capped `C_U <= 0.30` preserves generalization. **Key open gap for Q3:** WP4 proves discriminative SSL beats WP3 Graph LP (`0.458` vs `0.312` at `10%`), yet both still **discard $\tilde{y}_U$**. WP5 asks: *can modeling hospital errors beat discarding them?*

---

## Defense Notes (If Asked in Q&A)
* **"Why does Co-Training drop below `Full-84D` at $\eta=20\text{–}50\%$?"** Expected theoretical trade-off: with `180–450` Gold samples, splitting `84-D` avoids curse of dimensionality and leverages `3,968` unlabeled ECGs; with `1,802–4,505` Gold samples, joint GBDT splits across both views (`Full-84D`) outvalue noisy pseudo-labels.
* **"Why keep only the top 35% confidence margin in TSVM instead of all 3,968 points?"** In dense overlapping ECG space (WP1 purity `~0.58`), forcing ambiguous boundary points into TSVM causes WP2-style margin contamination and SV explosion.
