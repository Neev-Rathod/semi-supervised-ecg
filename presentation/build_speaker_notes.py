"""
presentation/build_speaker_notes.py
===================================
Builds a crisp, print- and tablet-ready editorial Speaker Notes & Viva Defense
PDF at presentation/speaker_notes.pdf aligned 1:1 with presentation/main.typ
(Cover + Slides 01-18 + References + Consolidated Viva Q&A Vault).
"""

from pathlib import Path
import subprocess

HTML_OUT = Path(
    "/home/shaurya/.gemini/antigravity/brain/1e0943a9-7357-4ba1-abd5-71d534904893/scratch/speaker_notes.html"
)
PDF_OUT = Path(__file__).resolve().parent / "speaker_notes.pdf"

SLIDES = [
    {
        "num": "COVER",
        "wp": "TEAM INTRO · ~20s",
        "accent": "ink",
        "title": "Semi-Supervised Learning Under Label Scarcity & Structured Noise",
        "point": "Open confidently: we ask whether automated hospital ECG diagnoses should be thrown away or probabilistically modeled when expert labels are scarce.",
        "say": [
            "Introduce the project in one crisp line: we benchmark <strong>four classical semi-supervised strategies</strong> on clinical 12-lead ECGs (PTB-XL) without deep learning.",
            "Set expectations quickly: each work package answers a clear causal link—<strong>WP1</strong> (features & hardware artifacts), <strong>WP2</strong> (controlled noise laws), <strong>WP3–WP4</strong> (discarding noisy hospital labels), and <strong>WP5</strong> (learning & inverting the noise channel).",
        ],
        "transition": "Let us start with why this problem exists in real clinics and the four exact questions guiding our study.",
        "qa": None,
    },
    {
        "num": "01 / 18",
        "wp": "OVERVIEW · TEAM LEAD · ~45s",
        "accent": "vermilion",
        "title": "Can Machine-Generated Hospital Labels Help When Expert Labels Are Scarce?",
        "point": "Hospitals sit on two unequal label sources—a tiny verified Gold Set (D_L) and a large, systematically biased machine pool (D_U).",
        "say": [
            "Point first to the red banner: expert verification takes cardiologist time, leaving <strong>D_L</strong> scarce (we test fractions <code>η ∈ {2, 5, 10, 20, 50}%</code>). Meanwhile, ECG machines auto-generate <code>3,968</code> unverified labels (<strong>D_U</strong>).",
            "Highlight the core ML dilemma: existing semi-supervised methods either <strong>discard</strong> unreliable labels completely (WP3 Graph LP, WP4 Co-Training & TSVM) or explicitly <strong>model and invert</strong> the hospital's mistake matrix (WP5 EM).",
            "Briefly gesture to <strong>Q1–Q4</strong> on the bottom cards—every slide ahead directly answers one of these four questions.",
        ],
        "transition": "Neev will start with WP1: turning raw ECG heartbeats into features, revealing a hidden bias in D_U, and testing Q1.",
        "qa": None,
    },
    {
        "num": "02 / 18",
        "wp": "WP1 (1/4) · NEEV RATHOD · ~50s",
        "accent": "cobalt",
        "title": "Why We Convert Raw 10-Second ECG Waves into 84 Clean Summary Features",
        "point": "We transform shift-sensitive 10-second waveforms into one frozen 84-D tabular space split into Time and Frequency views for an apples-to-apples SSL comparison.",
        "say": [
            "Walk across <strong>Panel A</strong>: each patient has a 10-second ECG at 100 Hz across 12 sensor angles (<code>1,000 × 12</code> numbers). On <strong>Lead II</strong> (aligned with the heart's electrical axis for the sharpest spikes), we detect <strong>R-peaks</strong> and measure <strong>HRV</strong> (mean/std RR gaps and beat-to-beat RMSSD jitter).",
            "Point to <strong>Panel B</strong>: real PTB-XL metadata flags two physical glitches—slow breathing sway (<code>baseline_drift</code>, 0.5–4 Hz) and loose-lead fuzz (<code>static_noise</code>, 15–40 Hz).",
            "Explain <strong>why 84-D instead of raw waves</strong>: classical models cannot align shifted heartbeats or fit 12,000 dimensions at <code>η = 2%</code> (180 records). Splitting into <strong>View 1 (Time/HRV/Hjorth, 0:42)</strong> and <strong>View 2 (Welch PSD + db4 wavelets, 42:84)</strong> freezes one fair space across WP3–WP5.",
        ],
        "transition": "Next, let us see how those patients are partitioned and the alarming bias hiding inside machine reports.",
        "qa": "Why does View 1 have 34 active features plus 8 zero-padded slots? StandardScaler, PCA, L2-LogReg, RBF-SVM, and trees mathematically ignore zero-variance columns; keeping one shared 84-D file keeps WP3–WP5 apples-to-apples.",
    },
    {
        "num": "03 / 18",
        "wp": "WP1 (2/4) · NEEV RATHOD · ~50s",
        "accent": "vermilion",
        "title": "Patient-Safe Splits Expose a Hidden 2.7× Heart-Attack Skew in Machine Labels",
        "point": "Machine-generated ECG labels aren't random typos—they over-diagnose heart attacks (MI) at 2.7× the cardiologist rate.",
        "say": [
            "Trace <strong>Panel A</strong> top-to-bottom: <code>21,837</code> raw recordings filter down to <code>16,272</code> clean single-label ECGs across 5 diseases (<code>NORM, MI, STTC, CD, HYP</code>). Crucially, PTB-XL stratifies by <strong>patient</strong> so the same heart never leaks across Folds 1–8 Train (<code>12,978</code>), Fold 9 Val (<code>1,642</code>), and Fold 10 Test (<code>1,652</code>).",
            "Pause on <strong>Panel B</strong>—this is the project's first smoking gun: splitting Folds 1–8 by <code>validated_by_human</code> yields <code>9,010</code> Gold records vs. <code>3,968</code> Untrusted records. In Gold, heart attacks (<code>MI</code>) are <code>10.4%</code>; in machine logs they spike to <strong><code>28.0%</code> (2.7× higher)</strong> while <code>NORM</code> drops <code>62.5% → 40.9%</code>.",
            "Conclude: because <code>NORM</code> dominates (<code>~55%</code>) and errors are skewed, we use <strong>Macro F1</strong> everywhere—not accuracy.",
        ],
        "transition": "Knowing our labels are skewed, WP1 next tests Q1: does physical sensor noise also distort feature distances before any classifier runs?",
        "qa": "Is Fold 9/10 gold-filtered? No—Folds 9 and 10 are strict patient-stratified evaluation folds preserving overall class ratios (~55% NORM, ~15% MI).",
    },
    {
        "num": "04 / 18",
        "wp": "WP1 (3/4) · NEEV RATHOD · ~50s",
        "accent": "cobalt",
        "title": "Wire Drift Distorts Euclidean Clusters (−5.1 pp), While PCA & Mahalanobis Help",
        "point": "Physical sensor artifacts degrade Euclidean clusters by −5.1 pp, whereas PCA cushions noise and full-pool Mahalanobis whitening doubles ARI.",
        "say": [
            "State the motivation upfront: Graph SSL (WP3) assumes nearby points share diagnoses. Running <strong>blind k-Means (k = 5)</strong> acts as an X-ray of feature geometry under <strong>Q1</strong>.",
            "Point to the dumbbell plot in <strong>Panel A</strong>: clean ECGs always cluster purer than artifact-flagged ones. <strong>Raw Euclidean</strong> takes the worst hit (<code>0.591 → 0.540</code>, <strong>−5.1 pp</strong>) because baseline drift causes correlated spikes across leads.",
            "Point to <strong>Panel B</strong>: compressing with <strong>PCA-20</strong> trims the clean–noisy drop to <code>−4.2 pp</code> and raises Euclidean ARI by <strong>+49%</strong> (<code>0.049 → 0.072</code>). Using full-pool <strong>Mahalanobis</strong> (whitening by <code>Σ⁻¹</code> over all 12,978 records) <strong>doubles ARI (0.049 → 0.108, 2.2×)</strong>.",
        ],
        "transition": "Wait—if Mahalanobis doubled ARI here, why did purity still plateau near 58%? Slide 05 explains both that ceiling and what happens in WP3.",
        "qa": None,
    },
    {
        "num": "05 / 18",
        "wp": "WP1 (4/4) · NEEV RATHOD · ~45s",
        "accent": "vermilion",
        "title": "Heavy Disease Overlap Caps Clustering at ~58%, Predicting WP3's Limit",
        "point": "Heavy feature overlap between NORM, MI, and STTC caps clustering near ~58% purity—predicting WP3's limit and WP3's low-D PCA requirement.",
        "say": [
            "Cite <strong>Panel A</strong> quickly: <code>5</code> PCs capture <code>52.0%</code> variance, <code>20</code> PCs capture <code>86.3%</code>, and <code>24</code> cross <code>90%</code>—so 84-D compresses well.",
            "Focus on <strong>Panel B</strong>: projecting 2,500 real ECGs into <code>(PC1, PC2)</code> shows all five disease medians packed tightly together. <code>MI</code> and <code>STTC</code> overlap <code>NORM</code> heavily.",
            "Deliver the <strong>two crucial foresight predictions</strong>: first, pure neighbor diffusion (WP3) will struggle across overlapping classes; second, while WP1 estimated covariance <code>Σ</code> on <code>12,978</code> points, WP3 fits <code>Σ_L</code> on tiny Gold slices (<code>180–900</code> points), which will require tight <code>PCA = 5</code> compression.",
        ],
        "transition": "With WP1's geometry mapped, Shaurya steps into WP2 to test exactly how noise breaks standard classifiers in a controlled lab.",
        "qa": None,
    },
    {
        "num": "06 / 18",
        "wp": "WP2 (1/3) · SHAURYA SUMAN · ~55s",
        "accent": "ink",
        "title": "Why We Built a Synthetic Lab: Trees Memorize Noise & Self-Training Backfires",
        "point": "Our controlled 50-D manifold exposes how each family fails under uniform flips—tree over-branching (−38.5%), SVM SV bloat (96%), and single-view self-training collapse.",
        "say": [
            "Answer <em>why build a synthetic lab?</em> PTB-XL never reveals true labels inside D_U, so we cannot sweep <code>ε</code> cleanly or check <code>T_hat</code> against ground truth. We build <code>3,000</code> orthogonal-rotated points (<code>10</code> informative, <code>5</code> correlated redundant, <code>35</code> noise dims) and map <strong>5 baselines</strong> directly to WP3–WP5 (GNB/LR → WP5, 7-NN → WP3, DT/SVM → WP4).",
            "Walk across the 5 small multiples as pool noise <code>ε → 60%</code>: unpruned <strong>Decision Trees crash worst (−38.5%)</strong> as leaves double (<code>348 → 641</code>) memorizing wrong labels—directly motivating WP4's depth-4 cap. <strong>7-NN drops −27.1%</strong>, crossing below <code>gold_only</code> by <code>ε ≈ 32%</code>.",
            "Highlight two hidden traps: <strong>RBF-SVM</strong> looks flat (<code>−7.4%</code>), yet support vectors swell from <code>1,318</code> to <strong><code>2,015</code> (96% of train!)</strong>; meanwhile naive single-view <strong>self-training collapses GNB by −8.3 pp</strong> (<code>0.648 → 0.565</code>) via overconfident self-contamination.",
        ],
        "transition": "That was purely uniform random noise. What happens when hospital noise is structured—like misdiagnosing specific pairs?",
        "qa": "Why only corrupt D_U? D_L models cardiologist verification (trusted anchor) and Val is the clean ground-truth test key; only automated logs D_U vary in noise rate.",
    },
    {
        "num": "07 / 18",
        "wp": "WP2 (2/3) · SHAURYA SUMAN · ~55s",
        "accent": "vermilion",
        "title": "Random Noise Spares Voting, But Systematic Confusion Collapses Every Model",
        "point": "Answering Q2: uniform flips spare plurality voting, whereas structured pair confusion (0↔1, 2↔3) crashes SVM, LR, and GNB alike—forcing WP5's C×C channel T.",
        "say": [
            "Explain the X-axis: we align all three mathematical noise injectors by the <strong>actual % of pool labels flipped</strong>.",
            "Compare <strong>Panel A (Uniform)</strong> vs. <strong>Panel B (Asymmetric Pair Confusion <code>0↔1, 2↔3</code>)</strong>: under uniform noise at <code>60.2%</code> flips, errors spread across 4 wrong classes so SVM stays at <code>0.814</code>. Under hospital-like pair confusion at just <strong><code>48.5%</code> flips</strong>, <strong>every single classifier collapses</strong>—SVM plunges <code>0.879 → 0.534</code>, LR drops <code>0.761 → 0.440</code>, and GNB crashes <code>0.649 → 0.464</code>—because wrong classes outvote truth.",
            "Point to <strong>Panel C (Boundary noise, Eq. 3.1)</strong>: concentrated near decision margins, it drives <code>SVM-naive_pool</code> (<code>0.794</code>) below <code>gold_only</code> (<code>0.813</code>) earlier at <code>40%</code> flips. Takeaway for Q2: regularizers cannot defeat structured confusion—we need WP5's full <code>C × C</code> matrix <code>T</code>.",
        ],
        "transition": "Before moving to semi-supervised learners, let us run these exact WP2 baselines on real PTB-XL to see the reality check.",
        "qa": None,
    },
    {
        "num": "08 / 18",
        "wp": "WP2 (3/3) · SHAURYA SUMAN · ~45s",
        "accent": "cobalt",
        "title": "On Real PTB-XL, Structured MI Bias Shatters Gaussian NB (−9.7 pp)",
        "point": "Real PTB-XL class imbalance and the 28% MI bias invert synthetic intuition—crashing naive GNB by −9.7 pp while establishing balanced LogReg as the bar for WP3–WP5.",
        "say": [
            "Point out the dramatic flip on <strong>Gaussian NB</strong>: on synthetic uniform flips GNB lost only <code>6.3%</code>. On real PTB-XL at <code>η = 2%</code>, <strong>pooling raw D_U crashes GNB by −9.7 pp</strong> (<code>0.362 → 0.265</code>) across every Gold fraction, because the <code>28% MI</code> bias warps Gaussian priors and variances.",
            "Highlight the real supervised bar: <strong>Balanced LogReg</strong> rises from <code>0.403</code> (<code>η=2%</code>) to <strong><code>0.494</code> val (<code>0.466</code> test)</strong> at <code>η=100%</code>, overtaking <code>naive_pool</code> (<code>0.489</code>) once Gold is abundant.",
            "Confirm naive <code>self_training</code> fails on ECGs too (<code>kNN</code> drops <code>0.216 → 0.143</code> at <code>2%</code>)—handing WP3–WP5 an honest, demanding supervised bar.",
        ],
        "transition": "We now begin testing the four semi-supervised approaches for Q3—starting with Pratyush on WP3 Graph Label Propagation.",
        "qa": None,
    },
    {
        "num": "09 / 18",
        "wp": "WP3 (1/3) · PRATYUSH SOMANI · ~45s",
        "accent": "cobalt",
        "title": "Spreading Verified Labels Over an ECG Network Works Best on Small Graphs",
        "point": "Approach 1 discards y_tilde_U and diffuses Gold labels on a k-NN graph—confirming WP1's prediction that scarce-Gold Mahalanobis requires PCA = 5 compression.",
        "say": [
            "Define <strong>Approach 1</strong>: discard noisy hospital labels <code>y_tilde_U</code>, build a Gaussian k-NN affinity graph over <code>D_L ∪ D_U</code>, and solve the closed-form harmonic system <code>(D_UU − W_UU) F_U = W_UL Y_L</code>.",
            "Explain <strong>Panel A (900 fits across distance × PCA × k × η)</strong>: this directly resolves the WP1-vs-WP3 Mahalanobis question. Estimating an <code>84 × 84</code> inverse covariance <code>Σ_L⁻¹</code> from scarce Gold sets (<code>180–900</code> points) blows up variance (<strong><code>0.211</code> at raw 84-D</strong>), recovering only when compressed to <strong><code>PCA = 5</code> (<code>0.290</code> vs Euclidean <code>0.294</code>)</strong>.",
            "Point to <strong>Panel B</strong>: tight graphs (<strong><code>k = 3</code></strong>, <code>1.3–2.0</code> components, <code>&lt;6</code> unreachable nodes) beat wider ones (<code>0.299 → 0.245</code> mean at <code>k=20</code>) because large neighborhoods bridge across disease boundaries.",
        ],
        "transition": "With our best graph geometry (Euclidean, PCA=5, k=3) locked on validation, how does it actually score on held-out Test Fold 10?",
        "qa": "What about Class-Mass Normalization (CMN)? A 60-run matched ablation showed CMN added only +0.0014 mean Macro F1—negligible next to the ~0.10 baseline gap.",
    },
    {
        "num": "10 / 18",
        "wp": "WP3 (2/3) · PRATYUSH SOMANI · ~45s",
        "accent": "vermilion",
        "title": "Adding Unlabeled ECGs Fails to Beat Same-Space k-NN or Linear Classifiers",
        "point": "Adding 3,968 unlabeled nodes gives zero consistent advantage over identical-space Gold k-NN and trails Gold-only linear/SVM baselines by 0.09–0.13 Macro F1.",
        "say": [
            "Focus first on <strong>Panel B (Same-Embedding Control)</strong>: comparing Graph LP against supervised <code>Gold k-NN</code> in the <em>exact same 5-D space</em> on Fold-10 Test yields <code>0.258 vs 0.306</code> at <code>2%</code>, <code>0.309 vs 0.328</code> at <code>10%</code>, and <code>0.352 vs 0.348</code> at <code>50%</code>. The unlabeled ECGs add <strong>no consistent transductive lift</strong>.",
            "Point to the shaded band in <strong>Panel A</strong>: Gold-only <strong>Balanced RBF-SVM</strong> (<code>0.352 → 0.471</code>) and <strong>Balanced LogReg</strong> (<code>0.335 → 0.457</code>) beat Graph LP (<code>0.258 → 0.352</code>) by <strong>+0.09 to +0.13 F1</strong>—and even <em>unweighted</em> LogReg beats LP cleanly.",
        ],
        "transition": "A careful scientist asks why—which classes collapsed inside Graph LP, and why is this negative finding actually decisive?",
        "qa": None,
    },
    {
        "num": "11 / 18",
        "wp": "WP3 (3/3) · PRATYUSH SOMANI · ~45s",
        "accent": "forest",
        "title": "Why Pure Neighbor Smoothing Fails on Overlapping ECGs — Eliminating WP3",
        "point": "Unweighted LogReg beats Graph LP on all 5 classes—especially STTC (0.106) and MI (0.181)—proving WP1's ~58% overlap breaks pure passive diffusion.",
        "say": [
            "Look at <strong>Panel A</strong> at <code>η = 10%</code> (<code>901</code> Gold records): unweighted LogReg beats Graph LP on <em>every single class</em> (including <code>NORM: 0.775 vs 0.720</code>), while isotropic diffusion crushes ischemic minorities—<strong><code>STTC = 0.106</code></strong> (vs <code>0.262</code>) and <strong><code>MI = 0.181</code></strong> (vs <code>0.260</code>).",
            "Frame the verdict using the 3 cards in <strong>Panel B</strong>: WP3 is a <em>textbook scientific elimination</em> rather than a bug. It validates WP1's Slide 05 forecast that overlapping ECG clouds violate the manifold smoothness needed by harmonic propagation.",
            "That rules out Approach 1 (passive geometry) and forces us toward <strong>discriminative boundaries (WP4)</strong> or <strong>modeling hospital noise (WP5)</strong>.",
        ],
        "transition": "Arnav picks up in WP4: still discarding y_tilde_U, can dual-view Co-Training and margin-based TSVMs succeed where passive graphs failed?",
        "qa": None,
    },
    {
        "num": "12 / 18",
        "wp": "WP4 (1/3) · ARNAV GUPTA · ~50s",
        "accent": "cobalt",
        "title": "Two Separate ECG Views Teaching Each Other Excel When Labels Are Scarce",
        "point": "Approach 2 splits Time and Frequency views using depth-capped boosted trees—delivering strong +0.051 to +0.071 F1 gains when Gold ≤ 10%, before hitting a 50% ceiling.",
        "say": [
            "Connect straight back to WP1 & WP2: Co-Training trains separate <code>HistGradientBoosting(max_depth=4)</code> learners (honoring WP2's depth cap!) on <strong>View 1 (Time/HRV)</strong> and <strong>View 2 (PSD/Wavelets)</strong>, pseudo-labeling top <code>10</code> unlabeled ECGs per class across 12 rounds only on <strong>non-contradictory high confidence (≥ 0.72, weight 0.35)</strong>.",
            "Contrast the two regimes in <strong>Panels A & B</strong>: in the <strong>Scarcity Sweet Spot (η ≤ 10%)</strong>, Co-Training lifts the 2-View Base by <strong>+0.051 at 2%</strong> (<code>0.315 → 0.365</code>, test <code>0.352</code>) and <strong>+0.071 at 5%</strong> (<code>0.361 → 0.431</code>, test <code>0.397</code>)—and even beats the joint <strong>Full-84D</strong> model by <code>+0.057</code> at <code>5%</code>!",
            "Be candid on <strong>50% saturation</strong>: once Gold reaches <code>4,505</code> records, joint <code>Full-84D</code> trees (<code>0.516</code>) capture cross-view feature splits better than pseudo-labels (<code>0.470</code>).",
        ],
        "transition": "Let us zoom into η = 5% to see which heart conditions gained and confirm our two ECG views truly stayed complementary.",
        "qa": None,
    },
    {
        "num": "13 / 18",
        "wp": "WP4 (2/3) · ARNAV GUPTA · ~45s",
        "accent": "cobalt",
        "title": "Co-Training Rescues Rare Arrhythmias Because Both Views Stay Complementary",
        "point": "Co-Training lifts every pathology at η = 5%—doubling rare HYP (+0.142) and lifting STTC (+0.116)—while ~22% inter-view disagreement prevents echo-chamber collapse.",
        "say": [
            "Walk across <strong>Panel A</strong> at <code>η = 5%</code> (<code>450</code> Gold records): unlike Graph LP which flooded rare classes into NORM, Co-Training boosts all five superclasses—<strong><code>HYP</code> nearly doubles (<code>0.164 → 0.306, +0.142</code>)</strong>, <strong><code>STTC</code> jumps <code>+0.116</code></strong>, and <strong><code>MI</code> climbs <code>+0.074</code></strong> (and <code>+0.152</code> on <code>MI</code> at <code>η = 2%</code>!).",
            "Explain <strong>Panel B</strong>: Blum & Mitchell's Co-Training theory requires two informative yet non-redundant views. <strong>View 2</strong> (spectral bands + <code>db4</code> wavelets catching brief Q/T spikes) leads View 1 by <code>+6 to +8 pp</code>, while cross-view agreement stabilizes around <strong><code>77.4–80.5%</code></strong>—meaning ~22% honest disagreement prevents WP2's single-view self-contamination.",
        ],
        "transition": "Next we test Approach 3 in WP4: Transductive SVM, pushing maximum margins across all 84 features jointly.",
        "qa": None,
    },
    {
        "num": "14 / 18",
        "wp": "WP4 (3/3) · ARNAV GUPTA · ~50s",
        "accent": "forest",
        "title": "Filtering Confident Unlabeled ECGs Lifts RBF-SVM Margins Everywhere",
        "point": "Approach 3 filters unlabeled ECGs to the top 35% margin-confident set (1,389) and anneals C_U ≤ 0.30—beating balanced RBF-SVM across every η (peak +0.031 at 20%).",
        "say": [
            "Connect to WP2's SV bloat lesson: throwing all 3,968 overlapping ECGs into an unlabeled SVM floods the margin. So we keep only the <strong>top 35% margin-confident pool (<code>1,389 / 3,968</code>)</strong> and gently anneal <code>C_U: 0.05 → 0.30</code> over 3 switching steps.",
            "Show <strong>Panel A</strong>: TSVM improves balanced RBF-SVM at <strong>all five η levels</strong>, peaking at <strong>+0.026 at 10%</strong> (<code>0.433 → 0.458</code>, test <code>0.441</code>) and <strong>+0.031 at 20%</strong> (<code>0.458 → 0.488</code>, test <code>0.459</code>), reaching <code>0.499</code> val / <code>0.474</code> test at <code>50%</code>.",
            "Point to <strong>Panel B</strong>: support vectors grow as WP2 predicted (<code>177 → 1,099</code> at <code>2%</code>), yet capping <code>C_U</code> keeps generalization clean. Still, <strong>WP4 throws away all 3,968 hospital labels <code>y_tilde_U</code></strong>—setting up WP5's punchline.",
        ],
        "transition": "Tanuj now presents WP5: instead of discarding hospital auto-labels, what happens if we treat the hospital software as a noisy channel and invert it?",
        "qa": None,
    },
    {
        "num": "15 / 18",
        "wp": "WP5 (1/3) · TANUJ YADAV · ~50s",
        "accent": "cobalt",
        "title": "Instead of Discarding Machine Labels, Model and Invert Their Mistake Pattern",
        "point": "Approach 4 models D_U via LatentNoiseEM—jointly fitting clean classifier θ and confusion matrix T, cutting synthetic Frobenius error by −63% on WP2's asymmetric lab.",
        "say": [
            "Frame the intuition simply: automated ECG software is biased (Slide 03), <em>yet still correct ~80–90% of the time</em>. Throwing <code>y_tilde_U</code> away wastes diagnostic signal. In <strong>Panel A</strong>, <code>LatentNoiseEM</code> models a <code>5 × 5</code> confusion channel <code>T_{c,j} = P(y_tilde = j | y = c)</code>:",
            "1) <strong>Anchor Init</strong>: train balanced Logistic Regression <code>θ⁰</code> on clean Gold D_L; 2) <strong>E-Step</strong>: infer posterior disease probabilities <code>γ</code> combining features and <code>T</code>; 3) <strong>M-Step</strong>: update Laplace-smoothed rows of <code>T</code> (<code>α = 1</code>) and refit <code>θ</code>.",
            "Point to <strong>Panel B</strong>: because PTB-XL hides true <code>D_U</code> labels, we validate EM on <strong>WP2's asymmetric synthetic benchmark</strong>: Frobenius recovery error <code>||T_hat − T_true||_F</code> drops <strong>−63%</strong> (<code>0.364</code> at <code>n_pool=100</code> → <strong><code>0.135</code></strong> at <code>n_pool=2,000</code>).",
        ],
        "transition": "Now we put Approach 4 head-to-head against discarding methods across label scarcity and heavy noise to answer Q3.",
        "qa": "Can EM identify T without degenerating on rare HYP? Yes—clean Gold D_L anchors classifier θ while α = 1.0 Laplace smoothing stabilizes rare rows.",
    },
    {
        "num": "16 / 18",
        "wp": "WP5 (2/3) · TANUJ YADAV · ~55s",
        "accent": "vermilion",
        "title": "Modeling Noisy Labels Wins Under Scarcity (0.462 at 2% Gold) & Extra Noise",
        "point": "Answering Q3 honestly: modeling y_tilde_U beats all discard methods under clinical scarcity (0.462 at 180 Gold records!) and survives +45% extra noise; nonlinear WP4 catches up only at η ≥ 20%.",
        "say": [
            "Show <strong>Panel B</strong>: across WP5's <code>20</code>-cell benchmark grid (5 scarcity levels × 4 extra noise injections up to <code>+45%</code>), <strong>EM wins 20/20 cells (<code>0.411–0.462</code>)</strong>. At <code>η = 2%</code> (just 180 Gold records!), EM achieves <strong><code>0.462</code> Macro F1</strong> and stays above <code>0.41</code> even after scrambling 45% more D_U labels.",
            "Be 100% transparent on the green dotted line in <strong>Panel A</strong> (great scientific integrity!): WP5's original CSV ran against WP4's earlier LogReg CoTrainer (<code>0.326–0.355</code>), before WP4 upgraded Co-Training to HistGBT (<code>0.365–0.470</code>). Plotting both openly reveals the <strong>exact phase law answering Q3</strong>:",
            "<strong>At scarcity (η ≤ 10%)</strong>, modeling <code>y_tilde_U</code> via EM (<code>0.453–0.462</code>) beats upgraded Co-Training (<code>0.365–0.439</code>) and TSVM (<code>0.388–0.458</code>). <strong>At abundance (η ≥ 20%)</strong>, nonlinear TSVM/HistGBT catch up to linear EM.",
        ],
        "transition": "Beyond raw accuracy, what did EM actually discover inside the hospital's black-box ECG software? Slide 17 answers Q4 and closes the loop.",
        "qa": "Why do WP4's standalone F1 numbers (0.431–0.470) differ from CoTrain inside WP5's CSV (0.326–0.355)? Chronological commit order before WP4 upgraded CoTrainer to HistGBT—we plot both lines openly on Slide 16.",
    },
    {
        "num": "17 / 18",
        "wp": "WP5 (3/3) · TANUJ YADAV · ~50s",
        "accent": "vermilion",
        "title": "Learned Confusion Matrix T̂ Exposes Why Automated ECGs Over-Alarm MI",
        "point": "Answering Q4 & closing WP1's opening mystery: EM converges in 39 iterations and exposes 9.41% NORM→MI and 9.18% STTC→MI hospital software false alarms.",
        "say": [
            "Walk through <strong>Panel A</strong> (fit on all <code>9,010</code> Gold + <code>3,968</code> Pool records, converged in 39 EM steps): automated software is highly reliable along the diagonal for <strong>CD (96.5%)</strong>, <strong>MI (95.8%)</strong>, <strong>STTC (89.5%)</strong>, and <strong>NORM (87.9%)</strong>—while struggling most on rare <strong>HYP (79.2%)</strong>.",
            "Point directly to the top two red bars in <strong>Panel B</strong>: <strong><code>NORM → MI (9.41%)</code></strong> and <strong><code>STTC → MI (9.18%)</code></strong>, plus <strong><code>HYP → NORM (6.19%)</code></strong>.",
            "Deliver the project punchline: clinically, software errs on the side of defensive sensitivity—flagging healthy and mild ST-T ECGs as heart attacks (<code>MI</code>). Without reading a single true label in D_U, EM explains WP1's <strong>2.7× MI skew</strong> and WP2's <strong>GNB collapse</strong>.",
        ],
        "transition": "Let us bring all five work packages together into clear answers to Q1–Q4 and a deployment rule.",
        "qa": None,
    },
    {
        "num": "18 / 18",
        "wp": "SYNTHESIS · CLOSING · ~50s",
        "accent": "ink",
        "title": "What Every Work Package Taught Us — And Which Method to Use",
        "point": "Leave the committee with four crisp answers and one memorable rule: correct noisy labels via EM under scarcity (η ≤ 10%), and switch to nonlinear margins when Gold is plentiful (η ≥ 20%).",
        "say": [
            "Summarize <strong>Q1 (WP1/WP3)</strong>: physical wire noise cuts Euclidean purity (<code>−5.1 pp</code>); global Mahalanobis doubles ARI, whereas scarce-Gold covariance requires <code>PCA = 5</code>; <code>~58%</code> overlap limits neighbor diffusion.",
            "Summarize <strong>Q2 (WP2)</strong>: uniform flips kill unpruned trees (<code>−38.5%</code>) and swell SVM SVs (<code>96%</code>); structured pair confusion breaks everyone, and <code>28% MI</code> shift cuts PTB-XL GNB <code>−9.7 pp</code>.",
            "Summarize <strong>Q3 (WP3–WP5)</strong>: Graph LP fails under overlap; Co-Training lifts scarce views (<code>+0.071</code> at <code>5%</code>), TSVM peaks at <code>20%</code> (<code>0.488</code>), and <strong>Latent-Noise EM dominates scarcity (<code>0.462</code> at <code>2%</code>, 20/20 benchmark wins)</strong>.",
            "Summarize <strong>Q4 (WP5)</strong>: Frobenius error drops <code>63%</code> cleanly and audits real hospital bias (<code>NORM→MI 9.41%</code>, <code>STTC→MI 9.18%</code>).",
        ],
        "transition": "Thank you—all references are on the next slide, and we welcome questions on any work package.",
        "qa": None,
    },
]

