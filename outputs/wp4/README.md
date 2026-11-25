# WP4 Outputs – Co-Training & Transductive Support Vector Machines
**Author:** Arnav Gupta (2024A7PS0613G)  
**Work Package:** WP4 – Co-Training & Transductive SVMs  
**Date:** November 2026  
**Course:** BITS F464 – Machine Learning, Sem 1 2026–2027  
**Instructor:** Prof. Anand Narasimhamurthy  

---

## 1. Overview and Deliverables

WP4 implements and evaluates two margin- and multi-view-based semi-supervised learning methods that **discard** untrusted machine labels in $\mathcal{D}_U$ and exploit unlabeled feature distributions:

1. **Multi-View Co-Training** (`cotraining.py`):
   - **View 1 (Temporal / Morphological)**: Feature indices `0:42` (per-lead amplitude means/stds, Heart Rate Variability metrics RR-mean, RR-std, RMSSD, QRS range).
   - **View 2 (Spectral / Wavelet)**: Feature indices `42:84` (Welch Power Spectral Density bands 0.5–4 Hz, 4–15 Hz, 15–40 Hz, spectral entropy, roll-off, Daubechies db4 sub-band wavelet energies).
   - Paired classifiers ($h_1, h_2$) iteratively label high-confidence unlabeled samples for each other for up to 12 rounds, with a cross-view agreement check.

2. **Transductive Support Vector Machine (TSVM)** (`tsvm.py`):
   - Multi-class formulation via One-vs-Rest (OvR) decision functions.
   - Dual-objective optimization treating unlabeled predictions $\hat{y}_j \in \{0, \dots, 4\}$ as latent optimization variables.
   - Margin-filtered pseudo-labeling and iterative label switching with $C_U$ annealing (starts at 0.05; capped at 0.30 and further bounded by the gold-to-unlabeled ratio).

### Generated Files in `outputs/wp4/`

| File | Description |
|---|---|
| `cotraining_eta_sweep.csv` | Co-Training vs. Baselines Macro F1, Per-Class F1, ROC-AUC, PR-AUC, and agreement rates vs. $\eta \in \{0.02, 0.05, 0.10, 0.20, 0.50\}$ |
| `tsvm_eta_sweep.csv` | TSVM vs. Supervised SVM Macro F1, Per-Class F1, ROC-AUC, PR-AUC, and support vector counts per class vs. $\eta$ |
| `f1_vs_eta_cotraining.png` | Validation Macro F1 comparison: Co-Training vs. Full Supervised Baseline vs. Single-View Baselines (V1 & V2) |
| `f1_vs_eta_tsvm.png` | Validation Macro F1 and total support vector growth comparison: TSVM vs. Supervised SVM Baseline |
| `cotraining_f1_only.png` | Presentation crop of the Co-Training macro-F1 panel, without the accuracy panel |
| `tsvm_f1_only.png` | Presentation-only TSVM vs. gold-only SVM macro-F1 comparison |
| `tsvm_per_class_f1_eta10.png` | Side-panel comparison of per-class validation F1 at 10% gold, generated from the current sweep CSV |
| `view_agreement.png` | Inter-view classifier agreement rate (%) dynamics across up to 12 Co-Training rounds for each $\eta$ |
| `margin_stability_imbalance.png` | Analysis of margin stability, support vector inflation, and per-class performance degradation under severe class imbalance |
| `README.md` | This technical analysis report |

---

## 2. Experimental Results & Data Tables

Experiments were conducted on the official **PTB-XL** 10-fold patient-stratified split:
- **Clean Gold Set ($\mathcal{D}_L$)**: 9,010 records (cardiologist-verified at 100% confidence, folds 1–8).
- **Untrusted Pool ($\mathcal{D}_U$)**: 3,968 records (machine-generated or unvalidated, folds 1–8).
- **Validation Set**: 1,642 records (fold 9).
- **Held-Out Test Set**: 1,652 records (fold 10, clean).

### 2.1 Multi-View Co-Training Results (`cotraining_eta_sweep.csv`)

| $\eta$ (%) | Gold $N$ | CoTrain Macro F1 | Base Full F1 | View 1 F1 | View 2 F1 | CoTrain ROC-AUC | CoTrain PR-AUC | Final Agreement | Test Macro F1 | Test ROC-AUC |
|---|---|---|---|---|---|---|---|---|---|---|
| **2.0%** | 180 | **0.3651** | 0.3448 | 0.2770 | 0.3548 | 0.7424 | 0.3950 | 80.47% | 0.3519 | 0.7295 |
| **5.0%** | 450 | **0.4310** | 0.3736 | 0.3376 | 0.3918 | 0.7888 | 0.4788 | 77.85% | 0.3969 | 0.7756 |
| **10.0%** | 901 | **0.4386** | 0.4378 | 0.3479 | 0.4231 | 0.8245 | 0.5391 | 78.05% | 0.3953 | 0.8057 |
| **20.0%** | 1802 | **0.4326** | 0.4576 | 0.3754 | 0.4502 | 0.8331 | 0.5524 | 77.92% | 0.4229 | 0.8214 |
| **50.0%** | 4505 | **0.4703** | 0.5159 | 0.4045 | 0.4833 | 0.8499 | 0.5868 | 77.42% | 0.4266 | 0.8337 |

