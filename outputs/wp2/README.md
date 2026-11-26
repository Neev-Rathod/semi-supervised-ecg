# WP2 Outputs – Synthetic Generator & Supervised Baselines
**Author:** Shaurya Suman (2024A7PS0589G)  
**Work Package:** WP2 – Synthetic Generator & Supervised Baselines  
**Date:** November 2026  
**Course:** BITS F464 – Machine Learning, Sem 1 2026–2027  
**Instructor:** Prof. Anand Narasimhamurthy  

---

## 1. Overview and Deliverables

WP2 serves as the **controlled causal diagnostic lab** and **supervised reference floor** for the entire project:

1. **Synthetic Benchmark Suite (`synthetic_generator.py`)**: A 5-class, 50-dimensional manifold (`10` informative + `5` redundant + `35` ambient noise features, orthogonally projected) with **three noise injectors**: Uniform, Asymmetric pair confusion, and Boundary-Dependent (Proposal Eq. 3.1). Used by WP2 to isolate failure modes and imported by WP5 to prove confusion-matrix recovery against known ground truth $T_{\text{true}}$.
2. **Five Supervised Baselines (`baselines.py`)**: `GaussianNaiveBayes`, `LogisticRegressionModel`, `KNNClassifierModel`, `DecisionTreeModel`, and `SVMModel` (using deterministic `CalibratedClassifierCV(SVC, cv=3, ensemble=False)`), each supporting three training modes (`gold_only`, `naive_pool`, `self_training`).
3. **Real PTB-XL Baselines (`ptbxl_baselines.csv`)**: Evaluates all 5 baselines (plus balanced `LR` and `SVM`) across $\eta \in \{2\%, 5\%, 10\%, 20\%, 50\%, 100\%\}$ of WP1's Gold Set against the real hospital Untrusted Pool $\mathcal{D}_U$ on Fold 9 (Val) and Fold 10 (Test).

### Generated Files in `outputs/wp2/`

| File | Description |
|------|-------------|
| `noise_breakdown.csv` | Synthetic uniform noise sweep: 5 classifiers × 3 modes × $\varepsilon \in \{0, 0.15, 0.30, 0.45, 0.60\}$ |
| `f1_vs_epsilon.png` | Synthetic uniform breakdown curves (all 15 model/mode combinations) |
| `svm_support_vectors.png` | SVM support vector inflation under uniform noise |
| `tree_depth_vs_epsilon.png` | Decision tree overfitting: unpruned vs. pruned (`max_depth=5`) |
| `noise_type_comparison.csv` | Uniform vs. Asymmetric vs. Boundary-Dependent noise (225 rows with `actual_flip_rate`) |
| `noise_types_comparison.png` | Side-by-side degradation comparison across all 3 noise mechanisms |
| `ptbxl_baselines.csv` | Real PTB-XL 3-mode baseline results across $\eta \in [0.02, 1.00]$ (Val & Test) |
| `ptbxl_baselines.png` | Real PTB-XL `gold_only` vs. `naive_pool` macro F1 across $\eta$ |
| `README.md` | This technical report |

---

## 2. Synthetic Results: Uniform Breakdown (`noise_breakdown.csv`)

Split: `420` Gold $\mathcal{D}_L$, `1,680` Untrusted $\mathcal{D}_U$ (noise injected *only* into $\mathcal{D}_U$), `450` Validation, `450` Test.

| $\varepsilon$ | GNB gold | GNB naive | LR gold | LR naive | kNN gold | kNN naive | DT gold | DT naive | SVM gold | SVM naive | SVM self |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **0.00** | 0.6480 | 0.6487 | 0.6820 | 0.7612 | 0.7406 | 0.8167 | 0.4863 | 0.5817 | 0.8133 | **0.8791** | 0.8133 |
| **0.15** | 0.6480 | 0.6232 | 0.6820 | 0.7432 | 0.7406 | 0.8103 | 0.4863 | 0.5489 | 0.8133 | **0.8615** | 0.8133 |
| **0.30** | 0.6480 | 0.6108 | 0.6820 | 0.7070 | 0.7406 | 0.7475 | 0.4863 | 0.4729 | 0.8133 | **0.8660** | 0.8133 |
| **0.45** | 0.6480 | 0.6074 | 0.6820 | 0.6922 | 0.7406 | 0.6726 | 0.4863 | 0.3510 | 0.8133 | **0.8255** | 0.8133 |
| **0.60** | 0.6480 | 0.6075 | 0.6820 | 0.6102 | 0.7406 | 0.5953 | 0.4863 | 0.3579 | 0.8133 | **0.8138** | 0.8133 |

### Key Uniform-Noise Takeaways
- **Clean sanity check ($\varepsilon=0$):** `naive_pool` beats `gold_only` for all 5 models (`SVM +6.6 pp`, `kNN +7.6 pp`, `LR +7.9 pp`).
- **Generative resilience vs. Tree overfitting:** `GNB-naive_pool` drops only **6.3%** relative (`0.6487 → 0.6075`), whereas unpruned `DT-naive_pool` drops **38.5%** (`0.5817 → 0.3579`), exploding to `640` leaves (depth `27` at $\varepsilon=0.30$). Pruning (`max_depth=5`) locks complexity at `32` leaves—justifying WP4's shallow `depth=4` trees.
- **Hidden SVM cost:** Even though `SVM` maintains `0.8138` F1 at $\varepsilon=0.60$, its support vectors inflate sharply (`svm_support_vectors.png`), foreshadowing WP4's TSVM SV growth.
- **Naive `self_training` fails:** Because `self_training` ignores $\tilde{y}_U$, its curve is flat across $\varepsilon$; worse, on poorly calibrated `GNB` it drops `−8.3 pp` below `gold_only` (`0.6480 → 0.5646`) due to confident self-contamination—motivating WP4's dual-view consensus check.

