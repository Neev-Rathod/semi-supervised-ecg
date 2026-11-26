#import "@preview/touying:0.8.0": *
#import themes.simple: *

// -----------------------------------------------------------------------------
// Editorial Palette (Archival Paper, Charcoal Ink, Vermilion & Blueprint Cobalt)
// -----------------------------------------------------------------------------
#let paper        = rgb("#f6f3ec")
#let paper-alt    = rgb("#ece7dc")
#let ink          = rgb("#18181b")
#let ink-soft     = rgb("#3f3f46")
#let ink-muted    = rgb("#71717a")
#let rule-color   = rgb("#d4cfc2")
#let vermilion    = rgb("#b91c1c")
#let vermilion-bg = rgb("#f9eaea")
#let cobalt       = rgb("#1d4ed8")
#let cobalt-bg    = rgb("#eaf0fa")
#let forest       = rgb("#166534")
#let forest-bg    = rgb("#e9f4ec")

#let serif-font = ("Libertinus Serif", "New Computer Modern", "Georgia", "DejaVu Serif")
#let sans-font  = ("IBM Plex Sans", "Inter", "Fira Sans", "Liberation Sans", "DejaVu Sans")
#let mono-font  = ("IBM Plex Mono", "JetBrains Mono", "DejaVu Sans Mono")

// -----------------------------------------------------------------------------
// Theme Configuration (16:9 Full-Canvas Proportions)
// -----------------------------------------------------------------------------
#show: simple-theme.with(
  aspect-ratio: "16-9",
  header: none,
  footer: none,
  config-colors(
    primary: ink,
    neutral-lightest: paper,
    neutral-darkest: ink,
  ),
  config-page(
    fill: paper,
    margin: (top: 0.72cm, bottom: 0.88cm, x: 1.25cm),
    footer-descent: 0.18cm,
  ),
)

#set text(font: sans-font, size: 11.4pt, fill: ink-soft)
#show math.equation: set text(font: ("New Computer Modern Math", "STIX Two Math"))
#show raw: set text(font: mono-font, size: 0.86em, fill: ink)
#set par(leading: 0.50em, spacing: 0.42em)
#set list(marker: text(fill: vermilion, weight: "bold", [—]), spacing: 0.34em)
#set enum(spacing: 0.34em)

// -----------------------------------------------------------------------------
// Editorial Layout Helpers (Seamless Figures + Scannable Bottom Takeaways)
// -----------------------------------------------------------------------------
#let make-footer(right-label) = {
  set text(font: mono-font, size: 8.3pt, fill: ink-muted)
  block(
    width: 100%,
    stroke: (top: 0.6pt + rule-color),
    inset: (top: 5pt),
  )[
    #grid(
      columns: (1fr, auto),
      align: (left, right),
      [BITS F464: MACHINE LEARNING #h(0.8em) / #h(0.8em) SEMI-SUPERVISED ECG],
      text(fill: ink, weight: "bold", right-label),
    )
  ]
}

#let content-slide(num, section, title, body) = {
  slide(config: config-page(footer: make-footer(num + " / 18")))[
    #text(font: mono-font, size: 8.6pt, weight: "bold", fill: vermilion, tracking: 0.08em, upper(section))
    #v(0.06em)
    #text(font: serif-font, size: 18.0pt, weight: "bold", fill: ink, title)
    #v(0.12em)
    #line(length: 100%, stroke: 1.15pt + ink)
    #v(0.22em)
    #body
  ]
}

#let seamless-fig(path, height: 9.45cm) = {
  align(center, image(path, width: 100%, height: height, fit: "contain"))
}

#let ruled-col(label, accent-col: ink, bg: none, h: auto, body) = {
  block(
    width: 100%,
    height: h,
    fill: bg,
    stroke: (top: 2.2pt + accent-col),
    inset: if bg != none { (x: 11pt, top: 7pt, bottom: 7pt) } else { (top: 6pt, bottom: 4pt) },
  )[
    #text(font: mono-font, size: 8.5pt, weight: "bold", fill: accent-col, tracking: 0.05em, label)
    #v(0.24em)
    #body
  ]
}

#let eq-strip(body, accent-col: cobalt, bg: cobalt-bg, y-pad: 8pt) = {
  block(
    width: 100%,
    fill: bg,
    stroke: (left: 3pt + accent-col),
    inset: (x: 12pt, y: y-pad),
  )[
    #align(center, body)
  ]
}