#### Per-Class F1 for Co-Training vs. Supervised Two-View Baseline
- **At $\eta = 0.02$ (180 Gold Records)**:
  - **Myocardial Infarction (MI)**: Co-Training achieves **0.3632** vs. Baseline **0.2115** (**+0.1517 F1 gain**).
  - **Conduction Disturbance (CD)**: Co-Training achieves **0.4365** vs. Baseline **0.4532**.
  - **Normal ECG (NORM)**: Co-Training and Baseline both score **0.7530**.
- **At $\eta = 0.05$ (450 Gold Records)**:
  - **MI**: Co-Training achieves **0.3709** vs. Baseline **0.2967** (**+0.0742 F1 gain**).
  - **NORM**: Co-Training achieves **0.7735** vs. Baseline **0.7648** (**+0.0087 F1 gain**).

### 2.2 Transductive SVM Results (`tsvm_eta_sweep.csv`)

| $\eta$ (%) | Gold $N$ | TSVM Macro F1 | Base SVM F1 | TSVM Total SVs | Base SVM SVs | TSVM ROC-AUC | TSVM PR-AUC | Test Macro F1 | Test ROC-AUC |
|---|---|---|---|---|---|---|---|---|---|
| **2.0%** | 180 | **0.3875** | 0.3830 | 1,099 | 177 | 0.7389 | 0.3891 | 0.3650 | 0.7057 |
| **5.0%** | 450 | **0.4245** | 0.4187 | 1,216 | 431 | 0.7542 | 0.3978 | 0.4182 | 0.7445 |
| **10.0%** | 901 | **0.4584** | 0.4326 | 1,540 | 848 | 0.7747 | 0.4438 | 0.4407 | 0.7629 |
| **20.0%** | 1802 | **0.4884** | 0.4576 | 2,211 | 1,635 | 0.7984 | 0.4803 | 0.4586 | 0.7810 |
| **50.0%** | 4505 | **0.4991** | 0.4962 | 4,438 | 3,979 | 0.8107 | 0.4847 | 0.4744 | 0.7906 |

---

## 3. Key Findings and Scientific Analysis

### 3.1 Complementarity of Time-Domain vs. Frequency-Domain Views
- **View 2 (Spectral / Wavelet)** outperforms **View 1 (Temporal / Morphology)** at every tested $\eta$ (at $\eta = 0.10$: 0.4231 vs. 0.3479).
- Co-Training exceeds both single views at $\eta = 0.02$–$0.10$, but not at 0.20 or 0.50; the combined model does not win in every label regime.
- Frequency band powers (PSD) and Daubechies wavelet sub-bands capture global rhythm and localized QRS-T wave abnormalities that temporal interval features alone cannot resolve.

### 3.2 Dynamics of Inter-View Agreement Rate
- Final inter-view agreement on the untrusted pool ranges from **77.42% to 80.47%** in the current sweep.
- Agreement is an internal consistency diagnostic, not label accuracy or proof that the theoretical assumptions hold; it need not increase monotonically.

### 3.3 The Impact of Class Imbalance on Semi-Supervised Margins
- At $\eta=0.10$, TSVM improves NORM and CD F1 over its gold-only SVM baseline (`0.646 → 0.739`, `0.428 → 0.515`), while MI and STTC dip slightly and HYP is nearly unchanged.
- TSVM uses 1,540 support vectors at $\eta=0.10$ vs. 848 for the baseline. This indicates increased boundary complexity, but support-vector count alone does not establish margin collapse or per-class support-vector inflation.
- Co-Training caps candidate selection per class (`p=10` per view and round), which limits majority-class domination during pseudo-label selection; it does not guarantee class-balanced final predictions.

---

## 4. Summary Table for Downstream Comparison (WP5)

| Strategy | WP | Key Mechanism | Best Val F1 ($\eta=0.10$) | Val ROC-AUC | Key Vulnerability |
|---|---|---|---|---|---|
| **Co-Training** | WP4 | Discard noisy labels; paired view self-teaching | **0.4386** | **0.8245** | Semantic drift; gains vary with gold fraction |
| **Transductive SVM** | WP4 | Discard noisy labels; low-density margin push | **0.4584** | **0.7747** | Modest, class-dependent gains; increased support-vector count |
| **Supervised Baseline (LR)** | WP2 | Train on gold labels only ($\mathcal{D}_L$) | 0.4279 | 0.7946 | Ignores 3,968 unlabeled/untrusted records |
| **Supervised Baseline (SVM)**| WP2 | Train on gold labels only ($\mathcal{D}_L$) | 0.2621 | 0.7479 | Majority class bias under low $\eta$ |