VIVA_QA = [
    ("Q1 · Why 84-D features instead of raw 1,000 × 12 matrices? Doesn't 34+8 zero-padding bias features toward WP4?",
     "Classical models (SVM, LogReg, k-NN, EM) lack time-shift invariance and massively overfit 12,000 dims when η = 2% (180 records). One frozen 84-D file keeps WP3–WP5 strictly apples-to-apples, and StandardScaler/PCA/L2-models mathematically give the 8 zero-variance slots zero gradient or distance weight."),
    ("Q2 · Why did WP1 praise Mahalanobis (2.2× ARI) while WP3 saw raw 84-D Mahalanobis collapse (0.211)?",
     "Sample-size vs. dimensionality! WP1 estimated Σ on all 12,978 training records (N ≫ d), making covariance whitening stable. WP3's Eq. 4.1 estimates Σ_L only from Gold anchors (180–900 records), so inverting an 84 × 84 matrix amplifies sampling noise unless PCA-compressed to 5-D (where Mahalanobis recovers to 0.290 vs Euclidean 0.294)."),
    ("Q3 · Isn't WP2's 50-D Gaussian manifold completely unrealistic compared to PTB-XL's overlapping ECGs?",
     "By design: PTB-XL lacks ground truth y for D_U, making ε sweeps and T_hat error checks impossible. Removing ECG imbalance isolates pure noise laws first (uniform vs asymmetric vs boundary), then Slide 08 runs those exact baselines on real PTB-XL (<code>ptbxl_baselines.csv</code>) to reveal the −9.7 pp GNB shift caused by 28% MI skew."),
    ("Q4 · WP3 performed worse than simple supervised Logistic Regression—was Graph LP implemented wrong?",
     "No—two controls prove why: (1) On the exact same PCA=5 embedding, Gold-only k-NN already matched/beat Graph LP; (2) Unweighted LogReg beat Graph LP on all 5 classes (especially STTC 0.106 vs 0.262). Because WP1 proved ECG classes overlap (~58% max purity), isotropic label diffusion washes minority arrhythmias into majority NORM (~55%)."),
    ("Q5 · Why does WP4 Co-Training beat Full-84D at η = 2–5% yet lose at η = 50% (0.470 vs 0.516)?",
     "Expected bias-variance regime shift: splitting 84 dims into two halves regularizes tiny datasets (180–450 Gold) while non-contradictory consensus mines 3,968 unlabeled ECGs. By 4,505 Gold records, joint gradient-boosted splits across Time × Frequency features outvalue pseudo-labels."),
    ("Q6 · How do you reconcile WP4's standalone CoTrain F1 (0.431–0.470) with CoTrain inside WP5's CSV (0.326–0.355)?",
     "Honest commit-order lag: WP5 ran <code>discard_vs_correct.csv</code> before WP4 upgraded <code>CoTrainer</code> from LogisticRegression to HistGradientBoosting. Slide 16 transparently plots BOTH curves—confirming EM (0.462 at η=2%, 0.456 at 10%) still decisively wins the scarce regime (η ≤ 10%) even against upgraded HistGBT Co-Training (0.365–0.439)."),
]


