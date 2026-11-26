# WP2 – Synthetic Generator & Supervised Baselines
**Person:** Shaurya Suman (2024A7PS0589G)

---

## What This WP Does

WP2 provides two things every other WP depends on:

1. **A synthetic benchmark dataset** – controllable noise, known ground truth, used to validate WP3–WP5 before touching real ECG data.
2. **Five supervised baseline classifiers** – the reference performance floor that semi-supervised methods must beat.

---

## Files in This Folder

| File | Purpose |
|------|---------|
| `run_wp2.py` | **Entry point** |
| `synthetic_generator.py` | Dataset generation + three noise injection functions |
| `baselines.py` | Five classifiers (GNB, LR, kNN, DT, SVM) with three training modes |
| `README.md` | This file |

---

## How to Run

### Prerequisites

Run WP1 first if you want to use PTB-XL features:
```bash
cd wp1_data_pipeline
python run_wp1.py --data_path D:\ml-project\dataset --out_dir ..\outputs\wp1
```

### Synthetic mode (no PTB-XL needed, great for quick testing)

```bash
cd wp2_synthetic_baselines
python run_wp2.py --mode synthetic --out_dir ..\outputs\wp2
```

### PTB-XL mode

```bash
python run_wp2.py --mode ptbxl \
    --features_path ..\outputs\wp1\features.npz \
    --labels_path   ..\outputs\wp1\labels.npz   \
    --out_dir       ..\outputs\wp2
```

### All mode (runs both synthetic experiments and PTB-XL baselines)

```bash
python run_wp2.py --mode all --out_dir ..\outputs\wp2
```

---

## Implementation Guide

### Step 1 – `synthetic_generator.py`

**`generate_manifold()`**
- Use `sklearn.datasets.make_classification` with `n_informative=10`, `n_redundant=5`, `n_features=50`, `n_classes=5`, `n_clusters_per_class=1`.
- Scale by a random projection matrix to make classes non-linearly separable.

**`inject_uniform_noise(y, epsilon)`**
- For each label, with probability `epsilon`, replace it with a uniform draw from the other C-1 classes.
- Use `np.random.default_rng(seed)` for reproducibility.

**`inject_asymmetric_noise(y, T)`**
- Build a default T that confuses class pairs (0,1) and (2,3) with probability 0.3.
- For each sample, draw the noisy label from `Categorical(T[y[i], :])`.

**`inject_boundary_noise(y, X, epsilon_max, gamma)`**
- Train a quick `LogisticRegression` on (X, y) to get class probabilities.
- For sample i with true label y\*, compute:
  `margin = P(z=y*|x) - max_{c≠y*} P(z=c|x)`
- Flip probability follows Proposal Eq. 3.1:
  `P(flip) = epsilon_max * exp(-gamma * margin)`
- Sample noisy labels accordingly.

### Step 2 – `baselines.py`

Each class has the same three-mode `fit()` pattern:

```python
def fit(self, X_L, y_L, X_U, y_U_noisy=None):
    if self.mode == "gold_only":
        self._clf.fit(X_L, y_L)
    elif self.mode == "naive_pool":
        X_all = np.vstack([X_L, X_U])
        y_all = np.hstack([y_L, y_U_noisy])
        self._clf.fit(X_all, y_all)
    elif self.mode == "self_training":
        self._clf = self_training_fit(self._clf, X_L, y_L, X_U)
    self._is_fitted = True
    return self
```

The `self_training_fit()` helper in `baselines.py` needs:
1. Fit classifier on (X_L, y_L).
2. Predict probabilities on X_U.
3. Add rows with max probability > threshold to labeled pool.
4. Repeat.

### Step 3 – `run_wp2.py`

Implement `run_breakdown_analysis()`:
1. Loop over epsilon values `[0, 0.15, 0.30, 0.45, 0.60]`.
2. Inject uniform noise into y_U_clean.
3. Train each of the 5 classifiers × 3 modes = 15 models.
4. Evaluate macro F1 on the validation set.
5. Save results to `noise_breakdown.csv`.
6. Plot macro F1 vs ε for each model (one line per model/mode).

**Additional plots to include:**
- SVM support vector count vs. ε (shows margin corruption).
- Decision tree depth vs. ε for `max_depth=None` (unpruned) vs. `max_depth=5` (pruned).

---

## Expected Output Files

```
outputs/wp2/
├── noise_breakdown.csv        ← macro F1 for each model × mode × epsilon (uniform)
├── f1_vs_epsilon.png          ← main comparison plot
├── svm_support_vectors.png    ← SVM inflation analysis
├── tree_depth_vs_epsilon.png  ← DT overfitting analysis
├── noise_type_comparison.csv  ← Uniform vs. Asymmetric vs. Boundary (Eq. 3.1)
├── noise_types_comparison.png ← 3-noise-mechanism comparison plot
├── ptbxl_baselines.csv        ← 3-mode baselines on real PTB-XL across η (val & test)
└── ptbxl_baselines.png        ← PTB-XL gold_only vs. naive_pool across η
```

---

## Key Expected Findings (Proposal §5.2)

- **Naïve Bayes** degrades more gradually under noise (global density estimate averages out errors).
- **SVM** degrades sharply because mislabeled boundary points become support vectors.
- **Decision Tree (unpruned)** overfits most: depth and leaf count grow with ε.
- **Self-training** sometimes outperforms gold-only when ε is low, but hurts when ε is high (confident wrong predictions self-contaminate the labeled pool).
- At ε = 0, `naive_pool` ≥ `gold_only` for all models (more data helps when labels are clean).

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `NotImplementedError` | Implement the TODO sections |
| Self-training is very slow | Reduce max_iter to 5 and threshold to 0.95 |
| `generate_manifold` returns too-easy data | Reduce `n_informative` or increase `class_sep` parameter |
