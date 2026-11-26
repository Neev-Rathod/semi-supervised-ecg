# WP5 Presentation Story & Speaker Guide: Latent Noise Channel EM & Clinical Audit (3 Slides)

**Owner:** Tanuj Yadav (WP5) · **Course:** BITS F464 Machine Learning  
**Budget:** 3 Slides (strictly Q3 & Q4 synthesis) · **Visuals:** [`presentation/figures/`](./figures/)

> **Core Takeaway:** WP5 implements **Approach 4 ("Keep & Denoise $\tilde{y}_U$")** via an anchored Expectation-Maximization model (`LatentNoiseEM`), recovering the hidden $5 \times 5$ hospital confusion matrix $T$ cleanly (`Frobenius error 0.364 → 0.135`), winning all **20/20 `(η, ε)` Discard-vs-Correct cells** in WP5's benchmark (`0.462` F1 at just `180` Gold records!), and exposing the **exact software bias** (`NORM→MI 9.41%`, `STTC→MI 9.18%`) behind WP1's opening mystery (**Q4**).

---

### Slide 1 — Treating Hospital Software as a Noisy Channel (`LatentNoiseEM`)
**Visual:** [`figures/wp5_fig1_em_recovery.png`](./figures/wp5_fig1_em_recovery.png)

* **The Core Idea (Eq. 4.4–4.5) — Stop throwing away imperfect labels:**
  Automated ECG labels $\tilde{y}_i$ are wrong roughly `10–20%` of the time, meaning they are **right `80–90%` of the time**. Instead of discarding $\tilde{y}_U$ (WP3/WP4), WP5 jointly models the clean feature classifier $P(y \mid x; \theta)$ and the hospital's stochastic confusion channel $T_{c,j} = P(\tilde{y}=j \mid y=c)$:
  1. **Anchor Init (`Panel A`):** Fit balanced Logistic Regression $\theta^{(0)}$ on clean Gold $\mathcal{D}_L$, with Laplace prior ($\alpha = 1.0$) stabilizing rare `HYP`.
  2. **E-Step:** Infer true-disease posteriors $\gamma_{i,c} \propto P(y=c \mid x_i; \theta) \cdot T_{c,\tilde{y}_i}$ on $\mathcal{D}_U$.
  3. **M-Step:** Update confusion rows $T$ and refit weighted $\theta$ across clean $\mathcal{D}_L$ + soft posteriors $\gamma_i$.
* **Proof of Channel Recovery (`Panel B` — Validated via WP2's Synthetic Lab):**
  Because PTB-XL lacks ground-truth $T_{\text{true}}$ on $\mathcal{D}_U$, WP5 benchmarks against WP2's `generate_manifold` + asymmetric $T_{\text{true}}$: Frobenius error $\| \hat{T} - T_{\text{true}} \|_F$ falls **−63%** (`0.364` at `n_pool=100` → **`0.135`** at `n_pool=2,000`).

---

### Slide 2 — [Q3] The Discard-vs-Correct Verdict Across Scarcity ($\eta$) & Extra Noise ($\varepsilon$)
**Visual:** [`figures/wp5_fig2_discard_vs_correct.png`](./figures/wp5_fig2_discard_vs_correct.png)

* **EM dominates all `20 / 20` `(η, ε)` benchmark cells (`Panel B` — `0.411–0.462` Val F1):**
  * **Largest edge under extreme Gold scarcity (`Panel A`):** With only `180` cardiologist labels ($\eta=2\%$), EM reaches **`0.462` Macro F1**—crushing WP3 Graph LP (`0.183`) and baseline CoTrain (`0.355`) by `+0.108` to `+0.279`!
  * **Immunity to heavy extra corruption:** Injecting **`+45%` extra symmetric noise** ($\varepsilon=0.45$) lowers EM only slightly (`0.462 → 0.413` at `2%`; `0.456 → 0.425` at `50%`), because inverting $\hat{T}$ extracts whatever residual signal survives inside $\tilde{y}_U$.
* **Complete Q3 Synthesis (Accounting for WP4's HistGBT Upgrade):**
  * WP5's saved 20-cell CSV (`discard_vs_correct.csv`) ran against WP4's initial LogReg `CoTrainer` (`0.326–0.355`). Comparing fairly against WP4's upgraded `HistGBT` Co-Training (`0.365–0.470`) and TSVM (`0.388–0.499`) reveals the **true project phase law**:
  * **When Gold is scarce ($\eta = 2\text{–}10\%$):** Modeling noisy labels via **`EM` (`0.453–0.462`)** cleanly beats discarding them via CoTrain (`0.365–0.439`) or TSVM (`0.388–0.458`). Once Gold exceeds ~`1,800–4,500` records ($\eta \ge 20\%$), richer nonlinear margins (`TSVM 0.488–0.499`) and boosted trees catch up.

---

### Slide 3 — [Q4] Clinical Software Audit: Closing the Entire Project Loop
**Visual:** [`figures/wp5_fig3_clinical_audit.png`](./figures/wp5_fig3_clinical_audit.png)

* **Fitting `LatentNoiseEM` across the full hospital pool (`9,010` Gold + `3,968` Pool, converged in `39` iters):**
  1. **Diagonal Reliability (`Panel A`):** Machine auto-reports are highly trustworthy for **`CD` (`96.5%`)**, **`MI` (`95.8%`)**, **`STTC` (`89.5%`)**, and **`NORM` (`87.9%`)**, but unreliable on **`HYP` (`79.2%`)** (`HYP → NORM: 6.19%`, `HYP → CD: 5.80%`).
  2. **The Two Major False-Alarm Channels (`Panel B`):**
     **`NORM → MI` (`9.41%`)** and **`STTC → MI` (`9.18%`)** — confirming clinicians' intuition that automated hospital software uses aggressive *"rule-out heart attack"* sensitivity thresholds!
* **Project-Wide Closure:**
  * WP1 discovered `MI` jumped `2.7×` (`10.4% → 28.0%`) in unverified hospital reports; WP2 proved `GNB-naive_pool` collapses (`−9.7 pp`) under such shift; WP5 quantitatively pinpoints *exactly* which healthy (`NORM`) and `STTC` patients caused the surge—and turns biased machine logs into our strongest scarce-label learner (`0.462` at `2%`).

---

## Defense Notes (If Asked in Q&A)
* **"Why do WP4's standalone CSV numbers (`0.431–0.470`) differ from `CoTrain` inside `outputs/wp5/discard_vs_correct.csv` (`0.326–0.355`)?"** Chronological commit order: WP5 ran before WP4 upgraded `CoTrainer` from `LogisticRegression` to `HistGradientBoostingClassifier`. We show both curves transparently on Slide 2 (`wp5_fig2`), proving EM (`0.462`) still wins the scarce regime ($\eta=2\text{–}10\%$) decisively even against upgraded CoTrain (`0.365–0.439`).
* **"Is `LatentNoiseEM`'s $5 \times 5$ matrix identifiable without anchor guarantees?"** Yes—clean Gold anchors ($\mathcal{D}_L$) pin $P(y \mid x; \theta)$, while Laplace smoothing ($\alpha = 1.0$) prevents rare rows (`HYP`) from collapsing.