// =============================================================================
// COVER SLIDE (Swiss Editorial Monograph)
// =============================================================================
#slide(config: config-page(margin: 0cm, fill: paper, header: none, footer: none))[
  #place(top + left, rect(width: 0.45cm, height: 100%, fill: ink))
  #place(top + left, rect(width: 0.45cm, height: 2.6cm, fill: vermilion))

  #place(top + left)[
    #block(width: 100%, height: 100%, inset: (left: 2.1cm, right: 1.9cm, top: 1.55cm, bottom: 1.35cm))[
      #text(font: mono-font, size: 10pt, weight: "bold", fill: vermilion, tracking: 0.12em)[
        BITS F464 · MACHINE LEARNING · SEMESTER PROJECT PRESENTATION
      ]
      #v(0.75cm)
      #text(font: serif-font, size: 34pt, weight: "bold", fill: ink)[
        #par(leading: 0.38em)[
          Semi-Supervised Learning Under Label Scarcity & Structured Noise
        ]
      ]
      #v(0.40cm)
      #text(font: serif-font, size: 18pt, style: "italic", fill: ink-soft)[
        Discard vs. Correct Strategies on Clinical 12-Lead ECG Waveforms (PTB-XL)
      ]
      #v(0.55cm)
      #rect(width: 56pt, height: 2.8pt, fill: vermilion)
      #v(1fr)
      #line(length: 100%, stroke: 0.9pt + ink)
      #v(0.42cm)
      #grid(
        columns: (1.55fr, 0.95fr),
        gutter: 1.8em,
        [
          #text(font: mono-font, size: 8.5pt, fill: ink-muted, tracking: 0.08em)[WORK PACKAGES & TEAM] \
          #v(0.28em)
          #set text(size: 10.6pt)
          #grid(
            columns: (auto, auto, 1fr),
            column-gutter: 0.7em,
            row-gutter: 0.24em,
            text(font: mono-font, weight: "bold", fill: vermilion)[WP1],
            [*Neev Rathod* #text(font: mono-font, size: 9.2pt, fill: ink-muted)[2024A7PS0487G]],
            text(fill: ink-muted)[Data Pipeline & Sensor Noise],
            text(font: mono-font, weight: "bold", fill: vermilion)[WP2],
            [*Shaurya Suman* #text(font: mono-font, size: 9.2pt, fill: ink-muted)[2024A7PS0589G]],
            text(fill: ink-muted)[Synthetic Lab & Baselines],
            text(font: mono-font, weight: "bold", fill: vermilion)[WP3],
            [*Pratyush Somani* #text(font: mono-font, size: 9.2pt, fill: ink-muted)[2024A7PS0514G]],
            text(fill: ink-muted)[Graph Label Propagation],
            text(font: mono-font, weight: "bold", fill: vermilion)[WP4],
            [*Arnav Gupta* #text(font: mono-font, size: 9.2pt, fill: ink-muted)[2024A7PS0613G]],
            text(fill: ink-muted)[Co-Training & TSVMs],
            text(font: mono-font, weight: "bold", fill: vermilion)[WP5],
            [*Tanuj Yadav* #text(font: mono-font, size: 9.2pt, fill: ink-muted)[2024AAPS0740G]],
            text(fill: ink-muted)[Latent-Noise EM & Audit],
          )
        ],
        [
          #text(font: mono-font, size: 8.5pt, fill: ink-muted, tracking: 0.08em)[COURSE & INSTITUTION] \
          #v(0.28em)
          #text(size: 12.0pt, weight: "bold", fill: ink)[Instructor: Prof. Anand Narasimhamurthy] \
          #v(0.15em)
          #text(size: 11.2pt, fill: ink-soft)[Birla Institute of Technology & Science, Pilani] \
          #text(size: 10.8pt, fill: ink-muted)[K. K. Birla Goa Campus · Nov 2026]
        ],
      )
    ]
  ]
]

