# WP4 Theoretical Foundations & Methodology Guide
**Work Package 4: Multi-View Co-Training & Transductive Support Vector Machines**  
**Course:** BITS F464 – Machine Learning, First Semester 2026–2027  
**Author:** Arnav Gupta (2024A7PS0613G)  
**Instructor:** Prof. Anand Narasimhamurthy  

---

## Table of Contents
1. [Introduction and Project Context](#1-introduction-and-project-context)
2. [The "Discard vs. Correct" Paradigm](#2-the-discard-vs-correct-paradigm)
3. [Theory of Multi-View Co-Training](#3-theory-of-multi-view-co-training)
   - 3.1 [Core Assumptions (Blum & Mitchell 1998)](#31-core-assumptions-blum--mitchell-1998)
   - 3.2 [ECG Feature Splitting: Temporal vs. Spectral Views](#32-ecg-feature-splitting-temporal-vs-spectral-views)
   - 3.3 [Mathematical Algorithm & Pseudo-Code](#33-mathematical-algorithm--pseudo-code)
   - 3.4 [Convergence & Inter-View Agreement Dynamics](#34-convergence--inter-view-agreement-dynamics)
   - 3.5 [Failure Modes: Confirmation Bias & Semantic Drift](#35-failure-modes-confirmation-bias--semantic-drift)
4. [Theory of Transductive Support Vector Machines (TSVM)](#4-theory-of-transductive-support-vector-machines-tsvm)
   - 4.1 [The Low-Density Separation Assumption](#41-the-low-density-separation-assumption)
   - 4.2 [Mathematical Formulation (Vapnik 1998)](#42-mathematical-formulation-vapnik-1998)
   - 4.3 [Optimization Complexity & $C_U$ Annealing Schedule](#43-optimization-complexity--c_u-annealing-schedule)
   - 4.4 [Iterative Label Switching Mechanism](#44-iterative-label-switching-mechanism)
   - 4.5 [Multi-Class Extension via One-vs-Rest](#45-multi-class-extension-via-one-vs-rest)
5. [In-Depth Analysis: Margin Stability under Severe Class Imbalance](#5-in-depth-analysis-margin-stability-under-severe-class-imbalance)
   - 5.1 [The Imbalance Geometry in PTB-XL](#51-the-imbalance-geometry-in-ptb-xl)
   - 5.2 [Support Vector Inflation Phenomenon ($|SV_c| / N_c \to 1.0$)](#52-support-vector-inflation-phenomenon-sv_c--n_c-to-10)
   - 5.3 [Why Co-Training Resists Imbalance Better than TSVM](#53-why-co-training-resists-imbalance-better-than-tsvm)
6. [Summary Comparison & Role in Final Evaluation](#6-summary-comparison--role-in-final-evaluation)

---

## 1. Introduction and Project Context

In standard supervised machine learning, algorithms assume access to a large, clean, independently and identically distributed (i.i.d.) dataset $\mathcal{D} = \{(\mathbf{x}_i, y_i)\}_{i=1}^N$. In clinical medicine—and electrocardiology specifically—this assumption fails dramatically:
1. **Label Scarcity**: Expert human annotations (cardiologists reading 12-lead ECGs) are scarce, expensive, and time-consuming. Only a small fraction of records form a verified **Gold Set** ($\mathcal{D}_L$).
2. **Structured Machine Noise**: Modern hospitals use automated algorithmic software to generate preliminary ECG interpretations. While voluminous, this **Untrusted Pool** ($\mathcal{D}_U$) suffers from systematic diagnostic biases, sensor artifacts (baseline wander, electrode motion, high-frequency muscle noise), and imperfect heuristics.

WP4 investigates **two classical semi-supervised learning paradigms** that handle this scenario by explicitly **discarding** the noisy machine-generated labels in $\mathcal{D}_U$, treating $\mathcal{D}_U$ purely as an unlabeled feature distribution:
- **Multi-View Co-Training**: Exploits feature-space factorization into conditionally independent representations.
- **Transductive Support Vector Machines (TSVM)**: Exploits cluster/manifold density structure by pushing the decision boundary into low-density regions.

---

## 2. The "Discard vs. Correct" Paradigm

A central research question of this project (Proposal §5.3) is:

> *When is it better to **discard** untrusted labels and apply semi-supervised manifold/margin learning, versus **keeping and correcting** noisy labels via latent-variable probabilistic modeling?*

```
                       ┌──────────────────────────────────────────────┐
                       │   Untrusted Machine-Labeled Pool (D_U)       │
                       │     Features X_U  +  Noisy Labels y~_U       │
                       └──────────────────────┬───────────────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      │                                               │
             [ DISCARD PARADIGM ]                            [ CORRECT PARADIGM ]
           (WP3 Graph LP & WP4 Co-Train/TSVM)                  (WP5 Latent-Noise EM)
                      │                                               │
         Discard y~_U completely.                        Keep y~_U as noisy observations.
         Treat X_U as unlabeled points.                 Model true class z as latent variable.
         Exploit feature geometry:                       Estimate transition matrix:
           • Graph affinities (WP3)                        T_ck = P(y~ = k | z = c)
           • Multi-view consensus (WP4)                  Iterate E-step & M-step to
           • Low-density margins (WP4)                   recover clean posterior labels.
```

WP4 represents the two margin- and multi-view-based pillars of the **Discard Paradigm**.

---

## 3. Theory of Multi-View Co-Training

Co-Training, introduced by Blum and Mitchell in 1998, is one of the foundational algorithms in semi-supervised learning. It transforms the learning problem from a single model operating on an isolated feature space into a cooperative game between two paired models operating on distinct representations.

### 3.1 Core Assumptions (Blum & Mitchell 1998)

Co-Training theoretically guarantees that an unlabeled pool can be leveraged to boost classification accuracy provided that two conditions hold:

#### Assumption 1: Feature Sufficiency (Individual Completeness)
The input feature vector $\mathbf{x} \in \mathbb{R}^d$ can be partitioned into two distinct sub-vectors (views), $\mathbf{x} = (\mathbf{x}^{(1)}, \mathbf{x}^{(2)})$, such that each view alone contains sufficient mutual information to predict the target class $y \in \{0, \dots, C-1\}$:
$$I(y; \mathbf{x}^{(1)}) \approx I(y; \mathbf{x}) \quad \text{and} \quad I(y; \mathbf{x}^{(2)}) \approx I(y; \mathbf{x})$$
That is, an optimal predictor $f_1^*(\mathbf{x}^{(1)})$ trained solely on View 1 has a low Bayes error rate, and an optimal predictor $f_2^*(\mathbf{x}^{(2)})$ trained solely on View 2 also has a low Bayes error rate.

#### Assumption 2: Conditional Independence Given the Label
Given the true class label $y$, the feature distributions in View 1 and View 2 are statistically independent:
$$P(\mathbf{x}^{(1)}, \mathbf{x}^{(2)} \mid y) = P(\mathbf{x}^{(1)} \mid y) \cdot P(\mathbf{x}^{(2)} \mid y)$$
This assumption ensures that the errors made by classifier $h_1$ on View 1 are uncorrelated with the errors made by classifier $h_2$ on View 2. Consequently, when $h_1$ predicts a sample with high confidence, its prediction acts as an informative, conditionally independent label for $h_2$, and vice versa.

---

### 3.2 ECG Feature Splitting: Temporal vs. Spectral Views

In clinical cardiology, 12-lead ECGs naturally exhibit a duality between **time-domain morphology** and **frequency-domain spectral dynamics**. WP1's 84-dimensional feature extractor explicitly constructed this split:

```
                            84-Dimensional ECG Feature Vector
  ┌────────────────────────────────────────┬────────────────────────────────────────┐
  │         View 1: Indices 0 to 41        │        View 2: Indices 42 to 83        │
  │     Temporal & Morphological (42 D)    │      Frequency & Wavelet (42 D)        │
  ├────────────────────────────────────────┼────────────────────────────────────────┤
  │ • Per-lead mean amplitude (12 leads)   │ • Welch PSD Band 1: 0.5–4.0 Hz (Delta) │
  │ • Per-lead std amplitude  (12 leads)   │ • Welch PSD Band 2: 4.0–15.0 Hz (Theta)│
  │ • RR Interval Statistics:              │ • Welch PSD Band 3: 15.0–40.0 Hz(Beta) │
  │     - Mean RR interval                 │ • Spectral Entropy                     │
  │     - Std RR interval                  │ • Spectral Roll-off                    │
  │     - RMSSD (vagal tone metric)        │ • Daubechies (db4) Wavelet sub-band    │
  │ • QRS amplitude peak-to-peak range     │   energies across multi-resolution     │
  │ • Zero-crossing rate                   │   decomposition levels                 │
  │ • Hjorth Activity, Mobility, Complexity│                                        │
  └────────────────────────────────────────┴────────────────────────────────────────┘
```

#### Why This Split Satisfies Conditional Independence:
- **View 1 (Temporal)** captures local waveform geometry: the height of the R-peak, the duration of the PR and QT intervals, and beat-to-beat rhythm irregularity.
- **View 2 (Spectral)** captures global energy distributions: the power spectral density across physiological frequency bands and localized time-frequency wavelets.
- While both reflect the underlying pathology (e.g., Myocardial Infarction causes ST-segment elevation in View 1 and alters high-frequency wavelet energy in View 2), measurement noise or lead artifacts affecting localized amplitude peaks rarely affect the spectral energy distribution in the exact same mathematical way.

---

### 3.3 Mathematical Algorithm & Pseudo-Code

Let $\mathcal{D}_L = \{(\mathbf{x}_i, y_i)\}_{i=1}^{N_L}$ be the clean Gold Set and $\mathcal{D}_U = \{\mathbf{x}_j\}_{j=1}^{N_U}$ be the Untrusted Pool with machine labels discarded.

```
Algorithm: Multi-View Co-Training for Multi-Class ECG Classification
─────────────────────────────────────────────────────────────────────────────
Input : Labeled set D_L, Unlabeled set D_U, rounds T, pool size p, threshold tau
Output: Final ensemble hypothesis H(x) = argmax_c [ (P_1(c|x^(1)) + P_2(c|x^(2))) / 2 ]

1. Initialize labeled pools:
     L_1 ← { (x_i^(1), y_i) : (x_i, y_i) ∈ D_L }
     L_2 ← { (x_i^(2), y_i) : (x_i, y_i) ∈ D_L }
2. Initialize remaining unlabeled indices: U_rem ← {1, 2, ..., N_U}
3. Instantiate base estimators h_1, h_2 (Multinomial Logistic Regression with StandardScaler)

4. For round t = 1, 2, ..., T do:
     a. If U_rem is empty, break.
     b. Fit h_1 on L_1.
     c. Fit h_2 on L_2.
     
     d. Predict class probabilities on remaining unlabeled samples:
          P_1(c | x_j^(1)) for j ∈ U_rem, c ∈ {0, ..., C-1}
          P_2(c | x_j^(2)) for j ∈ U_rem, c ∈ {0, ..., C-1}

     e. Candidate selection for View 1 teaching View 2:
          For each class c ∈ {0, ..., C-1}:
             Select top-p samples j ∈ U_rem maximizing P_1(c | x_j^(1))
             subject to P_1(c | x_j^(1)) ≥ tau.
             Collect into S_1.

     f. Candidate selection for View 2 teaching View 1:
          For each class c ∈ {0, ..., C-1}:
             Select top-p samples j ∈ U_rem maximizing P_2(c | x_j^(2))
             subject to P_2(c | x_j^(2)) ≥ tau.
             Collect into S_2.

     g. If S_1 ∪ S_2 is empty, break (no high-confidence samples remain).

     h. Add pseudo-labeled samples to the opposite pools:
          L_2 ← L_2 ∪ { (x_j^(2), c) : j ∈ S_1, c = argmax P_1 }
          L_1 ← L_1 ∪ { (x_j^(1), c) : j ∈ S_2, c = argmax P_2 }

     i. Remove added samples: U_rem ← U_rem \ (S_1 ∪ S_2).

5. Final refit of h_1 on L_1 and h_2 on L_2.
6. Return H(x).
─────────────────────────────────────────────────────────────────────────────
```

---

### 3.4 Convergence & Inter-View Agreement Dynamics

Why does Co-Training converge to an accurate classifier?

Let $A(h_1, h_2)$ denote the **Inter-View Agreement Rate** evaluated over the unlabeled pool $\mathcal{D}_U$:
$$A(h_1, h_2) = \frac{1}{|\mathcal{D}_U|} \sum_{j \in \mathcal{D}_U} \mathbb{I}\left(\arg\max_c P(c \mid \mathbf{x}_j^{(1)}; h_1) = \arg\max_c P(c \mid \mathbf{x}_j^{(2)}; h_2)\right)$$

Blum & Mitchell (1998) and Dasgupta et al. (2001) proved that:
1. **Upper Bound on Generalization Error**: The probability that $h_1$ and $h_2$ simultaneously make an error on an unlabeled sample is strictly bounded by the probability that they disagree:
   $$P(h_1(\mathbf{x}^{(1)}) \ne y \text{ and } h_2(\mathbf{x}^{(2)}) \ne y) \le P(h_1(\mathbf{x}^{(1)}) \ne h_2(\mathbf{x}^{(2)}))$$
2. **Agreement Maximization**: Minimizing the disagreement rate $1 - A(h_1, h_2)$ over unlabeled data drives both hypotheses toward the Bayes optimal classifier, provided the initial labeled set is sufficient to eliminate trivial constant solutions (e.g., predicting all NORM).

In our empirical experiments on PTB-XL, we observe that the agreement rate starts at **72.3%** in Round 0 and monotonically rises to a stable plateau between **82.2% and 84.3%** across all values of $\eta$, visually proving this theoretical convergence.

---

### 3.5 Failure Modes: Confirmation Bias & Semantic Drift

Co-Training is not infallible. Its primary vulnerabilities are:
1. **Semantic Drift**: If classifier $h_1$ makes a high-confidence mistake on a sample near the decision boundary, that false label is permanently added to $h_2$'s training set. In subsequent rounds, $h_2$ fits to this error, reinforces it, and propagates further mislabeled samples back to $h_1$.
2. **Confidence Threshold Sensitivity ($\tau$)**:
   - If $\tau$ is too high ($\tau > 0.90$), Co-Training stops early because few samples exceed the threshold.
   - If $\tau$ is too low ($\tau < 0.65$), noisy pseudo-labels flood the labeled pools, deteriorating performance below the baseline.
   - Setting $\tau = 0.75$ with $p = 5$ per class provided the optimal balance of conservative expansion and steady manifold propagation.

---

## 4. Theory of Transductive Support Vector Machines (TSVM)

While Co-Training relies on multiple representations, Transductive SVM (TSVM), introduced by Vladimir Vapnik (1998) and operationalized by Thorsten Joachims (1999), operates on a single feature space and formalizes the **low-density separation hypothesis**.

### 4.1 The Low-Density Separation Assumption

```
      Standard Inductive SVM (L Only)            Transductive SVM (L + U)
      ───────────────────────────────            ────────────────────────
            +                           +              +               +
               +  \                           +           +       |
                 + \                                        +     |
                    \                                             |  (Margin pushed into
           o         \                               o            |   empty gap between
             o        \   o                            o          |   clusters)
                        o                                o        |   o
                     Boundary cuts                                  o
                     through unlabeled                             Boundary avoids
                     cluster!                                      dense data!
```

- **Inductive SVM** seeks a hyperplane $(\mathbf{w}, b)$ that maximizes the margin solely on labeled points $\mathcal{D}_L$, completely unaware of the data manifold.
- **Transductive SVM** seeks a hyperplane $(\mathbf{w}, b)$ and a set of discrete labels $\hat{\mathbf{y}}_U = (\hat{y}_1, \dots, \hat{y}_{N_U})$ for the unlabeled data such that the separating margin avoids dense regions of *both* labeled and unlabeled data.

---

### 4.2 Mathematical Formulation (Vapnik 1998)

For binary classification $y \in \{-1, +1\}$, the primal TSVM optimization problem is:

$$\min_{\mathbf{w}, b, \hat{\mathbf{y}}_U, \boldsymbol{\xi}, \boldsymbol{\xi}^*} \quad \frac{1}{2} \|\mathbf{w}\|^2 + C_L \sum_{i=1}^{N_L} \xi_i + C_U \sum_{j=1}^{N_U} \xi_j^*$$

subject to the constraints:
$$\begin{aligned}
y_i (\mathbf{w}^T \phi(\mathbf{x}_i) + b) &\ge 1 - \xi_i, \quad &\xi_i \ge 0, \quad &\forall i \in \{1, \dots, N_L\} \\
\hat{y}_j (\mathbf{w}^T \phi(\mathbf{x}_j) + b) &\ge 1 - \xi_j^*, \quad &\xi_j^* \ge 0, \quad &\forall j \in \{1, \dots, N_U\} \\
\hat{y}_j &\in \{-1, +1\}, \quad &&\forall j \in \{1, \dots, N_U\}
\end{aligned}$$

where:
- $\phi(\mathbf{x})$ is the non-linear kernel feature mapping (in our implementation, the Radial Basis Function kernel $\mathcal{K}(\mathbf{x}, \mathbf{x}') = \exp(-\gamma \|\mathbf{x} - \mathbf{x}'\|^2)$).
- $C_L$ is the penalty for misclassifying or violating the margin on clean Gold records.
- $C_U$ is the penalty for violating the margin on unlabeled records with assigned pseudo-labels $\hat{y}_j$.
- $\xi_i$ and $\xi_j^*$ are the slack variables for labeled and unlabeled points, respectively.

---

### 4.3 Optimization Complexity & $C_U$ Annealing Schedule

The primal problem above is a **mixed-integer non-convex quadratic program (MIQP)** because $\hat{y}_j$ are discrete optimization variables. Solving it globally is NP-hard.

If we immediately set $C_U = C_L = 1.0$, the optimizer quickly gets trapped in terrible local minima (e.g., assigning all unlabeled points to $+1$ and placing the hyperplane far away from the data).

To resolve this, Joachims proposed a **deterministic annealing schedule** on the regularization weight $C_U$:
1. Start with an infinitesimally small weight $C_U = 0.005 \ll C_L$. At this stage, the unlabeled points exert negligible influence on the hyperplane, which is primarily guided by the clean Gold set $\mathcal{D}_L$.
2. In each outer iteration, double the weight:
   $$C_U^{(k+1)} = \min\left(2 \cdot C_U^{(k)}, \, C_{U,\max}\right)$$
3. At each intermediate $C_U$ level, solve the continuous SVM problem with sample weights:
   $$w_i = C_L \quad (\forall i \in \mathcal{D}_L), \qquad w_j = C_U \quad (\forall j \in \mathcal{D}_U)$$
4. Run inner label switching to adjust pseudo-labels $\hat{y}_j$ whenever an unlabeled point falls on the wrong side of the margin.
5. As $C_U$ approaches $C_{U,\max} = 0.50$, the margin is gradually forced out of the dense unlabeled clusters without jumping into an unrecoverable local minimum.

---

### 4.4 Iterative Label Switching Mechanism

At each annealing step, the algorithm inspects the unlabeled points under the current decision function $f(\mathbf{x}) = \mathbf{w}^T \phi(\mathbf{x}) + b$.

In our implementation:
1. The classifier computes the predictions $\hat{y}_j^{\text{new}} = \text{sign}(f(\mathbf{x}_j))$.
2. A difference mask is formed: $\mathcal{M} = \{j \in \mathcal{D}_U : \hat{y}_j^{\text{new}} \ne \hat{y}_j^{\text{current}}\}$.
3. If $|\mathcal{M}| > 0$, the pseudo-labels are updated:
   $$\hat{y}_j^{\text{current}} \leftarrow \hat{y}_j^{\text{new}} \quad (\forall j \in \mathcal{M})$$
4. The weighted SVM is re-fit on $\mathcal{D}_L \cup \mathcal{D}_U$.
5. The inner loop repeats up to `max_iter = 3` times before advancing $C_U$.

---

### 4.5 Multi-Class Extension via One-vs-Rest

PTB-XL requires classifying ECG waveforms into $C = 5$ superclasses:
- `NORM`: Normal ECG
- `MI`: Myocardial Infarction
- `STTC`: ST/T Change
- `CD`: Conduction Disturbance
- `HYP`: Hypertrophy

Standard SVM is fundamentally a binary classifier. To handle 5 classes, we formulate TSVM using the **One-vs-Rest (OvR)** decomposition. For each class $c \in \{0, \dots, 4\}$:
1. An independent binary TSVM separates class $c$ from all other classes.
2. The model outputs a continuous decision function vector $\mathbf{s}(\mathbf{x}) = (s_0(\mathbf{x}), \dots, s_4(\mathbf{x})) \in \mathbb{R}^5$.
3. To obtain well-calibrated class probability distributions required for ROC-AUC and PR-AUC calculations, we apply numerically stable softmax normalization:
   $$P(y = c \mid \mathbf{x}) = \frac{\exp(s_c(\mathbf{x}) - \max_k s_k(\mathbf{x}))}{\sum_{c'=0}^4 \exp(s_{c'}(\mathbf{x}) - \max_k s_k(\mathbf{x}))}$$

---

## 5. In-Depth Analysis: Margin Stability under Severe Class Imbalance

One of the most significant theoretical contributions of WP4 is uncovering the **geometric failure mode of Transductive SVMs under clinical class imbalance**.

### 5.1 The Imbalance Geometry in PTB-XL

The Gold Set $\mathcal{D}_L$ in PTB-XL has the following severe class disparity:

| Superclass | Clinical Name | Gold Count ($N=9,010$) | Proportion |
|---|---|---|---|
| **NORM** | Normal ECG | 5,629 | **62.5%** |
| **STTC** | ST/T Changes | 1,251 | 13.9% |
| **MI** | Myocardial Infarction | 937 | 10.4% |
| **CD** | Conduction Disturbance | 896 | 9.9% |
| **HYP** | Hypertrophy | 297 | **3.3%** |

Normal records outnumber Hypertrophy by nearly **19 to 1**.

---

### 5.2 Support Vector Inflation: Diagnosis and Fix

In a standard SVM, support vectors are the points that lie strictly on the margin or violate it:
$$\mathcal{SV} = \{k : y_k (\mathbf{w}^T \phi(\mathbf{x}_k) + b) \le 1\}$$
For a well-balanced dataset, typical support vector ratios are $20\% \text{ to } 40\%$, meaning only points near the boundary dictate the separating hyperplane while points deep within the interior are irrelevant.

#### 5.2.1 The Original Failure Mode: 100% SV Inflation

In the initial (v1) TSVM implementation, **all 3,968 unlabeled points** were included without filtering. This caused an extreme failure:

> **Empirical Law of Imbalanced Transductive Margins (v1)**:  
> *Across **all** tested gold fractions $\eta \in \{0.02, 0.05, 0.10, 0.20, 0.50\}$, **100% of all labeled minority-class samples became active support vectors** ($|SV_c| / N_c = 1.0$).*

**Why this occurred mathematically:**
1. **Majority Class Density Pull**: Since 62.5% of the data belongs to NORM, the unlabeled NORM cluster exerts a massive gravitational pull on the hyperplane.
2. **Margin Collapse**: To avoid cutting through the dense NORM cluster, the optimizer pushes the hyperplane into the sparse territory of minority classes (HYP, CD, MI).
3. **Boundary Inundation**: Every single minority sample falls within the margin band ($\mathbf{w}^T \phi(\mathbf{x}) + b < 1$), making every minority point an active SV. The transductive margin completely collapses for minority classes, leading to near-zero F1 for HYP and STTC.

#### 5.2.2 The Fixed Implementation: Margin-Percentile Filtering

The v2 TSVM resolves this with **three structural changes**:

**1. Margin-Percentile Filtering (the core fix):**

Instead of including all $|\mathcal{D}_U| = 3968$ unlabeled points, we filter to the **top 35% most confidently predicted** unlabeled samples:

$$\mathcal{D}_U^{\text{filtered}} = \{x_j \in \mathcal{D}_U : \text{margin}(x_j) \ge \text{percentile}_{65}(\{\text{margin}(x_i)\}_{i \in \mathcal{D}_U})\}$$

where $\text{margin}(x_j) = \max_c f_c(x_j) - \text{second\_max}_c f_c(x_j)$ under the initial base SVM.

This prevents the boundary-uncertain minority-class samples near the NORM/MI/HYP overlap region from participating in optimization, dramatically reducing SV inflation.

**2. Adaptive $C_{U,\max}$ scaling:**

$$C_{U,\max} = \min\!\left(0.30,\; 0.8 \cdot \frac{N_L}{|\mathcal{D}_U^{\text{filtered}}|}\right)$$

This ensures the unlabeled regularization weight scales proportionally with the gold/unlabeled ratio. At very low η (η=0.02, $N_L=180$), this caps $C_U$ very aggressively, preventing the unlabeled noise from overwhelming the 180 gold samples.

**3. Balanced class weights:**

The SVC uses `class_weight='balanced'`, which upweights minority classes by $w_c = N / (C \cdot N_c)$. For HYP ($N_c = 10$ at η=0.02), $w_{\text{HYP}} \approx 18\times$ the NORM weight, preventing the optimizer from ignoring the minority clusters.

**Empirical result with the fix:**

| η | BaseSVM Acc | TSVM Acc | ΔAcc | BaseSVM F1 | TSVM F1 | ΔF1 |
|---|---|---|---|---|---|---|
| 0.02 | 0.4951 | 0.5018 | **+0.007** | 0.3830 | 0.3875 | **+0.005** |
| 0.05 | 0.5286 | 0.5646 | **+0.036** | 0.4187 | 0.4245 | **+0.006** |
| 0.10 | 0.5061 | 0.5889 | **+0.083** | 0.4326 | 0.4584 | **+0.026** |
| 0.20 | 0.5329 | 0.5956 | **+0.063** | 0.4576 | 0.4884 | **+0.031** |
| 0.50 | 0.5591 | 0.5907 | **+0.032** | 0.4962 | 0.4991 | **+0.003** |

TSVM now shows **positive gains in both Accuracy and Macro F1 across all 5 η values**, confirming that the low-density separation principle is effective once minority-class boundary samples are excluded from the unlabeled optimization.

---

### 5.3 Why Co-Training Resists Imbalance Better than TSVM

Co-Training does not suffer from this margin collapse for three structural reasons:

1. **Per-Class Candidate Pools**:  
   In each co-training round, the selection is parameterized by $p$ **per class**:
   $$\text{Select top-}p \text{ samples for class } c, \quad \forall c \in \{0, \dots, C-1\}$$
   Regardless of whether NORM has 2,000 high-confidence candidates and HYP has only 10, the algorithm takes at most $p=10$ candidates for NORM and at most $p=10$ candidates for HYP. This enforces **balanced pseudo-label growth** even under severe class imbalance.

2. **Non-Contradiction Filtering**:  
   Before h1 adds a sample with label $c$ to L2, we require that h2 also predicts class $c$ on that sample's view. This prevents confirmation bias: a sample that h1 is confident about STTC but h2 sees as NORM is **rejected**, not added. This design avoids the cascade failure where one view's errors propagate unchecked through the other.

3. **Confidence-Weighted Pseudo-Labels**:  
   Each pseudo-label has weight $w = \text{pseudo\_w} \times \text{conf}$ where $\text{pseudo\_w} = 0.35$. This downweights uncertain pseudo-labels (e.g., conf=0.75 → w=0.26) relative to gold labels (w=1.0), preventing the minority pseudo-labels from being treated as equivalent to verified gold annotations.

As a result, Co-Training achieves **Macro F1 = 0.4386** at $\eta = 0.10$ (a +0.035 gain over the 2-view supervised baseline of 0.4039), maintaining balanced predictive capacity across all 5 superclasses without geometric boundary collapse.

---

## 6. Summary Comparison & Role in Final Evaluation

The theoretical and empirical findings of WP4 provide crucial benchmarks for the overarching project:

```
┌─────────────────────────┬──────────────────────────────┬──────────────────────────────┐
│ Dimension               │ Multi-View Co-Training       │ Transductive SVM (TSVM)      │
├─────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Fundamental Assumption  │ Conditional independence of  │ Low-density separation       │
│                         │ multiple feature views       │ (margin avoids clusters)     │
│ Input Requirements      │ 2 independent feature views  │ 1 unified feature space      │
│ Base Estimator          │ HistGradientBoosting (HGB)   │ Balanced SVC (OvR)           │
│ Unlabeled Handling      │ Discard y~; non-contradiction│ Discard y~; margin-pct filter│
│                         │ filtering + confidence weighting│ + C_U annealing           │
│ Convergence Indicator   │ Inter-view agreement rate    │ Support vector count / C_U   │
│ Resistance to Imbalance │ HIGH (per-class p-capping +  │ MODERATE (balanced weights + │
│                         │  non-contradiction filter)   │  margin-pct filtering)       │
│ Best Val Acc vs Base    │ +0.007 (η=0.05)              │ +0.083 (η=0.10)              │
│ Best Val F1 vs Base     │ +0.071 (η=0.05)              │ +0.031 (η=0.20)              │
│ Validation F1 at η=0.10 │ 0.4386 (+0.035 vs Base2V)   │ 0.4584 (+0.026 vs BaseSVM)   │
│ Validation Acc at η=0.10│ 0.6352 (+0.006 vs Base2V)   │ 0.5889 (+0.083 vs BaseSVM)   │
│ SSL gain direction      │ Positive F1 at η=0.02–0.20  │ Positive both at all 5 η     │
└─────────────────────────┴──────────────────────────────┴──────────────────────────────┘
```

### Connection to WP5 (Latent-Noise EM):
In WP5's final comparative synthesis, WP4's results serve as the definitive benchmark for the **"Discard Noisy Labels"** strategy. The project can conclusively demonstrate:
- When untrusted labels contain structured annotator noise (e.g. over-flagging MI at 28% vs 10%), **Co-Training safely circumvents label noise** by relying on view consensus (non-contradiction filtering), yielding up to +0.071 F1 gain at $\eta = 0.05$.
- **TSVM** also consistently improves over its supervised baseline (positive ΔAcc and ΔF1 at all η values) once margin-percentile filtering and balanced class weights are applied — demonstrating that the low-density separation principle is effective when boundary-uncertain minority-class samples are excluded from optimization.
- The natural question becomes: **does WP5's Latent-Noise EM, which keeps the noisy labels and models the confusion matrix $T_{ck} = P(\tilde{y} = k \mid z = c)$, achieve even better recovery than the discard paradigm?** WP4's results provide the discard paradigm's upper bound for this comparison.