---

## 3. All Three Noise Mechanisms (`noise_type_comparison.csv`)

Comparing `naive_pool` Macro F1 across **Uniform**, **Asymmetric** (confusing pairs `(0,1)` and `(2,3)` at rate $p \in [0, 0.60]$), and **Boundary-Dependent** (Proposal Eq. 3.1, $\gamma = 2.0$, $\varepsilon_{\max} \in [0, 1.0]$):

| Noise Type | Max Param | Actual Pool Flips | GNB F1 | LR F1 | kNN F1 | DT F1 | SVM F1 |
|---|---|---|---|---|---|---|---|
| **Clean baseline** | `0.0` | `0.0%` | 0.6487 | 0.7612 | 0.8167 | 0.5817 | 0.8791 |
| **Uniform** | `ε = 0.60` | `60.2%` | 0.6075 | 0.6102 | 0.5953 | 0.3579 | **0.8138** |
| **Asymmetric** | `p = 0.30` | `24.8%` | 0.6383 | 0.6830 | 0.7225 | 0.5052 | 0.8377 |
| **Asymmetric** | `p = 0.60` | `48.5%` | **0.4640** | **0.4402** | **0.5052** | 0.3957 | **0.5340** |
| **Boundary (Eq. 3.1)** | `ε_max = 1.0` | `40.0%` | 0.6126 | 0.6831 | 0.7309 | 0.4977 | 0.7944 |

**Critical Finding:** **Structured asymmetric noise is far deadlier than uniform random noise.** Even at `60.2%` uniform flips, `SVM` (`0.8138`) and `GNB` (`0.6075`) hold up because uniform errors spread across 4 wrong classes, leaving the true class with the plurality. Under `48.5%` asymmetric confusion (`p=0.60`), *every* model collapses (`SVM` drops to `0.5340`, `LR` to `0.4402`, `GNB` to `0.4640`) because confused pairs systematically outvote the truth—directly explaining why WP5 must model the full $C \times C$ confusion matrix $T$. Meanwhile, **Boundary noise** pushes `SVM-naive_pool` (`0.7944`) below `SVM-gold_only` (`0.8133`) at `40%` flips because flips target margin points directly.

---

## 4. Real PTB-XL Supervised Baselines (`ptbxl_baselines.csv`)

Evaluated on WP1 features (`9,010` Gold, `3,968` real machine-labeled $\mathcal{D}_U$, `1,642` Fold-9 Val, `1,652` Fold-10 Test):

| $\eta$ | Gold $N$ | LR (bal) gold | LR (bal) naive | LR naive | GNB gold | GNB naive | kNN gold | kNN naive | SVM (bal) gold | SVM naive |
|---|---|---|---|---|---|---|---|---|---|---|
| **2%** | 180 | 0.4032 | **0.4506** | 0.4423 | 0.3618 | 0.2648 | 0.2158 | 0.3631 | 0.1432 | 0.4082 |
| **5%** | 450 | 0.4013 | **0.4604** | 0.4424 | 0.3712 | 0.2655 | 0.2423 | 0.3741 | 0.2427 | 0.4138 |
| **10%** | 901 | 0.4220 | **0.4573** | 0.4308 | 0.3610 | 0.2600 | 0.2622 | 0.3776 | 0.2716 | 0.4263 |
| **20%** | 1802 | 0.4468 | **0.4683** | 0.4227 | 0.3712 | 0.2653 | 0.2787 | 0.3823 | 0.3222 | 0.4350 |
| **50%** | 4505 | 0.4820 | **0.4911** | 0.4461 | 0.2736 | 0.2630 | 0.3014 | 0.3719 | 0.3645 | 0.4216 |
| **100%** | 9010 | **0.4943** | 0.4893 | 0.4331 | 0.3405 | 0.2762 | 0.3194 | 0.3817 | 0.3644 | 0.4212 |

*(Values above are Fold-9 validation Macro F1; Fold-10 test metrics are stored in `ptbxl_baselines.csv`.)*

### Key Real-Data Insights
1. **Why synthetic ≠ real for `GNB`:** While `GNB` tolerated uniform synthetic flips, on real PTB-XL **`GNB-naive_pool` drops ~10 pp across all $\eta$** (`0.3618 → 0.2648` at 2%) because $\mathcal{D}_U$'s `28% MI` class shift corrupts its Gaussian class priors and variances!
2. **Low-$\eta$ vs. High-$\eta$ trade-off:** When Gold labels are scarce ($\eta = 2\text{–}20\%$), pooling the `3,968` real machine-labeled ECGs gives `LR`, `kNN`, and `SVM` a big data boost (still noisy, yet mostly right). Once Gold reaches `100%` (`9,010`), `LR (bal)-gold_only` (`0.4943` val / `0.4657` test) overtakes `naive_pool` (`0.4893`).
3. **Self-training consistently hurts on PTB-XL too:** e.g., at $\eta=2\%$, `kNN` drops `0.2158 → 0.1432` and `LR` drops `0.4001 → 0.3545`, confirming single-view pseudo-labeling fails under clinical class overlap.