// =============================================================================
// SLIDE 01: BIG PICTURE & FOUR QUESTIONS (INSPIRED BY ORIGINAL FLOW)
// =============================================================================
#content-slide("01", "Overview · Motivation & Roadmap", "Can Machine-Generated Hospital Labels Help When Expert Labels Are Scarce?")[
  #eq-strip(accent-col: vermilion, bg: vermilion-bg, y-pad: 9pt)[
    #align(left)[
      #text(font: mono-font, size: 8.6pt, weight: "bold", fill: vermilion, tracking: 0.06em)[THE REAL-WORLD CLINICAL DILEMMA]
      #v(0.16em)
      #text(size: 11.6pt)[
        Hospitals have few *cardiologist-verified ECGs* ($cal(D)_L$, slow and costly) alongside thousands of *automated machine reports* ($cal(D)_U$, abundant but systematically wrong). *Goal:* build accurate diagnostic models using classical ML—testing whether it is better to *discard* noisy machine labels or *model and fix* them.
      ]
    ]
  ]

  #v(0.45em)
  #text(font: mono-font, size: 8.8pt, weight: "bold", fill: ink, tracking: 0.06em)[OUR FOUR SEMI-SUPERVISED CONTENDERS]
  #v(0.18em)
  #grid(
    columns: (1fr, 1fr, 1fr, 1fr),
    gutter: 0.75em,
    ruled-col("WP3 · DISCARD LABELS", accent-col: cobalt, bg: cobalt-bg, h: 2.70cm)[
      *Graph Propagation* \
      #text(size: 10.2pt)[Spread verified Gold labels along nearest ECG neighbors.]
    ],
    ruled-col("WP4 · DISCARD LABELS", accent-col: cobalt, bg: cobalt-bg, h: 2.70cm)[
      *Dual-View Co-Training* \
      #text(size: 10.2pt)[Time & Frequency views teach each other via agreement.]
    ],
    ruled-col("WP4 · DISCARD LABELS", accent-col: cobalt, bg: cobalt-bg, h: 2.70cm)[
      *Transductive SVM* \
      #text(size: 10.2pt)[Push decision margins away from dense ECG clouds.]
    ],
    ruled-col("WP5 · CORRECT LABELS", accent-col: forest, bg: forest-bg, h: 2.70cm)[
      *Latent-Noise EM* \
      #text(size: 10.2pt)[Keep $tilde(y)_U$, learn the software's mistake pattern, and invert it.]
    ],
  )

  #v(1fr)
  #ruled-col("FOUR KEY QUESTIONS THIS PROJECT ANSWERS", accent-col: ink, bg: paper-alt, h: 4.10cm)[
    #set text(size: 11.2pt)
    #v(0.2em)
    #grid(
      columns: (1fr, 1fr),
      column-gutter: 1.5em,
      row-gutter: 0.85em,
      [*Q1 · Data Geometry (WP1):* Do physical wire glitches break feature distances, and can PCA or Mahalanobis repair them?],
      [*Q3 · Discard vs. Correct (WP3–5):* When expert labels are scarce, should we throw noisy machine labels away or fix them?],
      [*Q2 · Failure Laws (WP2):* How fast do standard classifiers collapse under random typos vs. structured confusion?],
      [*Q4 · Software Audit (WP5):* Can EM uncover the hospital software's exact hidden mistakes without extra human labels?],
    )
  ]
  #v(0.10fr)
]

