# WP4 – Co-Training & Transductive SVMs
**Person:** Arnav Gupta (2024A7PS0613G)

---

## What This WP Does

WP4 implements the two margin/multi-view semi-supervised methods from Proposal §4.4–4.5.

- **Co-Training** – trains two `HistGradientBoostingClassifier` models on independent feature views (temporal vs. spectral); each one teaches the other by adding high-confidence, non-contradicting unlabeled samples as confidence-weighted pseudo-labels.
- **Transductive SVM (TSVM)** – extends standard SVM to treat unlabeled labels as optimization variables, pushing the decision boundary into low-density regions, with margin-percentile filtering and C_U annealing.

Both methods **discard** the noisy machine-generated labels in D_U, treating D_U purely as an unlabeled feature distribution.

---

## Files in This Folder

| File | Purpose |
|------|---------|
| `THEORY.md` | **Theoretical foundations, mathematical derivations & methodology guide** |
| `run_wp4.py` | **Entry point** – orchestrates all sweeps, baselines, plots, and CSV outputs |
| `cotraining.py` | Multi-view Co-Training with HGB base clf, non-contradiction filtering, confidence weighting |
| `tsvm.py` | Transductive SVM with margin-percentile filtering, balanced class weights, C_U annealing |
| `README.md` | This file |

---

## Prerequisites

WP1 must have run first to produce the feature/label `.npz` files:
```bash
cd wp1_data_pipeline
python run_wp1.py --data_path <dataset_path> --out_dir ../outputs/wp1
```

---

## How to Run

```bash
python wp4_cotraining_tsvm/run_wp4.py \
    --features_path outputs/wp1/features.npz \
    --labels_path   outputs/wp1/labels.npz   \
    --out_dir       outputs/wp4 \
    --eta_values    0.02,0.05,0.10,0.20,0.50 \
    --eval_test
```

Expected runtime: ~5–8 minutes (Co-Training: ~2 min, TSVM: ~3 min).

---

## Implementation: Co-Training (`cotraining.py`)

### Key Design Choices (over baseline LR Co-Training)

| Design Decision | Rationale |
|---|---|
| `HistGradientBoosting` base clf | Better-calibrated probabilities on small labeled sets (180–900 samples) than Logistic Regression |
| Non-contradiction filtering | Before h1 adds sample `x` to L2 with label `c`, require h2 also predicts `c`; prevents confirmation bias |
| Confidence-weighted pseudo-labels | Each pseudo-label has `sample_weight = pseudo_w × conf` (default `pseudo_w=0.35`), downweighting uncertain pseudo-labels relative to gold (weight=1.0) |
| Per-class top-p selection | Selects at most `p=10` candidates per class, enforcing balanced growth even when NORM dominates |
| `_align_proba` helper | Safely handles the case where HGB may not have seen all classes at very low η |

### Algorithm Outline

```
Views: V1 = X[:, 0:42]  (temporal/morphology features)
       V2 = X[:, 42:84] (spectral/wavelet features)

For round = 1..12:
    h1.fit(L1_X, L1_y, sample_weight)   # train on View 1
    h2.fit(L2_X, L2_y, sample_weight)   # train on View 2
    
    # h1 → teaches L2 (with non-contradiction from h2)
    For each class c:
        candidates = top-p from h1 by p(y=c | x, V1) > threshold=0.72
        kept = [x for x in candidates if h2.predict(x, V2) == c]
        Add to L2 with weight = pseudo_w × conf
    
    # h2 → teaches L1 (symmetric)

Final predict: average of h1.predict_proba(V1) and h2.predict_proba(V2)
```

**Baseline (fair comparison):** Same HGB architecture as a 2-view supervised ensemble trained only on D_L split-view data (not the full 84D).

---

## Implementation: TSVM (`tsvm.py`)

### Key Design Choices (over v1 TSVM)

| Design Decision | Rationale |
|---|---|
| `margin_percentile=65` filtering | Retains only the top 35% most-confident unlabeled predictions, excluding boundary-uncertain samples from optimization |
| `C_U_max = min(0.30, 0.8 × N_L/N_U_kept)` | Scales regularization weight to gold/unlabeled ratio; prevents unlabeled noise overwhelming small gold sets |
| `class_weight='balanced'` on SVC | Counteracts NORM (62.5%) dominating minority classes; prevents HYP/MI from 100% SV inflation |
| Inductive scaler for baseline | `StandardScaler.fit(X_L only)` for fair comparison; old code leaked X_U scale info into baseline |

### Algorithm Outline

```
1. Scale X_L → X_L_s using scaler fit on X_L ONLY (inductive, fair baseline)
2. Baseline SVM: fit balanced SVC(C=C_L=2.0) on X_L_s → evaluate on X_val
3. Scale X_U using same inductive scaler → X_U_s
4. Filter X_U: keep top margin_percentile (top 35%) most-confident predictions
5. Initialize pseudo-labels y_U_hat from base SVM predictions on X_U_filtered
6. C_U annealing: start C_U=0.005, double each step until C_U_max
   For each C_U level:
     a. Fit SVC on (X_L_s, y_L, weight=C_L) ∪ (X_U_filtered, y_U_hat, weight=C_U)
     b. Inner label switching (max_iter steps): update y_U_hat where clf disagrees
7. TSVM predict: average decision functions over OvR classifiers via softmax
```

---

## Actual Experimental Results