def render_html() -> str:
    cards_html = []
    for s in SLIDES:
        acc = s["accent"]
        border_col = {"vermilion": "#b91c1c", "cobalt": "#1d4ed8", "forest": "#166534", "ink": "#18181b"}[acc]
        bg_pill = {"vermilion": "#f9eaea", "cobalt": "#eaf0fa", "forest": "#e9f4ec", "ink": "#ece7dc"}[acc]
        say_lis = "".join(f"<li>{item}</li>" for item in s["say"])
        qa_block = (
            f'<div class="qa-inline"><strong>Likely Q&amp;A Shield:</strong> {s["qa"]}</div>'
            if s["qa"] else ""
        )
        cards_html.append(f"""
        <section class="slide-card" style="border-top: 3px solid {border_col};">
          <div class="card-head">
            <span class="slide-num" style="background:{bg_pill}; color:{border_col}; border:1px solid {border_col};">SLIDE {s["num"]}</span>
            <span class="wp-tag" style="color:{border_col};">{s["wp"]}</span>
          </div>
          <h2>{s["title"]}</h2>
          <div class="point-box" style="border-left: 3px solid {border_col}; background:{bg_pill};">
            <strong>Core Takeaway:</strong> {s["point"]}
          </div>
          <ul class="say-list">{say_lis}</ul>
          <div class="transition-line"><strong>Next-Slide Handoff:</strong> <em>{s["transition"]}</em></div>
          {qa_block}
        </section>
        """)

    qa_cards = "".join(
        f"""
        <div class="viva-card">
          <div class="viva-q">{q}</div>
          <div class="viva-a">{a}</div>
        </div>
        """
        for q, a in VIVA_QA
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Speaker Notes — Semi-Supervised ECG (BITS F464)</title>
<style>
  @page {{
    size: A4;
    margin: 13mm 14mm 14mm 14mm;
    @top-right {{
      content: "BITS F464 · SEMI-SUPERVISED ECG · SPEAKER NOTES";
      font-family: "Liberation Sans", "DejaVu Sans", sans-serif;
      font-size: 7.5pt;
      color: #71717a;
      letter-spacing: 0.06em;
    }}
    @bottom-left {{
      content: "PTB-XL · WP1–WP5 Presentation & Viva Guide";
      font-family: "Liberation Sans", "DejaVu Sans", sans-serif;
      font-size: 8pt;
      color: #71717a;
    }}
    @bottom-right {{
      content: "Page " counter(page) " of " counter(pages);
      font-family: "Liberation Sans", "DejaVu Sans", sans-serif;
      font-size: 8pt;
      font-weight: bold;
      color: #18181b;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: "Liberation Sans", "DejaVu Sans", sans-serif;
    color: #18181b;
    background: #ffffff;
    margin: 0;
    padding: 0;
    font-size: 9.6pt;
    line-height: 1.42;
  }}
  .doc-banner {{
    background: #f6f3ec;
    border-left: 5px solid #b91c1c;
    border-top: 1px solid #d4cfc2;
    border-right: 1px solid #d4cfc2;
    border-bottom: 1px solid #d4cfc2;
    padding: 12px 16px;
    margin-bottom: 14px;
  }}
  .doc-kicker {{
    font-size: 8pt;
    font-weight: bold;
    letter-spacing: 0.09em;
    color: #b91c1c;
    margin-bottom: 4px;
  }}
  .doc-title {{
    font-family: "DejaVu Serif", Georgia, serif;
    font-size: 16.5pt;
    font-weight: bold;
    color: #18181b;
    margin: 0 0 4px 0;
  }}
  .doc-sub {{
    font-size: 9.2pt;
    color: #3f3f46;
    margin: 0;
  }}
  .timing-bar {{
    display: flex;
    gap: 8px;
    margin-top: 8px;
    flex-wrap: wrap;
    font-size: 8.2pt;
  }}
  .timing-pill {{
    background: #ece7dc;
    border: 1px solid #d4cfc2;
    padding: 2px 7px;
    border-radius: 3px;
    color: #18181b;
    font-weight: bold;
  }}
  .slide-card {{
    background: #fcfbf8;
    border: 1px solid #e4dfd3;
    border-radius: 3px;
    padding: 9px 12px;
    margin-bottom: 11px;
    break-inside: avoid;
    page-break-inside: avoid;
  }}
  .card-head {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 3px;
  }}
  .slide-num {{
    font-size: 7.8pt;
    font-weight: bold;
    padding: 1px 6px;
    border-radius: 2px;
    letter-spacing: 0.04em;
  }}
  .wp-tag {{
    font-size: 7.8pt;
    font-weight: bold;
    letter-spacing: 0.06em;
  }}
  h2 {{
    font-family: "DejaVu Serif", Georgia, serif;
    font-size: 11.4pt;
    color: #18181b;
    margin: 2px 0 6px 0;
  }}
  .point-box {{
    padding: 5px 8px;
    font-size: 9.1pt;
    color: #18181b;
    margin-bottom: 6px;
  }}
  .say-list {{
    margin: 4px 0 6px 0;
    padding-left: 16px;
  }}
  .say-list li {{
    margin-bottom: 3px;
    color: #27272a;
  }}
  code {{
    font-family: "DejaVu Sans Mono", monospace;
    font-size: 8.5pt;
    background: #f1ede4;
    padding: 0 3px;
    border-radius: 2px;
  }}
  .transition-line {{
    font-size: 8.8pt;
    color: #3f3f46;
    border-top: 1px dashed #d4cfc2;
    padding-top: 4px;
    margin-top: 4px;
  }}
  .qa-inline {{
    margin-top: 5px;
    background: #f6f3ec;
    border-left: 2.5px solid #71717a;
    padding: 4px 8px;
    font-size: 8.6pt;
    color: #3f3f46;
  }}
  .viva-section {{
    page-break-before: always;
    break-before: page;
  }}
  .viva-card {{
    background: #f6f3ec;
    border-top: 2.5px solid #18181b;
    border-left: 1px solid #d4cfc2;
    border-right: 1px solid #d4cfc2;
    border-bottom: 1px solid #d4cfc2;
    padding: 8px 11px;
    margin-bottom: 9px;
    break-inside: avoid;
    page-break-inside: avoid;
  }}
  .viva-q {{
    font-weight: bold;
    color: #b91c1c;
    font-size: 9.5pt;
    margin-bottom: 3px;
  }}
  .viva-a {{
    color: #27272a;
    font-size: 9.1pt;
  }}
</style>
</head>
<body>
  <div class="doc-banner">
    <div class="doc-kicker">BITS F464 · MACHINE LEARNING · PRESENTER SCRIPT &amp; VIVA DEFENSE</div>
    <h1 class="doc-title">Speaker Notes: Semi-Supervised Learning Under Label Scarcity &amp; Structured Noise</h1>
    <p class="doc-sub">Matched 1:1 to <code>presentation/main.typ</code> (Cover + 18 Content Slides). Suggested total talk time: <strong>~15 minutes</strong> + Q&amp;A.</p>
    <div class="timing-bar">
      <span class="timing-pill">Intro + Q1–Q4: ~1m05s (Cover, 01)</span>
      <span class="timing-pill">WP1 · Neev: ~3m15s (02–05)</span>
      <span class="timing-pill">WP2 · Shaurya: ~2m35s (06–08)</span>
      <span class="timing-pill">WP3 · Pratyush: ~2m15s (09–11)</span>
      <span class="timing-pill">WP4 · Arnav: ~2m25s (12–14)</span>
      <span class="timing-pill">WP5 + Closing · Tanuj: ~3m25s (15–18)</span>
    </div>
  </div>

  {"".join(cards_html)}

  <div class="viva-section">
    <div class="doc-banner" style="border-left-color:#18181b;">
      <div class="doc-kicker" style="color:#18181b;">CROSS-WP DEFENSE CHEAT SHEET</div>
      <h1 class="doc-title">Top 6 Anticipated Professor Questions &amp; Airtight Answers</h1>
      <p class="doc-sub">Keep this page open during panel Q&amp;A—every answer cites verified experiments across WP1–WP5.</p>
    </div>
    {qa_cards}
  </div>
</body>
</html>
"""


def main():
    HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text(render_html(), encoding="utf-8")
    cmd = [
        "/usr/bin/google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_OUT}",
        HTML_OUT.as_uri(),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    print("Generated:", PDF_OUT, "bytes:", PDF_OUT.stat().st_size)


if __name__ == "__main__":
    main()