// =============================================================================
// SLIDE 02: WP1 (1/4) — ECG BASICS & FEATURE DESIGN
// =============================================================================
#content-slide("02", "WP1 · Neev Rathod · ECG Data & Feature Engineering", "Why We Convert Raw 10-Second ECG Waves into 84 Clean Summary Features")[
  #seamless-fig("figures/wp1_fig1_ecg_primer_and_artifacts.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("WHY NOT FEED RAW ECG MATRICES DIRECTLY?", accent-col: cobalt, bg: cobalt-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Each ECG is `1,000 × 12` numbers, and heartbeats shift in time across patients. Classical models also overfit `12,000` raw inputs badly when only `~180` Gold records are available.
      ]
    ],
    ruled-col("HOW THIS SERVES WP3, WP4 & WP5", accent-col: forest, bg: forest-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Extracting `84` features once freezes one fair benchmark across WP3–WP5—and splits naturally into *Time/Rhythm* and *Frequency/Wavelet* views needed by WP4 Co-Training.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 03: WP1 (2/4) — DATASET LAYOUT & HIDDEN LABEL BIAS
// =============================================================================
#content-slide("03", "WP1 · Neev Rathod · Dataset Splits & Bias Discovery", "Patient-Safe Splits Expose a Hidden 2.7× Heart-Attack Skew in Machine Labels")[
  #seamless-fig("figures/wp1_fig2_dataset_funnel_and_shift.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("LEAK-FREE CLINICAL SPLIT", accent-col: cobalt, bg: cobalt-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        We keep `16,272` clear single-disease ECGs across `5` classes and separate patients strictly across Train, Val, and Test. Train splits by human verification into Gold ($cal(D)_L$) vs. Untrusted ($cal(D)_U$).
      ]
    ],
    ruled-col("WHY THIS MATTERS FOR THE WHOLE PROJECT", accent-col: vermilion, bg: vermilion-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Machine reports flag *`2.7×` more heart attacks (`MI`)* than doctors (`28%` vs. `10.4%`) while `NORM` dominates (`~55%`). Therefore all models must be judged by *Macro F1*, not accuracy.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 04: WP1 (3/4) — SENSOR ARTIFACTS VS GEOMETRY (Q1)
// =============================================================================
#content-slide("04", "WP1 · Neev Rathod · Hardware Noise Check (Q1)", "Wire Drift Distorts Euclidean Clusters (−5.1 pp), While PCA & Mahalanobis Help")[
  #seamless-fig("figures/wp1_fig4_noise_geometry_redesign.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("WHY TEST CLUSTERING WITHOUT LABELS?", accent-col: ink, bg: paper-alt, h: 2.45cm)[
      #text(size: 10.5pt)[
        Graph methods (WP3) assume nearby ECGs share the same disease. Blind clustering checks *Q1*: do physical glitches (`baseline_drift`, `static_noise`) break distance metrics upfront?
      ]
    ],
    ruled-col("HOW IT GUIDES WP3", accent-col: forest, bg: forest-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Physical artifacts hurt every metric, hitting *Raw Euclidean* hardest. *PCA* cushions sensor drift (`+49%` ARI), and *Mahalanobis* doubles ARI (`2.2×`) when covariance is well estimated.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 05: WP1 (4/4) — CLASS OVERLAP & FORECAST FOR WP3–WP5
// =============================================================================
#content-slide("05", "WP1 · Neev Rathod · Structural Limits", "Heavy Disease Overlap Caps Clustering at ~58%, Predicting WP3's Limit")[
  #seamless-fig("figures/wp1_fig5_pca_and_overlap.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("WHAT OVERLAP TELLS US BEFORE TRAINING", accent-col: cobalt, bg: cobalt-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        While `20` PCs capture `86%` of signal variance, real ECG diseases still crowd heavily together in `(PC1, PC2)`—capping pure unsupervised purity around `~58%`.
      ]
    ],
    ruled-col("TWO PREDICTIONS FOR DOWNSTREAM WORK", accent-col: vermilion, bg: vermilion-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        *(1)* Spreading labels purely by nearest neighbors (WP3) will struggle across boundaries. *(2)* Estimating Mahalanobis on tiny Gold subsets in WP3 will need strong PCA compression.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 06: WP2 (1/3) — SYNTHETIC LAB & UNIFORM BREAKDOWN
// =============================================================================
#content-slide("06", "WP2 · Shaurya Suman · Controlled Noise Lab", "Why We Built a Synthetic Lab: Trees Memorize Noise & Self-Training Backfires")[
  #seamless-fig("figures/wp2_fig2_uniform_breakdown_small_multiples.png", height: 9.40cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("WHY USE A SYNTHETIC MANIFOLD?", accent-col: ink, bg: paper-alt, h: 2.50cm)[
      #text(size: 10.4pt)[
        Real hospital reports ($cal(D)_U$) never reveal true labels or let us vary error rate `ε`. Our `50-D` lab tests *5 model families* directly mirroring WP3–WP5 (*k-NN*, *DT/SVM*, *GNB/LR*).
      ]
    ],
    ruled-col("THREE LESSONS USED DIRECTLY IN WP4 & WP5", accent-col: vermilion, bg: vermilion-bg, h: 2.50cm)[
      #text(size: 10.4pt)[
        *(1)* Unpruned trees shatter (`−38.5%`, forcing WP4's shallow `depth=4` cap); *(2)* SVM hides margin bloat (`96%` SVs); *(3)* Single-model self-training harms `GNB` (`−8.3 pp`), proving WP4 needs two views.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 07: WP2 (2/3) — UNIFORM VS ASYMMETRIC CONFUSION (Q2)
// =============================================================================
#content-slide("07", "WP2 · Shaurya Suman · Noise Physics (Q2)", "Random Noise Spares Voting, But Systematic Confusion Collapses Every Model")[
  #seamless-fig("figures/wp2_fig4_three_noise_types.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("RANDOM TYPOS VS. HOSPITAL-LIKE BIAS", accent-col: vermilion, bg: vermilion-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        When typos scatter evenly across classes (`Panel A`), truth still outvotes errors. When specific pairs get systematically swapped (`Panel B`), wrong labels outvote truth—crashing *every model*.
      ]
    ],
    ruled-col("WHY THIS PROVES WP5 IS NECESSARY", accent-col: cobalt, bg: cobalt-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Hospitals have *structured* biases (like over-flagging `MI`). Simple models cannot survive systematic confusion—so WP5 explicitly learns the `5 × 5` mistake matrix using WP2's lab to validate it.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 08: WP2 (3/3) — REAL PTB-XL REALITY CHECK
// =============================================================================
#content-slide("08", "WP2 · Shaurya Suman · Real ECG Reality Check", "On Real PTB-XL, Structured MI Bias Shatters Gaussian NB (−9.7 pp)")[
  #seamless-fig("figures/wp2_fig5_ptbxl_reality_check.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("SYNTHETIC RESILIENCE BREAKS ON REAL SHIFT", accent-col: vermilion, bg: vermilion-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Under synthetic random noise, `GNB` looked toughest. On real ECGs, pooling unverified hospital reports *crashes `GNB` (`−9.7 pp`)* because the `28% MI` over-alarm skews class priors.
      ]
    ],
    ruled-col("THE BAR WP3–WP5 MUST BEAT", accent-col: cobalt, bg: cobalt-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Simple *Balanced Logistic Regression* on Gold data alone sets a strong supervised floor (`0.40 → 0.49` val F1), while naive `self_training` stalls—giving WP3–WP5 an honest target.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 09: WP3 (1/3) — GRAPH LABEL PROPAGATION (APPROACH 1)
// =============================================================================
#content-slide("09", "WP3 · Pratyush Somani · Approach 1: Graph Propagation", "Spreading Verified Labels Over an ECG Network Works Best on Small Graphs")[
  #seamless-fig("figures/wp3_fig1_metric_and_k.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("THE IDEA · DISCARD ỹ_U & CONNECT SIMILAR ECGS", accent-col: cobalt, bg: cobalt-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Throwing away noisy hospital labels, we link each patient to `k` nearest ECGs and let Gold labels flow across neighbors (`900` sweeps). Tight neighborhoods (`k = 3`) avoid blurring classes.
      ]
    ],
    ruled-col("RESOLVING WP1'S MAHALANOBIS PUZZLE", accent-col: forest, bg: forest-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Inverting `84 × 84` covariance from scarce Gold slices fails (`0.211`), matching Euclidean *only* once compressed to `PCA = 5`—directly confirming WP1's Slide 05 warning.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 10: WP3 (2/3) — CONTROL TESTS VS SUPERVISED BASELINES
// =============================================================================
#content-slide("10", "WP3 · Pratyush Somani · Controls & Baselines", "Adding Unlabeled ECGs Fails to Beat Same-Space k-NN or Linear Classifiers")[
  #seamless-fig("figures/wp3_fig2_test_comparison.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("DID THE UNLABELED POOL HELP? (CONTROL)", accent-col: cobalt, bg: cobalt-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Comparing Graph LP against Gold-only `k-NN` in the *exact same 5-D space* on held-out Fold 10 gives zero consistent lift (`Panel B`)—extra unlabeled neighbors don't sharpen ECG boundaries.
      ]
    ],
    ruled-col("BEHIND SIMPLE SUPERVISED MODELS", accent-col: vermilion, bg: vermilion-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Trained strictly on clean Gold records, *RBF-SVM* and *Logistic Regression* beat Graph LP by `0.09–0.13` F1 everywhere—even without class weighting.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 11: WP3 (3/3) — DIAGNOSIS & ELIMINATION
// =============================================================================
#content-slide("11", "WP3 · Pratyush Somani · Verdict on Approach 1", "Why Pure Neighbor Smoothing Fails on Overlapping ECGs — Eliminating WP3")[
  #seamless-fig("figures/wp3_fig3_class_collapse.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("WHAT WENT WRONG AT THE CLASS LEVEL", accent-col: vermilion, bg: vermilion-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Because diseases overlap (`WP1` purity `~58%`), isotropic diffusion floods minority heart conditions (`STTC`, `MI`) with surrounding majority healthy ECGs (`~55% NORM`).
      ]
    ],
    ruled-col("WHY THIS NEGATIVE RESULT IS VALUABLE", accent-col: forest, bg: forest-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        It proves passive distance geometry alone cannot solve clinical ECGs—cleanly eliminating Approach 1 for *Q3* and steering us to *discriminative views (WP4)* and *noise modeling (WP5)*.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 12: WP4 (1/3) — CO-TRAINING (APPROACH 2)
// =============================================================================
#content-slide("12", "WP4 · Arnav Gupta · Approach 2: Dual-View Co-Training", "Two Separate ECG Views Teaching Each Other Excel When Labels Are Scarce")[
  #seamless-fig("figures/wp4_fig1_cotraining_curves.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("HOW TWO VIEWS STOP SELF-CONTAMINATION", accent-col: cobalt, bg: cobalt-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Still discarding `ỹ_U`, depth-4 boosted trees train separately on *Time* and *Frequency* features—transferring unlabeled pseudo-labels *only when both views confidently agree*.
      ]
    ],
    ruled-col("WHERE IT WORKS BEST (AND ITS CEILING)", accent-col: forest, bg: forest-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Gives strong scarcity gains (`+0.071` F1 at `5%` Gold, beating even joint `84-D` training). By `50%` Gold (`4,505` records), full supervised trees overtake pseudo-labels.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 13: WP4 (2/3) — CO-TRAINING DIAGNOSTICS
// =============================================================================
#content-slide("13", "WP4 · Arnav Gupta · Inside Co-Training", "Co-Training Rescues Rare Arrhythmias Because Both Views Stay Complementary")[
  #seamless-fig("figures/wp4_fig2_cotraining_diagnostics.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("RESCUING RARE HEART CONDITIONS (η = 5%)", accent-col: cobalt, bg: cobalt-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Unlike Graph LP which erased minorities, Co-Training lifts every pathology at `450` Gold records—nearly doubling rare `HYP` (`+0.14`) and boosting `STTC` (`+0.12`).
      ]
    ],
    ruled-col("WHY THE TWO VIEWS ACTUALLY HELP EACH OTHER", accent-col: forest, bg: forest-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        *View 2* (Frequency/Wavelets) catches localized waveform spikes best (`+6–8 pp` lead), while `~78%` cross-view agreement leaves `~22%` healthy diversity so views correct one another.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 14: WP4 (3/3) — TRANSDUCTIVE SVM (APPROACH 3)
// =============================================================================
#content-slide("14", "WP4 · Arnav Gupta · Approach 3: Transductive SVM", "Filtering Confident Unlabeled ECGs Lifts RBF-SVM Margins Everywhere")[
  #seamless-fig("figures/wp4_fig3_tsvm_results.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("KEEPING MARGINS CLEAN UNDER OVERLAP", accent-col: forest, bg: forest-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        To prevent WP2-style support-vector bloat in overlapping space, TSVM filters to the *top `35%` margin-confident pool*—lifting balanced RBF-SVM consistently across all Gold fractions.
      ]
    ],
    ruled-col("WHAT REMAINS UNUSED BEFORE WP5", accent-col: cobalt, bg: cobalt-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        WP4 proves discriminative SSL beats Graph LP easily (`0.46` vs. `0.31` at `10%` Gold). Yet both WP3 and WP4 *still throw away 3,968 machine labels* that are right ~80–90% of the time.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 15: WP5 (1/3) — LATENT NOISE EM (APPROACH 4)
// =============================================================================
#content-slide("15", "WP5 · Tanuj Yadav · Approach 4: Latent-Noise EM", "Instead of Discarding Machine Labels, Model and Invert Their Mistake Pattern")[
  #seamless-fig("figures/wp5_fig1_em_recovery.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("HOW ANCHORED EM WORKS SIMPLY", accent-col: cobalt, bg: cobalt-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Clean Gold anchors ($cal(D)_L$) seed a baseline classifier, while EM jointly learns a `5 × 5` hospital confusion table `T` on $cal(D)_U$—downweighting false alarms rather than discarding logs.
      ]
    ],
    ruled-col("PROVEN CHANNEL RECOVERY (VIA WP2 LAB)", accent-col: forest, bg: forest-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Because real hospital data hides true `D_U` labels, we verify on WP2's asymmetric generator: EM cuts matrix recovery error by *`63%`* (`0.364 → 0.135`) as pool size grows.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 16: WP5 (2/3) — DISCARD VS CORRECT VERDICT (Q3)
// =============================================================================
#content-slide("16", "WP5 · Tanuj Yadav · Discard vs. Correct Verdict (Q3)", "Modeling Noisy Labels Wins Under Scarcity (0.462 at 2% Gold) & Extra Noise")[
  #seamless-fig("figures/wp5_fig2_discard_vs_correct.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("STRONGEST WHEN EXPERT LABELS ARE SCARCE", accent-col: vermilion, bg: vermilion-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        EM wins `20/20` benchmark grid cells (`0.462` F1 with just `180` Gold ECGs!) and holds above `0.41` even after adding `+45%` extra random label flips to the machine pool.
      ]
    ],
    ruled-col("COMPLETE Q3 DECISION LAW", accent-col: forest, bg: forest-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        *Scarcity (`≤ 10%` Gold):* Keeping & inverting machine logs (*EM*) clearly beats discarding them (Co-Training / TSVM / LP). *Abundance (`≥ 20%`):* nonlinear margins catch up.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 17: WP5 (3/3) — CLINICAL SOFTWARE AUDIT (Q4)
// =============================================================================
#content-slide("17", "WP5 · Tanuj Yadav · Hospital Software Audit (Q4)", "Learned Confusion Matrix T̂ Exposes Why Automated ECGs Over-Alarm MI")[
  #seamless-fig("figures/wp5_fig3_clinical_audit.png", height: 9.45cm)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    ruled-col("OPENING THE BLACK BOX OF MACHINE REPORTS", accent-col: vermilion, bg: vermilion-bg, h: 2.45cm)[
      #text(size: 10.5pt)[
        Auditing `3,968` hospital logs reveals high detection on `CD (96.5%)` & `MI (95.8%)`, weaker `HYP (79.2%)`, and two big biases: *`9.4%` of healthy* & *`9.2%` of STTC* ECGs get flagged as `MI`.
      ]
    ],
    ruled-col("CLOSING THE ENTIRE PROJECT LOOP", accent-col: ink, bg: paper-alt, h: 2.45cm)[
      #text(size: 10.5pt)[
        Without any extra human labels, EM explains *WP1's `2.7× MI` spike* (`Slide 03`) and *WP2's `GNB` collapse* (`Slide 08`): hospital rules deliberately over-alarm heart attacks for safety.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 18: SYNTHESIS & PRACTICAL TAKEAWAYS
// =============================================================================
#content-slide("18", "Synthesis · Answers & Decision Guide", "What Every Work Package Taught Us — And Which Method to Use")[
  #v(0.20fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.15em,
    row-gutter: 0.90em,
    ruled-col("Q1 · DATA & NOISE GEOMETRY (WP1 & WP3)", accent-col: cobalt, bg: cobalt-bg, h: 4.10cm)[
      #text(size: 11.2pt)[
        *Finding:* Wire drift hurts raw distances (`−5.1 pp`); PCA cushions noise and Mahalanobis helps only with enough clean data (`PCA=5` on scarce Gold). \
        *Why Useful:* Tells us upfront that overlapping ECGs (`~58%` purity) limit pure clustering.
      ]
    ],
    ruled-col("Q2 · HOW CLASSIFIERS BREAK (WP2)", accent-col: vermilion, bg: vermilion-bg, h: 4.10cm)[
      #text(size: 11.2pt)[
        *Finding:* Random flips collapse unpruned trees (`−38.5%`) and bloat SVM SVs (`96%`), while *structured confusion crashes every model*—and `28% MI` skew cuts PTB-XL `GNB −9.7 pp`. \
        *Why Useful:* Motivated depth caps (`WP4`) and noise modeling (`WP5`).
      ]
    ],
    ruled-col("Q3 · DISCARD VS. CORRECT (WP3–WP5)", accent-col: forest, bg: forest-bg, h: 4.10cm)[
      #text(size: 11.2pt)[
        *Finding:* Graph LP fails under class overlap; Co-Training lifts scarce views (`+0.071` at `5%`); TSVM lifts balanced SVM everywhere (`0.488` at `20%`); *EM wins scarcity (`0.462` at `2%`)*. \
        *Why Useful:* Clear rule matching method to budget.
      ]
    ],
    ruled-col("Q4 · AUDITING LEGACY SOFTWARE (WP5)", accent-col: ink, bg: paper-alt, h: 4.10cm)[
      #text(size: 11.2pt)[
        *Finding:* EM cuts synthetic channel error `63%` and spots real hospital bias (`NORM → MI 9.4%`, `STTC → MI 9.2%`, `HYP → NORM 6.2%`). \
        *Why Useful:* Turns biased logs into a free clinical software audit.
      ]
    ],
  )

  #v(1fr)
  #eq-strip(accent-col: ink, bg: paper-alt, y-pad: 10pt)[
    #text(size: 11.4pt)[
      *Practical Takeaway:* *Use Latent-Noise EM* whenever expert labels are scarce ($eta <= 10%$) and noisy logs retain signal; switch to *TSVM or boosted trees* only once verified labels are abundant ($eta >= 20%$).
    ]
  ]
  #v(0.10fr)
]