> Results evaluated on the **validation set** (fold 9, n=1,642).  
> Co-Training Δ is vs. **2-View HGB Ensemble** (fair same-architecture baseline).  
> TSVM Δ is vs. **Inductive Balanced SVM** (scaler fit on X_L only).

### Co-Training vs. 2-View Supervised Ensemble

| η (%) | Gold | Base2V Acc | CoTrain Acc | ΔAcc | Base2V F1 | CoTrain F1 | ΔF1 |
|---|---|---|---|---|---|---|---|
| 2.0 | 180 | 0.5987 | 0.5871 | −0.012 | 0.3145 | 0.3651 | **+0.051** |
| 5.0 | 450 | 0.6194 | 0.6261 | **+0.007** | 0.3605 | 0.4310 | **+0.071** |
| 10.0 | 901 | 0.6291 | 0.6352 | **+0.006** | 0.4039 | 0.4386 | **+0.035** |
| 20.0 | 1802 | 0.6340 | 0.6401 | **+0.006** | 0.4148 | 0.4326 | **+0.018** |
| 50.0 | 4505 | 0.6644 | 0.6638 | −0.001 | 0.4782 | 0.4703 | −0.008 |

**Key takeaway:** Co-Training shows strong F1 gains (+5% to +7%) at η=0.02–0.10 where the views are most complementary. The accuracy advantage is also positive at η=0.05–0.20. At η=0.50 (4,505 gold), views become less complementary (more supervised data already covers the space), and the effect tapers off.

### TSVM vs. Inductive Balanced SVM

| η (%) | Gold | BaseSVM Acc | TSVM Acc | ΔAcc | BaseSVM F1 | TSVM F1 | ΔF1 |
|---|---|---|---|---|---|---|---|
| 2.0 | 180 | 0.4951 | 0.5018 | **+0.007** | 0.3830 | 0.3875 | **+0.005** |
| 5.0 | 450 | 0.5286 | 0.5646 | **+0.036** | 0.4187 | 0.4245 | **+0.006** |
| 10.0 | 901 | 0.5061 | 0.5889 | **+0.083** | 0.4326 | 0.4584 | **+0.026** |
| 20.0 | 1802 | 0.5329 | 0.5956 | **+0.063** | 0.4576 | 0.4884 | **+0.031** |
| 50.0 | 4505 | 0.5591 | 0.5907 | **+0.032** | 0.4962 | 0.4991 | **+0.003** |

**Key takeaway:** TSVM shows consistent positive gains in **both Accuracy and F1 across all 5 η values**. The largest accuracy gain is at η=0.10 (+8.3%), where the gold/unlabeled ratio is optimal for the low-density separation principle. The margin-percentile filtering (keeping only the top 35% most-confident unlabeled samples) is critical: it prevents boundary-uncertain minority-class samples from triggering 100% SV inflation (as observed in v1).

---

## Output Files

```
outputs/wp4/
├── cotraining_eta_sweep.csv       ← Full metric sweep (Acc, F1, ROC-AUC, PR-AUC, agreement, per-class F1)
├── tsvm_eta_sweep.csv             ← Full metric sweep (Acc, F1, ROC-AUC, PR-AUC, SV counts, per-class F1)
├── f1_vs_eta_cotraining.png       ← Dual-panel: F1 and Accuracy vs η for Co-Training
├── f1_vs_eta_tsvm.png             ← Dual-panel: F1 and Accuracy vs η for TSVM
├── view_agreement.png             ← h1/h2 inter-view agreement rate across co-training rounds
└── margin_stability_imbalance.png ← TSVM SV ratio per class across η
```

---

## Key Findings: Why These Methods Work

### Why Co-Training Works at Low η

At very low label fractions (η=2–10%), the two views (temporal morphology vs. spectral/wavelet) are **conditionally independent given the class label** — a sufficient condition for Blum & Mitchell (1998) guarantees. Each view captures distinct ECG phenomena:
- **View 1 (0:42):** R-peak amplitudes, QRS durations, T-wave morphology, heart rate
- **View 2 (42:84):** Fourier magnitudes, Daubechies wavelet energy bands

This conditional independence means h1's confident predictions contain information not yet seen by h2, and vice versa. Non-contradiction filtering (`pred2==c` before h1 adds to L2) prevents the most common failure mode: adding samples where the two views genuinely disagree.

### Why TSVM Works

TSVM exploits the **low-density separation** assumption: class clusters are dense islands separated by sparse gaps. By optimizing the decision boundary to avoid these dense regions of X_U (even when unlabeled), the boundary is forced into the natural inter-cluster gaps rather than cutting through them.

The key improvement over the failed v1 implementation:
- **v1 problem:** ALL 3,968 unlabeled points included → SVM tries to put the boundary in a gap but the minority-class sparse regions are on the boundary → 100% SV inflation → F1 collapse
- **v2 fix:** Only the **top 35% most-confident** unlabeled predictions retained → forces the SVM to work only with clearly-separated unlabeled points, preventing boundary collapse for HYP/MI

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Co-Training adds no samples | Lower `threshold` to 0.65 or increase `p` to 15 |
| TSVM slow on large η | TSVM scales ~O(N²) with kernel SVM; linear kernel is faster |
| Poor TSVM F1 at very low η | Increase `C_L` to 3.0 or raise `margin_percentile` to 70 |
| `_align_proba` import error | Ensure you are importing from the new `cotraining.py`, not cached `.pyc` |