// =============================================================================
// REFERENCES SLIDE (Balanced Full-Canvas Layout)
// =============================================================================
#slide(config: config-page(footer: make-footer("REFERENCES")))[
  #text(font: mono-font, size: 8.6pt, weight: "bold", fill: vermilion, tracking: 0.08em)[BIBLIOGRAPHY]
  #v(0.06em)
  #text(font: serif-font, size: 18.0pt, weight: "bold", fill: ink)[References]
  #v(0.12em)
  #line(length: 100%, stroke: 1.15pt + ink)
  #v(0.30fr)

  #grid(
    columns: (1fr, 1fr),
    gutter: 1.25em,
    ruled-col("FOUNDATIONAL ML & PTB-XL DATASET [1–5]", accent-col: cobalt, bg: cobalt-bg, h: 9.2cm)[
      #set text(size: 10.8pt)
      #v(0.25em)
      #grid(
        columns: (2.5em, 1fr),
        column-gutter: 0.45em,
        row-gutter: 1.15em,
        text(font: mono-font, weight: "bold", fill: cobalt)[\[1\]],
        [S. Rogers and M. Girolami, _A First Course in Machine Learning_, 2nd ed., CRC Press, 2015.],
        text(font: mono-font, weight: "bold", fill: cobalt)[\[2\]],
        [P.-N. Tan, M. Steinbach, A. Karpatne, and V. Kumar, _Introduction to Data Mining_, 2nd ed., Pearson, 2018.],
        text(font: mono-font, weight: "bold", fill: cobalt)[\[3\]],
        [C. M. Bishop, _Pattern Recognition and Machine Learning_, Springer, 2006.],
        text(font: mono-font, weight: "bold", fill: cobalt)[\[4\]],
        [K. P. Murphy, _Probabilistic Machine Learning: An Introduction_, MIT Press, 2022.],
        text(font: mono-font, weight: "bold", fill: cobalt)[\[5\]],
        [P. Wagner et al., "PTB-XL, a large publicly available electrocardiography dataset," _Scientific Data_, vol. 7, no. 1, Art. no. 154, 2020.],
      )
    ],
    ruled-col("SEMI-SUPERVISED & NOISE MODELING CORE [6–10]", accent-col: vermilion, bg: vermilion-bg, h: 9.2cm)[
      #set text(size: 10.8pt)
      #v(0.25em)
      #grid(
        columns: (2.5em, 1fr),
        column-gutter: 0.45em,
        row-gutter: 1.15em,
        text(font: mono-font, weight: "bold", fill: vermilion)[\[6\]],
        [A. P. Dawid and A. M. Skene, "Maximum likelihood estimation of observer error-rates using the EM algorithm," _JRSS Series C_, vol. 28, no. 1, pp. 20–28, 1979.],
        text(font: mono-font, weight: "bold", fill: vermilion)[\[7\]],
        [X. Zhu, Z. Ghahramani, and J. D. Lafferty, "Semi-supervised learning using Gaussian fields and harmonic functions," in _ICML_, 2003, pp. 912–919.],
        text(font: mono-font, weight: "bold", fill: vermilion)[\[8\]],
        [A. Blum and T. Mitchell, "Combining labeled and unlabeled data with co-training," in _COLT_, ACM, 1998, pp. 92–100.],
        text(font: mono-font, weight: "bold", fill: vermilion)[\[9\]],
        [T. Joachims, "Transductive inference for text classification using support vector machines," in _ICML_, 1999, pp. 200–209.],
        text(font: mono-font, weight: "bold", fill: vermilion)[\[10\]],
        [A. Y. Ng and M. I. Jordan, "On discriminative vs. generative classifiers: A comparison of logistic regression and naive Bayes," in _NIPS_, vol. 14, 2001.],
      )
    ],
  )

  #v(1fr)
  #eq-strip(accent-col: ink, bg: paper-alt, y-pad: 9pt)[
    #text(size: 10.6pt)[
      *Reproducibility:* All experiments share `shared/data_utils.py` & `shared/metrics.py` across modular packages `wp1_data_pipeline/` through `wp5_latent_noise_em/`.
    ]
  ]
  #v(0.10fr)
]
