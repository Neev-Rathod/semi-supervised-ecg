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
// Theme Configuration (Balanced Full-Canvas Proportions)
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
    margin: (top: 0.85cm, bottom: 1.05cm, x: 1.35cm),
    footer-descent: 0.22cm,
  ),
)

#set text(font: sans-font, size: 12.2pt, fill: ink-soft)
#show math.equation: set text(font: ("New Computer Modern Math", "STIX Two Math"))
#show raw: set text(font: mono-font, size: 0.88em, fill: ink)
#set par(leading: 0.56em, spacing: 0.48em)
#set list(marker: text(fill: vermilion, weight: "bold", [—]), spacing: 0.42em)
#set enum(spacing: 0.42em)

// -----------------------------------------------------------------------------
// Editorial Layout Helpers (Hairlines, Rules, Bars & Plot Frames)
// -----------------------------------------------------------------------------
#let make-footer(right-label) = {
  set text(font: mono-font, size: 8.5pt, fill: ink-muted)
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
  slide(config: config-page(footer: make-footer(num + " / 17")))[
    #text(font: mono-font, size: 9.0pt, weight: "bold", fill: vermilion, tracking: 0.08em, upper(section))
    #v(0.10em)
    #text(font: serif-font, size: 21.5pt, weight: "bold", fill: ink, title)
    #v(0.18em)
    #line(length: 100%, stroke: 1.15pt + ink)
    #v(0.48em)
    #v(0.65fr)
    #body
    #v(0.65fr)
  ]
}

#let ruled-col(label, accent-col: ink, bg: none, body) = {
  block(
    width: 100%,
    fill: bg,
    stroke: (top: 2.2pt + accent-col),
    inset: if bg != none { (x: 10pt, top: 7pt, bottom: 7pt) } else { (top: 6pt, bottom: 2pt) },
  )[
    #text(font: mono-font, size: 8.8pt, weight: "bold", fill: accent-col, tracking: 0.05em, label)
    #v(0.28em)
    #body
  ]
}

#let eq-strip(body, accent-col: cobalt, bg: cobalt-bg) = {
  block(
    width: 100%,
    fill: bg,
    stroke: (left: 3pt + accent-col),
    inset: (x: 10pt, y: 6pt),
  )[
    #align(center, body)
  ]
}

#let fig-frame(path, height: 5.5cm, caption: none) = {
  block(
    width: 100%,
    fill: white,
    stroke: 0.7pt + rule-color,
    radius: 2pt,
    inset: (x: 5pt, y: 4pt),
  )[
    #align(center, image(path, width: 100%, height: height, fit: "contain"))
    #if caption != none [
      #v(0.16em)
      #align(center, text(size: 9.3pt, fill: ink-muted, caption))
    ]
  ]
}

#let metric-bar(label, pct, val-str, fill-col, label-w: 4.0em, val-w: 3.8em) = {
  let bar-pct = calc.min(100%, calc.max(0%, pct))
  grid(
    columns: (label-w, 1fr, val-w),
    gutter: 0.5em,
    align: (left + horizon, left + horizon, right + horizon),
    text(font: mono-font, size: 9.4pt, weight: "bold", fill: ink, label),
    box(width: 100%, height: 9pt, fill: paper-alt)[
      #if bar-pct > 0% [
        #rect(width: bar-pct, height: 100%, fill: fill-col)
      ]
    ],
    text(font: mono-font, size: 9.4pt, weight: "bold", fill: fill-col, val-str),
  )
}

// =============================================================================
// COVER SLIDE (Swiss Editorial Monograph — Excluded from 17-Slide Count)
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
      #text(font: serif-font, size: 35pt, weight: "bold", fill: ink)[
        #par(leading: 0.38em)[
          Semi-Supervised Learning Under Label Scarcity & Structured Noise
        ]
      ]
      #v(0.42cm)
      #text(font: serif-font, size: 18.5pt, style: "italic", fill: ink-soft)[
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
            text(fill: ink-muted)[Synthetic Suite & Baselines],
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
          #text(size: 12.2pt, weight: "bold", fill: ink)[Instructor: Prof. Anand Narasimhamurthy] \
          #v(0.15em)
          #text(size: 11.4pt, fill: ink-soft)[Birla Institute of Technology & Science, Pilani] \
          #text(size: 11.0pt, fill: ink-muted)[K. K. Birla Goa Campus · Nov 2026]
        ],
      )
    ]
  ]
]
// =============================================================================
// WP1 helper: small pipeline box
// =============================================================================
#let pipe-step(tag, title, body, accent-col: ink) = block(
  width: 100%,
  fill: paper-alt,
  stroke: (top: 2.2pt + accent-col),
  inset: (x: 8pt, y: 7pt),
)[
  #text(font: mono-font, size: 8.4pt, weight: "bold", fill: accent-col, tracking: 0.05em, tag)
  #v(0.15em)
  #text(size: 11.2pt, weight: "bold", fill: ink, title) \
  #text(size: 9.8pt, body)
]

#let pipe-arrow = text(size: 14pt, fill: ink-muted)[$arrow.r$]
// =============================================================================
// WP1 helper: question card
// =============================================================================
#let q-card(tag, title, body, accent-col: ink) = block(
  width: 100%,
  fill: paper-alt,
  stroke: (top: 2.2pt + accent-col),
  inset: (x: 10pt, y: 8pt),
)[
  #text(font: mono-font, size: 9.2pt, weight: "bold", fill: accent-col, tracking: 0.05em, tag)
  #v(0.2em)
  #text(size: 12.4pt, weight: "bold", fill: ink, title) \
  #v(0.1em)
  #text(size: 11.2pt, body)
]

// =============================================================================
// SLIDE 01: WP1 — PROBLEM & QUESTIONS
// =============================================================================
#content-slide("01", "WP1 · Neev Rathod · Problem & Questions", "Learning When Good Labels Are Scarce or Noisy")[
  #eq-strip(accent-col: vermilion, bg: vermilion-bg)[
    #align(left)[
      #text(font: mono-font, size: 8.6pt, weight: "bold", fill: vermilion, tracking: 0.06em)[PROBLEM STATEMENT]
      #v(0.2em)
      #text(size: 12.2pt)[
        Modern models are trained on huge labelled datasets. But in many fields, such as *medicine, rare-disease diagnosis, industrial fault detection, satellite imagery and low-resource languages*, trusted labels are scarce and expensive, and the cheap labels we can get are noisy. *Goal:* build a reliable model from a little trusted data plus a lot of imperfect data.
      ]
    ]
  ]

  #v(1fr)
  #grid(
    columns: (1fr, 1fr, 1fr),
    gutter: 1.0em,
    ruled-col("TRUSTED LABELS ARE SCARCE", accent-col: forest, bg: forest-bg)[
      #text(size: 10.8pt)[Expert-verified labels are accurate but slow and costly, so we only have a small amount.]
    ],
    ruled-col("CHEAP LABELS ARE NOISY", accent-col: vermilion, bg: vermilion-bg)[
      #text(size: 10.8pt)[Automatic labels come in bulk, but contain mistakes that are often systematic, not random.]
    ],
    ruled-col("UNLABELLED DATA IS PLENTIFUL", accent-col: cobalt, bg: cobalt-bg)[
      #text(size: 10.8pt)[Raw data is abundant. We must learn from it without being misled by bad labels.]
    ],
  )

  #v(1fr)
  #text(font: mono-font, size: 9.4pt, weight: "bold", fill: ink, tracking: 0.06em)[QUESTIONS THIS PROJECT ANSWERS]
  #v(0.2em)
  #line(length: 100%, stroke: 0.8pt + ink)
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 0.9em,
    row-gutter: 0.9em,
    q-card("Q1 · DATA", "How does noise affect the data?", [Does noise change the structure of the data, and can scaling and PCA help?], accent-col: cobalt),
    q-card("Q3 · METHODS", "Which method works best?", [How does performance change as the amount of trusted data grows, and is it better to discard noisy labels or correct them?], accent-col: forest),
    q-card("Q2 · BREAKDOWN", "How fast do models fail?", [How quickly do standard classifiers degrade as label noise increases?], accent-col: vermilion),
    q-card("Q4 · MISTAKES", "Can we find the pattern?", [Can we uncover the systematic mistakes in the cheap labels themselves?], accent-col: ink),
  )
]
// =============================================================================
// SLIDE 02: WP1 — DATA, FEATURES & PCA
// =============================================================================
#content-slide("02", "WP1 · Neev Rathod · Data & Features", "From Raw ECGs to 84 Features, Then PCA")[
  #grid(
    columns: (1fr, auto, 1fr, auto, 1fr, auto, 1fr),
    column-gutter: 0.45em,
    align: horizon,
    pipe-step("1 · DATA", "PTB-XL ECGs", [`21,837` recordings, 12 leads, 10 s each (`1000 × 12`). Gold set = `9,010` verified.], accent-col: forest),
    pipe-arrow,
    pipe-step("2 · FEATURES", "84 hand-crafted", [`42` time/shape (HRV, Hjorth) + `42` frequency/wavelet (Welch PSD, `db4`).], accent-col: cobalt),
    pipe-arrow,
    pipe-step("3 · CLEAN", "Standardize", [Zero NaN/Inf left; every feature on the same scale.], accent-col: ink),
    pipe-arrow,
    pipe-step("4 · PCA", "Compress to 20 PCs", [Keeps about `86%` of the variance.], accent-col: vermilion),
  )

  #v(1fr)
  #grid(
    columns: (1.1fr, 1fr),
    gutter: 1.3em,
    align: horizon,
    [
      #align(center, image("plots/wp1_fig1a_ecg_primer.png", width: 100%, height: 5.05cm, fit: "contain"))
      #v(0.10em)
      #align(center, text(size: 8.8pt, fill: ink-muted)[ECG waves, R-peaks, and HRV (schematic).])
    ],
    [
      #align(center, image("plots/pca_explained_variance.png", width: 100%, height: 5.05cm, fit: "contain"))
      #v(0.10em)
      #align(center, text(size: 8.8pt, fill: ink-muted)[Cumulative variance explained by principal components.])
    ],
  )

  #v(1fr)
  #ruled-col("WHAT PCA TELLS US", accent-col: ink)[
    #set text(size: 10.8pt)
    - *Fast compression:* `5` PCs capture `~52%`, `10` capture `~70%`, `20` capture `~86%`.
    - *Why 20:* `90%` would need `~30–35` PCs. `20` keeps most of the information and filters drift and noise.
    - *Result:* a clean `21,837 × 84` matrix, ready for all later methods.
  ]
]

// =============================================================================
// SLIDE 03: WP1 — K-MEANS & WHAT IT TELLS US (Q1)
// =============================================================================
#content-slide("03", "WP1 · Neev Rathod · k-Means (Q1)", "Clustering Shows Overlapping Classes and the Cost of Sensor Noise")[
  #grid(
    columns: (1.15fr, 1fr),
    gutter: 1.0em,
    [
      #align(center, image("plots/noise_cluster_purity.png", width: 100%, height: 4.55cm, fit: "contain"))
      #v(0.08em)
      #align(center, text(size: 8.6pt, fill: ink-muted)[k-Means ($k=5$) purity on clean vs. noisy ECGs (baseline drift, static).])
      #v(0.2em)
      #ruled-col("PURITY & ADJUSTED RAND INDEX", accent-col: ink)[
        #set text(size: 9.6pt)
        #table(
          columns: (1.6fr, 0.8fr, 0.8fr),
          stroke: none,
          inset: (x: 3pt, y: 2.5pt),
          fill: (x, y) => if y == 3 or y == 6 { cobalt-bg } else { none },
          table.hline(stroke: 1.1pt + ink),
          table.header([*Variant*], [*Purity*], [*ARI*]),
          table.hline(stroke: 0.5pt + ink),
          [Raw + Euclidean], [0.5778], [0.0486],
          [Raw + Cosine], [0.5589], [0.0416],
          [*Raw + Mahalanobis*], [0.5646], text(fill: cobalt, weight: "bold")[0.1081],
          [PCA + Euclidean], [0.5777], [0.0723],
          [PCA + Cosine], [0.5589], [0.0427],
          [*PCA + Mahalanobis*], [0.5771], [0.0814],
          table.hline(stroke: 1.1pt + ink),
        )
      ]
      #v(0.2em)
      #ruled-col("WHAT WE DID", accent-col: cobalt, bg: cobalt-bg)[
        #set text(size: 9.6pt)
        Ran k-Means with `5` clusters (one per diagnosis) on gold folds 1–8, using `3` distances (Euclidean, Cosine, Mahalanobis) on raw and PCA features. *Purity* = how well clusters match the true diagnoses.
      ]
    ],
    [
      #align(center, image("plots/wp1_fig5b_feature_overlap.png", width: 100%, height: 5.35cm, fit: "contain"))
      #v(0.08em)
      #align(center, text(size: 8.6pt, fill: ink-muted)[PTB-XL feature overlap in the first two principal components.])
      #v(0.22em)
      #ruled-col("WHAT IT TELLS US", accent-col: vermilion, bg: vermilion-bg)[
        #set text(size: 10.0pt)
        - *Purity varies with signal quality:* Clean-flagged records have higher purity than records flagged for baseline drift or static noise across the tested variants.
        - *PCA doesn't clearly improve purity:* Dimensionality reduction alone doesn't consistently improve cluster quality.
        - *Classes overlap:* Low ARI values suggest the clusters don't strongly separate all five diagnoses.
        - *So:* These are clues about the feature space—not proof that artifacts caused the differences or that a diagnostic model will perform the same way. This points to the need for labels, leading to semi-supervised learning.
      ]
    ],
  )
]
// SLIDE 05: WP2 — CONTROLLED LAB & UNIFORM BREAKDOWN (Q2)
// =============================================================================
#content-slide("05", "WP2 · Shaurya Suman · Controlled Noise Lab", "Controlled Noise Lab: How Classifiers & Self-Training Fail")[
  #align(center, image("plots/wp2_fig2_uniform_breakdown_small_multiples.png", width: 100%, height: 8.3cm, fit: "contain"))
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    block(width: 100%, height: 2.75cm, fill: paper-alt, stroke: (top: 2.2pt + ink), inset: (x: 10pt, y: 7pt))[
      #text(font: mono-font, size: 8.6pt, weight: "bold", fill: ink, tracking: 0.05em)[WHY BUILD A SYNTHETIC MANIFOLD?]
      #v(0.22em)
      #text(size: 10.6pt)[
        Real hospital reports ($cal(D)_U$) hide true labels and prevent sweeping noise `ε`. Our `50-D` lab tests *5 model families* directly mirroring WP3–WP5 (*k-NN*, *DT/SVM*, *GNB/LR*).
      ]
    ],
    block(width: 100%, height: 2.75cm, fill: vermilion-bg, stroke: (top: 2.2pt + vermilion), inset: (x: 10pt, y: 7pt))[
      #text(font: mono-font, size: 8.6pt, weight: "bold", fill: vermilion, tracking: 0.05em)[LESSONS APPLIED IN WP4 & WP5]
      #v(0.22em)
      #text(size: 10.6pt)[
        *(1)* Unpruned trees shatter (`−38.5%`, forcing WP4's depth-4 cap); *(2)* SVM hides margin bloat (`96%` SVs); *(3)* Single-model self-training harms `GNB` (`−8.3 pp`), requiring WP4's two views.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 06: WP2 — UNIFORM VS ASYMMETRIC & BOUNDARY NOISE (Q2)
// =============================================================================
#content-slide("06", "WP2 · Shaurya Suman · Noise Physics (Q2)", "Random Noise Spares Voting; Structured Bias Breaks Everyone")[
  #align(center, image("plots/wp2_fig4_three_noise_types.png", width: 100%, height: 8.4cm, fit: "contain"))
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    block(width: 100%, height: 2.65cm, fill: vermilion-bg, stroke: (top: 2.2pt + vermilion), inset: (x: 10pt, y: 7pt))[
      #text(font: mono-font, size: 8.6pt, weight: "bold", fill: vermilion, tracking: 0.05em)[RANDOM TYPOS VS. STRUCTURED PAIR BIAS]
      #v(0.22em)
      #text(size: 10.6pt)[
        When flips scatter uniformly (`Panel A`), truth still outvotes errors. When pairs get systematically confused (`Panel B`), wrong labels outvote truth—crashing *every classifier* (`SVM`, `LR`, `GNB`).
      ]
    ],
    block(width: 100%, height: 2.65cm, fill: cobalt-bg, stroke: (top: 2.2pt + cobalt), inset: (x: 10pt, y: 7pt))[
      #text(font: mono-font, size: 8.6pt, weight: "bold", fill: cobalt, tracking: 0.05em)[WHY THIS PROVES WP5 IS NECESSARY]
      #v(0.22em)
      #text(size: 10.6pt)[
        Real clinics have *structured* biases (like over-flagging `MI`). Simple classifiers cannot survive asymmetric flips—so WP5 explicitly learns the `5 × 5` matrix $T$, validated on this lab.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 07: WP2 — REAL PTB-XL REALITY CHECK
// =============================================================================
#content-slide("07", "WP2 · Shaurya Suman · Real ECG Reality Check", "PTB-XL Reality Check: MI Bias Shatters Gaussian NB (−9.7 pp)")[
  #align(center, image("plots/wp2_fig5_ptbxl_reality_check.png", width: 100%, height: 8.4cm, fit: "contain"))
  #v(1fr)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.0em,
    block(width: 100%, height: 2.65cm, fill: vermilion-bg, stroke: (top: 2.2pt + vermilion), inset: (x: 10pt, y: 7pt))[
      #text(font: mono-font, size: 8.6pt, weight: "bold", fill: vermilion, tracking: 0.05em)[SYNTHETIC RESILIENCE BREAKS ON REAL SHIFT]
      #v(0.22em)
      #text(size: 10.6pt)[
        Under random synthetic noise, `GNB` looked toughest (`−6.3%`). On real PTB-XL, pooling hospital logs *crashes `GNB` (`−9.7 pp`)* because the `28% MI` over-alarm skews class priors.
      ]
    ],
    block(width: 100%, height: 2.65cm, fill: cobalt-bg, stroke: (top: 2.2pt + cobalt), inset: (x: 10pt, y: 7pt))[
      #text(font: mono-font, size: 8.6pt, weight: "bold", fill: cobalt, tracking: 0.05em)[SUPERVISED BAR FOR WP3–WP5]
      #v(0.22em)
      #text(size: 10.6pt)[
        Simple *Balanced Logistic Regression* on clean Gold data sets a strong baseline (`0.40 → 0.49` val F1), while naive `self_training` stalls—handing WP3–WP5 an honest target to beat.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 08: WP3 — BACKGROUND THEORY: GRAPH LABEL PROPAGATION
// =============================================================================
#content-slide("08", "WP3 · Pratyush Somani · Background", "From Few Labels to a Graph: Harmonic Label Propagation")[
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.2em,
    ruled-col("THE SETTING & THE QUESTION", accent-col: ink)[
      #set text(size: 10.2pt)
      - *Question:* does spreading the few clean labels through the Pool's geometry beat simply training on the Gold labels?
      - *The "discard" strategy:* throw away the Pool's noisy labels $tilde(y)_U$; keep only its *features* as unlabeled points.
      - *Assumption (cluster / manifold):* ECGs joined by dense paths share a diagnosis.
      
    ],
    ruled-col("THE IDEA: LET LABELS DIFFUSE OVER A k-NN GRAPH", accent-col: cobalt)[
      #set text(size: 10.2pt)
      - *Graph:* each ECG is a node, linked to its $k$ nearest neighbours with weight $W_(i j) = exp(-d_(i j)^2 slash (sigma_i sigma_j))$, where $sigma_i$ = distance to the 7th neighbour (adapts to local density).
      - *Clamp* labeled nodes to their one-hot label $Y_L$; labels flow along edges until every unlabeled node equals the weighted average of its neighbours ("harmonic").
      - *Random-walk view:* $F_(i c)$ = probability that a walk from node $i$ first reaches a labeled node of class $c$.
      - *New ECG (val / test):* kernel-weighted average of its $k$ nearest graph nodes.
    ],
  )

  #v(1fr)
  #eq-strip(accent-col: cobalt, bg: cobalt-bg)[
    #text(size: 10.6pt)[
      *Minimise* $E(F) = 1/2 sum_(i,j) W_(i j) norm(F_i - F_j)^2$ s.t. $F_L = Y_L$
      #h(0.6em) ⇒ #h(0.6em) $F_i = 1/D_(i i) sum_j W_(i j) F_j$ #h(0.6em) ⇒ #h(0.6em)
      $F_U^* = (D_"UU" - W_"UU" + 10^(-6) I)^(-1) W_"UL" Y_L$
    ]
  ]

  #v(1fr)
  #grid(
    columns: (1fr, 1fr, 1fr),
    gutter: 1.0em,
    ruled-col("1 · PREPROCESS & METRIC", accent-col: ink)[
      #set text(size: 9.6pt)
      Standardize on $cal(D)_L union cal(D)_U$ features (no labels), clip at $plus.minus 5 sigma$, PCA (`0–40` dims). Distances: *Euclidean*, *Cosine*, Cholesky-whitened *Mahalanobis* with $hat(Sigma)_L + lambda I$.
    ],
    ruled-col("2 · SPARSE GRAPH", accent-col: cobalt)[
      #set text(size: 9.6pt)
      Symmetric $k$-NN graph, $k in \{3, 5, 10, 20\}$, $W <- max(W, W^top)$. Diagnostics logged per fit: connected components and nodes unreachable from any label.
    ],
    ruled-col("3 · SOLVE & PREDICT", accent-col: forest)[
      #set text(size: 9.6pt)
      One sparse-LU factorisation solves all 5 classes at once; `900` fits in the main sweep. Scored on the validation fold; test fold used only for final runs.
    ],
  )
]

// =============================================================================
// SLIDE 09: WP3 — SENSITIVITY GRAPHS AND WHY THEY LOOK LIKE THIS
// =============================================================================
#content-slide("09", "WP3 · Pratyush Somani · Sensitivity", "What Moves the Score: Labels, k, and PCA Dimension")[
  #fig-frame("plots/wp3_summary.png", height: 5.3cm, caption: [Run 2 sweep (3 distances × 5 PCA dims × 4 k × 5 gold fractions × 3 seeds, validation fold). Left: best config per distance, mean ± std over 3 seeds. Middle and right: η = 10%.])
  #v(1fr)
  #grid(
    columns: (1fr, 1fr, 1fr),
    gutter: 1.0em,
    ruled-col("LEFT · F1 vs LABEL SCARCITY", accent-col: ink)[
      #set text(size: 9.8pt)
      *Observed:* Euclidean / PCA 5 / $k = 3$ rises `0.246 → 0.341` (2% → 50%); biggest jump 2% → 5%. The three metrics overlap within error bars.
      *Why:* at 2% only `≈180` labels are revealed (`≈6` HYP, F1 `0.018`) — some classes are barely seeded, so there is little to diffuse.
    ],
    ruled-col("MIDDLE · SMALLER k IS BETTER", accent-col: cobalt)[
      #set text(size: 9.8pt)
      *Observed:* Euclidean falls `0.299 → 0.245` from $k = 3$ to $k = 20$ (mean over η, PCA); Mahalanobis is lowest at every $k$.
      *Reason:* classes overlap (WP1 k-Means purity `≈0.58`), so each extra neighbour is more likely to cross a class boundary; small $k$ keeps diffusion local. The guide expected the opposite.
    ],
    ruled-col("RIGHT · FEW PCA DIMS WIN", accent-col: forest)[
      #set text(size: 9.8pt)
      *Observed:* Euclidean peaks at PCA 5 (`0.294`) and fades to `0.267` at 40; Cosine is flat (`0.272`); Mahalanobis `0.290` at PCA 5 but `0.211` raw, `0.224` at 40.
      *Reason:* extra components add mostly noise; whitening gives noisy directions full weight, and $hat(Sigma)_L$ is estimated from only `≈180–4,500` labeled points.
    ],
  )
]

// =============================================================================
// SLIDE 10: WP3 — CONTROLS: DOES THE UNLABELED POOL HELP?
// =============================================================================
#content-slide("10", "WP3 · Pratyush Somani · Controls", "Does the Unlabeled Pool Help? Controls & Ruled-Out Explanations")[
  #grid(
    columns: (1.15fr, 1fr),
    gutter: 1.3em,
    [
      #ruled-col("CONTROL · LP vs GOLD-ONLY kNN ON THE SAME EMBEDDING (TEST FOLD)", accent-col: cobalt)[
        #set text(size: 10pt)
        #table(
          columns: (auto, 1fr, 1fr, 1fr),
          align: center,
          inset: 4pt,
          stroke: none,
          fill: (x, y) => if y == 0 { paper-alt } else { none },
          [*$eta$*], [*Graph LP*], [*Gold-only kNN*], [*Gain*],
          [2%], [`0.258`], [`0.306`], [`−0.048`],
          [5%], [`0.306`], [`0.319`], [`−0.013`],
          [10%], [`0.309`], [`0.328`], [`−0.019`],
          [20%], [`0.315`], [`0.325`], [`−0.010`],
          [50%], [`0.352`], [`0.348`], [`+0.003`],
        )
        #v(0.1em)
        Same scaler, PCA 5, $k = 3$; they differ only in whether the Pool is used. Validation: gain negative at 2%, 5%, 20%, positive at 10%, 50%. *No consistent benefit from the Pool.*
      ]
      #v(0.3em)
      #ruled-col("WHERE LP LOSES · PER-CLASS F1 AT η = 10% (VAL)", accent-col: ink)[
        #set text(size: 9.8pt)
        #table(
          columns: (auto, 1fr, 1fr, 1fr, 1fr, 1fr),
          align: center,
          inset: 3.5pt,
          stroke: none,
          fill: (x, y) => if y == 0 { paper-alt } else { none },
          [], [*NORM*], [*MI*], [*STTC*], [*CD*], [*HYP*],
          [*Graph LP*], [`0.720`], [`0.181`], [`0.106`], [`0.375`], [`0.179`],
          [*LogReg (unw.)*], [`0.775`], [`0.260`], [`0.262`], [`0.427`], [`0.199`],
        )
        #v(0.1em)
        Unweighted LogReg wins on all five classes; the gap is largest on *STTC* and *MI*.
      ]
    ],
    [
      #ruled-col("RIGOROUS DIAGNOSTIC ELIMINATION", accent-col: vermilion, bg: vermilion-bg)[
        #set text(size: 10.4pt)
        LP is below the gold-only supervised baselines (next slide). Checks that rule out simple explanations:
        - *Not connectivity:* only `1–2` graph components; `0–5` of `≈4,000` nodes unreachable.
        - *Not class imbalance handling:* class-mass normalization changes mean F1 by only `+0.0014` (60 paired runs).
        - *Not PCA information loss:* LP on all 84 raw features (`0.216 → 0.361`) still trails unweighted LogReg.
        - *Not too few unlabeled points:* adding the unused Gold records *hurt* (`0.267` vs `≈0.30`, η ∈ {5, 10, 20}%).
      ]
      #v(0.3em)
      #eq-strip(accent-col: ink, bg: paper-alt)[
        #text(size: 10pt)[*Reading:* the extra unlabeled data gives no consistent gain, and more of it made things worse — so the limit is not the amount of data or a bug in the solver.]
      ]
    ],
  )
]

// =============================================================================
// SLIDE 11: WP3 — GOLD-ONLY BASELINES
// =============================================================================
#content-slide("11", "WP3 · Pratyush Somani · Baselines", "Graph LP vs. Gold-Only Supervised Baselines")[
  #grid(
    columns: (1.32fr, 0.84fr),
    gutter: 1.3em,
    [
      #fig-frame("plots/wp3_vs_baselines.png", height: 6.2cm)
      #v(0.2em)
      #text(size: 9.6pt)[
        #table(
          columns: (auto, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
          align: center,
          inset: 3pt,
          stroke: none,
          fill: (x, y) => if y == 0 { paper-alt } else { none },
          [*Test $eta$*], [*LogReg bal.*], [*LogReg unw.*], [*SVM bal.*], [*Naive Bayes*], [*5-NN*], [*Graph LP*],
          [2%], [`0.335`], [`0.341`], [`0.352`], [`0.340`], [`0.219`], [*`0.258`*],
          [10%], [`0.407`], [`0.408`], [`0.416`], [`0.384`], [`0.276`], [*`0.309`*],
          [50%], [`0.457`], [`0.429`], [`0.471`], [`0.325`], [`0.311`], [*`0.352`*],
        )
      ]
    ],
    [
      #ruled-col("WHAT THE COMPARISON SHOWS", accent-col: vermilion, bg: vermilion-bg)[
        #set text(size: 10.2pt)
        - Balanced LogReg / SVM beat LP at *every* $eta$ on both folds, by `≈8–13 pp`.
        - Unweighted LogReg still beats LP, so class weighting is not the reason.
        - LP only beats raw `5-NN` (and Naive Bayes at 50%).
        - LP numbers are the best of a grid tuned on validation; baselines are untuned, so the gap is not inflated.
      ]
      #v(0.3em)
      #ruled-col("WHY?", accent-col: ink)[
        #set text(size: 10pt)
        *Class overlap* in the 84 hand-crafted features (WP1 purity `≈0.58`) weakens "close ECGs share a label"; supervised models can learn to ignore uninformative directions, distances cannot. The Pool also differs from Gold (`28%` vs `10%` MI).
      ]
    ],
  )
]
// =============================================================================
// SLIDE 10: WP4 — CO-TRAINING THEORY AND ALGORITHM
// =============================================================================
#content-slide("10", "WP4 · Arnav Gupta · Co-Training", "Two ECG Views Teach Each Other — With a Consensus Guard")[
  #grid(
    columns: (0.95fr, 1.05fr),
    gutter: 0.95em,
    [
      #ruled-col("THEORY · TWO USEFUL, NON-REDUNDANT VIEWS", accent-col: cobalt, bg: cobalt-bg)[
        #set text(size: 9.5pt)
        Each view should be predictive, with errors that are not perfectly correlated. View 1 uses temporal/morphology features (`0:42`); View 2 uses spectral/wavelet features (`42:84`). The split offers different descriptions of the same ECG, but does not prove statistical independence. Co-Training tests whether one view can add useful evidence beyond the labels already available to the other.
      ]
      #v(0.48em)
      #eq-strip(accent-col: cobalt, bg: paper-alt)[
        #text(size: 9.6pt)[
          Transfer only when confidence is at least `0.72` *and* the other view predicts the same class.
        ]
      ]
      #v(0.48em)
      #ruled-col("HISTOGRAM BOOSTING + CO-TRAINING ALGORITHM", accent-col: forest, bg: forest-bg)[
        #set text(size: 9.0pt)
        + Train one HistGradientBoosting model per view on the gold labels; each uses `100` depth-`4` trees (learning rate `0.06`, minimum leaf `10`, L2 `1`).
        + In each round, a view proposes up to `10` remaining examples per class with confidence at least `0.72`, limiting majority-class dominance.
        + Transfer a proposal only when the peer view predicts the same class; give it weight `0.35 × confidence`, while every verified gold example keeps weight `1`.
        + Remove accepted records from the pool and retrain both views. Stop if no examples are added or after `12` rounds, then average the two probability outputs.
      ]
    ],
    [
      #fig-frame("plots/view_agreement.png", height: 8.8cm, caption: [Agreement across rounds is a diagnostic — not accuracy or proof of convergence.])
      #v(0.16em)
      #ruled-col("LIMIT", accent-col: vermilion, bg: vermilion-bg)[
        #text(size: 9.1pt)[
          Peer agreement and the per-class cap reduce risky transfers, but cannot eliminate semantic drift.
        ]
      ]
    ],
  )
]

// =============================================================================
// SLIDE 11: WP4 — CO-TRAINING RESULTS
// =============================================================================
#content-slide("11", "WP4 · Arnav Gupta · Co-Training Results", "The Lift Is Clearest at Low Label Fractions — Not Universal")[
  #grid(
    columns: (0.76fr, 1.24fr),
    gutter: 0.95em,
    [
      #ruled-col("READ THE CURVES", accent-col: cobalt, bg: cobalt-bg)[
        #set text(size: 9.8pt)
        Validation fold 9 (`1,642` ECGs); the pool contributes features only, not its machine-generated labels. The reference is a supervised ensemble with the same two views and classifier family.
        #v(0.18em)
        - *Macro-F1 gain over baseline:* `+0.051`, `+0.071`, `+0.035`, and `+0.018` at `2–20%` gold; the largest lift is at `5%`.
        - At `2%`, macro-F1 rises `0.315 → 0.365` even as accuracy falls by `0.012`; MI F1 rises `0.212 → 0.363`, illustrating that accuracy and class-balanced F1 can tell different stories.
        - *Diminishing return:* at `50%`, the result is `0.470` vs. `0.478` for the baseline (`−0.008`), when more verified labels leave less room for pseudo-labels to help.
      ]
      #v(0.48em)
      #text(size: 9.1pt, fill: ink-muted)[
        *Takeaway:* the strongest gain appears with scarce labels, but neither the improvement nor the class-wise benefit is universal.
      ]
    ],
    fig-frame("plots/cotraining_f1_only.png", height: 10.2cm, caption: [Validation macro-F1 by gold fraction.]),
  )
]

// =============================================================================
// SLIDE 12: WP4 — TSVM THEORY AND ALGORITHM
// =============================================================================
#content-slide("12", "WP4 · Arnav Gupta · Transductive SVM", "TSVM Uses Unlabeled Geometry to Seek Low-Density Boundaries")[
  #grid(
    columns: (0.96fr, 1.04fr),
    gutter: 0.95em,
    [
      #ruled-col("THEORY · LOW-DENSITY SEPARATION", accent-col: cobalt, bg: cobalt-bg)[
        #set text(size: 9.4pt)
        A supervised SVM maximizes the margin on labeled data. Under the *cluster assumption*, class boundaries should pass through low-density gaps. TSVM uses unlabeled features to seek such boundaries; overlap and class imbalance can violate the assumption. Unlike Co-Training, it does not exchange examples between views: it starts from one classifier's provisional labels and revises them as the boundary changes.
      ]
      #v(0.16em)
      #eq-strip(accent-col: cobalt, bg: paper-alt)[
        #text(size: 9.2pt)[
          Conceptual weighted hinge objective: $J = 1/2 norm(f)_cal(H)^2 + C_L sum_(i in L) ell_i + C_U sum_(j in U^*) q_j ell_j^U$. Here $hat(y)_j$ is a latent pseudo-label and $q_j$ downweights less-confident retained points.
        ]
      ]
      #v(0.16em)
      #ruled-col("TSVM ALGORITHM · FILTER, ANNEAL, SWITCH", accent-col: forest, bg: forest-bg)[
        #set text(size: 8.9pt)
        + Scale $X_L ∪ X_U$. Fit a balanced RBF SVC (`C = 1`) on gold data; initialize unlabeled pseudo-labels and margins.
        + Keep the top-confidence `35%` by margin ($m_j =$ top-two score gap); set $q_j = 1/(1+e^(-m_j))$.
        + Set $C_U = 0.05$ and cap it at $min(0.30, 0.8 N_L/N_(U, "kept"))$.
        + At each $C_U$, fit an RBF SVC (`C_L = 2`) with weights `1` for gold and $C_U q_j$ for unlabeled points.
        + Re-predict and switch pseudo-labels, refitting up to `3` times or until stable; double $C_U$ to its cap, then return the final classifier.
      ]
    ],
    [
      #fig-frame("plots/tsvm_f1_only.png", height: 8.4cm, caption: [Validation macro-F1: TSVM vs. gold-only SVM.])
      #v(0.16em)
      #ruled-col("IMPLEMENTATION CAVEAT", accent-col: vermilion, bg: vermilion-bg)[
        #text(size: 9.0pt)[
          Alternating fits and label switches are a heuristic, not a global optimizer. Margin weights are not calibrated probabilities.
        ]
      ]
    ],
  )
]

// =============================================================================
// SLIDE 13: WP4 — TSVM RESULTS AND CLASS-LEVEL DIAGNOSTICS
// =============================================================================
#content-slide("13", "WP4 · Arnav Gupta · TSVM Results", "Aggregate Gains Are Modest — Inspect the Class-Wise Trade-Off")[
  #grid(
    columns: (0.76fr, 1.24fr),
    gutter: 0.95em,
    [
      #ruled-col("LATEST VALIDATION SWEEP", accent-col: cobalt, bg: cobalt-bg)[
        #set text(size: 9.7pt)
        Validation fold 9, compared with an inductive balanced SVM whose scaler is fit on gold data only. TSVM's Macro-F1 gains at `2%`, `5%`, `10%`, `20%`, and `50%` are `+0.005`, `+0.006`, `+0.026`, `+0.031`, and `+0.003`, respectively.
        #v(0.16em)
        The largest lift is `0.458 → 0.488` at `20%` gold. Positive differences at the other fractions are small, so the result is a consistent direction of change, not a large gain at every setting.
      ]
      #v(0.48em)
      #ruled-col("CLASS-WISE TRADE-OFF · 10% GOLD", accent-col: vermilion, bg: vermilion-bg)[
        #text(size: 9.4pt)[
          At `10%`, NORM F1 rises `0.646 → 0.739` and CD `0.428 → 0.515`; MI falls `0.393 → 0.352`, STTC `0.325 → 0.315`, and HYP is nearly unchanged (`0.372 → 0.371`). The NORM and CD gains more than offset the MI and STTC dips in the macro average (`+0.026`).
          #v(0.12em)
          The model uses `1,540` support vectors vs. `848` for the baseline. This signals a more complex fitted boundary; by itself it is not evidence of better generalization or margin collapse.
        ]
      ]
      #v(0.16em)
      #text(size: 9.0pt, fill: ink-muted)[
        *Interpretation:* margin filtering and class balancing are safeguards; performance still depends on which classes supply reliable boundary examples.
      ]
    ],
    fig-frame("plots/tsvm_per_class_f1_eta10.png", height: 10.2cm, caption: [Per-class validation F1 at `10%` gold.]),
  )
]

// =============================================================================
// SLIDE 14: WP5 — LATENT-NOISE EM & SYNTHETIC RECOVERY
// =============================================================================

// =============================================================================
#content-slide("14", "WP5 · Tanuj Yadav · Latent-Noise EM", "Modeling Structured Noise Explicitly Instead of Discarding It")[
  #grid(
    columns: (1.12fr, 1.00fr),
    gutter: 1.3em,
    [
      #ruled-col("GENERATIVE–DISCRIMINATIVE EM (DAWID & SKENE, 1979)", accent-col: cobalt, bg: cobalt-bg)[
        #set text(size: 10.8pt)
        Keep observed labels $tilde(y)_j$, treat true class $z_j$ as latent, and parameterize annotator noise via a $C times C$ matrix $T_(c k) = P(tilde(y) = k | z = c)$ (L-BFGS-B multinomial LR, $C_"lr"=1.0$, Dirichlet $alpha=1.5$):
      ]
      #v(0.35em)
      #eq-strip(accent-col: cobalt, bg: paper-alt)[
        #align(left, text(font: mono-font, size: 8.2pt, weight: "bold", fill: cobalt)[E-STEP · POSTERIOR RESPONSIBILITY])
        #v(0.10em)
        #text(size: 11.0pt)[
          $gamma_(j c)^((t)) = frac(T_(c k)^((t)) P(z_j = c | x_j; theta^((t))), sum_(c'=1)^C T_(c' k)^((t)) P(z_j = c' | x_j; theta^((t))))$
        ]
      ]
      #v(0.28em)
      #eq-strip(accent-col: forest, bg: forest-bg)[
        #align(left, text(font: mono-font, size: 8.2pt, weight: "bold", fill: forest)[M-STEP · TRANSITION MATRIX UPDATE])
        #v(0.10em)
        #text(size: 11.0pt)[
          $T_(c k)^((t+1)) = frac((alpha_(c k) - 1) + sum_(j in cal(D)_U) gamma_(j c)^((t)) bold(1)[tilde(y)_j = k], sum_(k'=1)^C (alpha_(c k') - 1) + sum_(j in cal(D)_U) gamma_(j c)^((t)))$
        ]
      ]
      #v(0.30em)
      #text(size: 10.6pt)[
        Classifier $theta^((t+1))$ then refits on $cal(D)_L union cal(D)_U$ weighted by clamped gold labels and soft responsibilities $gamma_(j c)^((t))$.
      ]
    ],
    [
      #fig-frame("plots/frobenius_recovery.png", height: 6.9cm, caption: [Synthetic recovery: known *uniform* $T_"true"$ (`diag = 0.70, off = 0.075`), 500 gold samples.])
      #v(0.30em)
      #ruled-col("CONSISTENT MATRIX RECOVERY VERIFIED", accent-col: forest, bg: forest-bg)[
        #text(size: 10.4pt)[
          Frobenius error $norm(hat(T) - T_"true")_F$ drops by *63%* from `0.364` ($N_U = 100$) to a minimum of `0.135` at $N_U =$ `2,000` (`0.145` at `5,000`, capped at 50 EM iterations), confirming identifiability before auditing PTB-XL.
        ]
      ]
    ],
  )
]

// =============================================================================
// SLIDE 15: WP5 — DISCARD VS. CORRECT COMPARISON (Q3 MAIN SYNTHESIS)
// =============================================================================
#content-slide("15", "WP5 · Tanuj Yadav · Discard vs. Correct (Q3)", "EM Wins All 20/20 Cells Over Graph LP & Co-Training")[
  #grid(
    columns: (0.98fr, 1.16fr),
    gutter: 1.3em,
    [
      #fig-frame("plots/discard_vs_correct_heatmap.png", height: 7.6cm, caption: [Validation Macro F1 gain (EM minus GraphLP) across 20 ($eta times epsilon$) cells — positive in every cell.])
      #v(0.22em)
      #text(size: 9.7pt, fill: ink-muted)[Even vs. WP3's tuned `PCA=5, k=3` LP (`0.246 -> 0.341`), EM leads every cell by *+0.07 to +0.21* Macro F1.]
    ],
    [
      #ruled-col([PTB-XL VALIDATION MACRO F1 (+ GOLD SVM REF.)], accent-col: forest)[
        #set text(size: 10.0pt)
        #table(
          columns: (0.46fr, 0.78fr, 0.72fr, 0.72fr, 0.72fr, 0.80fr),
          stroke: none,
          inset: (x: 3.5pt, y: 4.0pt),
          fill: (x, y) => if (x == 4 or x == 5) and y >= 1 { forest-bg } else if x == 1 and y >= 1 { paper-alt } else { none },
          table.hline(stroke: 1.0pt + ink),
          table.header([*$eta$*], [*Gold SVM*], [*GraphLP*], [*CoTrain*], [*EM (0)*], [*EM (0.45)*]),
          table.hline(stroke: 0.4pt + ink),
          [2%], [0.344], [0.183], [0.355], [*0.462*], [0.413],
          [5%], [0.400], [0.253], [0.351], [*0.453*], [0.418],
          [10%], [0.429], [0.266], [0.346], [*0.456*], [0.418],
          [20%], [*0.459*], [0.293], [0.340], [0.441], [0.411],
          [50%], [*0.489*], [0.340], [0.326], [0.456], [0.425],
          table.hline(stroke: 1.0pt + ink),
        )
      ]
      #v(0.38em)
      #ruled-col("ANSWER TO Q3: WHEN TO CORRECT", accent-col: cobalt, bg: cobalt-bg)[
        #set text(size: 10.5pt)
        - *Signal Preserved:* Machine labels retain `79%–97%` diagonal accuracy; discarding $tilde(y)_U$ throws away `3,968` informative clinical priors.
        - *Scarcity Winner ($eta <= 10%$):* At `2%` (`180` gold), EM (`0.462`) beats Gold SVM (`0.344`) by *+11.8 pp* (`HYP` F1 `0.372` vs `0.000` LP).
        - *High-Gold Regime ($eta >= 20%$):* Non-linear Gold RBF-SVM catches up (`0.459–0.489`) once clean data saturates EM's linear LR base.
        - *Noise Resilience:* Stays `>0.41` even with `45%` *extra* uniform corruption.
      ]
    ],
  )
]

// =============================================================================
// SLIDE 16: WP5 — CLINICAL ANNOTATOR BIAS AUDIT (Q4)
// =============================================================================
#content-slide("16", "WP5 · Tanuj Yadav · Annotator Bias Audit (Q4)", "Learned 5×5 Confusion Matrix T̂ Exposes Hospital Software Biases")[
  #grid(
    columns: (1.12fr, 0.98fr),
    gutter: 1.3em,
    align: horizon,
    [
      #fig-frame("plots/T_hat_heatmap.png", height: 8.1cm, caption: [Converged at EM iteration `39` ($Delta T = 9.65 times 10^(-5)$) on the `3,968` unvalidated autogenerated PTB-XL reports (rows = latent truth $z$, cols = machine label $tilde(y)$.])
    ],
    [
      #ruled-col("CLINICAL DIAGNOSTIC INSIGHTS (Q4)", accent-col: vermilion, bg: vermilion-bg)[
        #set text(size: 11.0pt)
        - *#1 `NORM -> MI` (9.41%):* Independently explains WP1's Slide 02 discovery (`MI` jumping from `10.4%` in $cal(D)_L$ to `28.0%` in $cal(D)_U$). Hospital software conservatively over-flags normal ECGs as infarction to minimize missed emergencies.
        - *#2 `STTC -> MI` (9.18%):* Automated rules confuse ST-T morphology shifts with myocardial infarction, whereas true `MI` retains `95.8%` diagonal accuracy.
        - *#3 `HYP -> NORM` (6.19%):* Hypertrophy has the lowest diagonal agreement (`79.2%`), leaking `6.2%` to `NORM` and `5.8%` to `CD`.
      ]
      #v(0.45em)
      #eq-strip(accent-col: ink, bg: paper-alt)[
        #text(size: 10.6pt)[*Takeaway:* Latent-Noise EM acts as both a *noise-robust classifier* and an *unsupervised diagnostic auditor* of legacy clinical software.]
      ]
    ],
  )
]

// =============================================================================
// SLIDE 17: FINAL CONCLUSION
// =============================================================================
#content-slide("17", "Final conclusion", "Conclusion")[
  #grid(columns: (1.15fr, 1fr), gutter: 1.2em,
    [
      #block(width: 100%, height: 3.15cm, fill: forest-bg, stroke: (left: 3pt + forest), inset: (x: 10pt, y: 8pt))[
        #grid(columns: (0.8fr, 1.6fr), column-gutter: 0.6em, align: horizon,
          text(font: mono-font, size: 9.0pt, weight: "bold", fill: forest)[Q1 · WHICH MODEL PERFORMS BEST?],
          text(size: 11.0pt, fill: ink)[Noise-aware EM leads with `2–10%` gold labels (macro F1 `0.462`, `0.453`, `0.456`). Gold-only SVM leads at `20–50%` (`0.459`, `0.489`).],
        )
      ]
      #v(0.35em)
      #block(width: 100%, height: 3.15cm, fill: vermilion-bg, stroke: (left: 3pt + vermilion), inset: (x: 10pt, y: 8pt))[
        #grid(columns: (0.8fr, 1.6fr), column-gutter: 0.6em, align: horizon,
          text(font: mono-font, size: 9.0pt, weight: "bold", fill: vermilion)[Q2 · WHAT HAPPENS WHEN NOISE DECREASES?],
          text(size: 11.0pt, fill: ink)[Decision-tree macro F1 rises from `0.351` at `45%` flips to `0.582` with clean labels. Structured class-pair noise still degrades every tested classifier.],
        )
      ]
      #v(0.35em)
      #block(width: 100%, height: 3.15cm, fill: cobalt-bg, stroke: (left: 3pt + cobalt), inset: (x: 10pt, y: 8pt))[
        #grid(columns: (0.8fr, 1.6fr), column-gutter: 0.6em, align: horizon,
          text(font: mono-font, size: 9.0pt, weight: "bold", fill: cobalt)[Q3 · CAN WE FIND LABEL-ERROR PATTERNS?],
          text(size: 11.0pt, fill: ink)[EM estimates `NORM → MI` (`9.41%`), `STTC → MI` (`9.18%`), and `HYP → NORM` (`6.19%`) among `3,968` machine-labeled ECGs; these patterns need clinical review.],
        )
      ]
    ],
    [
      #block(width: 100%, height: 10.05cm, fill: white, stroke: 0.7pt + rule-color, radius: 2pt, inset: (x: 8pt, y: 9pt))[
        #text(font: mono-font, size: 8.8pt, weight: "bold", fill: forest, tracking: 0.04em)[PTB-XL VALIDATION · MACRO F1]
        #v(0.25em)
        #text(size: 8.8pt, fill: ink-muted)[By verified-label budget; bold values mark the best result.]
        #v(0.35em)
        #set text(size: 8.9pt)
        #table(
          columns: (1.55fr, 0.85fr, 0.85fr, 0.85fr, 0.85fr, 0.85fr),
          inset: (x: 1.2pt, y: 7pt),
          stroke: none,
          align: (left, center, center, center, center, center),
          fill: (x, y) => if (y == 1 and x >= 1 and x <= 3) or (y == 2 and x >= 4) { forest-bg } else if y == 0 { paper-alt },
          [*Method*], [*2%*], [*5%*], [*10%*], [*20%*], [*50%*],
          [Noise-aware EM], [*0.462*], [*0.453*], [*0.456*], [0.441], [0.456],
          [Gold-only SVM], [0.344], [0.400], [0.429], [*0.459*], [*0.489*],
          [Co-training], [0.355], [0.351], [0.346], [0.340], [0.326],
          [Graph LP], [0.183], [0.253], [0.266], [0.293], [0.340],
        )
        #v(1fr)
        #ruled-col("MACRO-F1 TAKEAWAY", accent-col: ink, bg: paper-alt)[
          #text(size: 10.0pt)[At `2%` gold, EM leads SVM by `0.118`; at `50%`, SVM leads EM by `0.033`. The best choice changes as verified data grows.]
        ]
      ]
    ],
  )
]

// =============================================================================
// REFERENCES SLIDE (Excluded from 17-Slide Count)
// =============================================================================
#slide(config: config-page(footer: make-footer("REFERENCES")))[
  #text(font: mono-font, size: 9.0pt, weight: "bold", fill: vermilion, tracking: 0.08em)[BIBLIOGRAPHY]
  #v(0.10em)
  #text(font: serif-font, size: 21.5pt, weight: "bold", fill: ink)[References]
  #v(0.18em)
  #line(length: 100%, stroke: 1.15pt + ink)
  #v(1fr)

  #set text(size: 10.5pt)
  #grid(
    columns: (1fr, 1fr),
    gutter: 1.8em,
    [
      #grid(
        columns: (2.6em, 1fr),
        column-gutter: 0.35em,
        row-gutter: 1.12em,
        text(font: mono-font, weight: "bold", fill: vermilion)[\[1\]],
        [S. Rogers and M. Girolami, _A First Course in Machine Learning_, 2nd ed., CRC Press, 2015.],
        text(font: mono-font, weight: "bold", fill: vermilion)[\[2\]],
        [P.-N. Tan, M. Steinbach, A. Karpatne, and V. Kumar, _Introduction to Data Mining_, 2nd ed., Pearson, 2018.],
        text(font: mono-font, weight: "bold", fill: vermilion)[\[3\]],
        [C. M. Bishop, _Pattern Recognition and Machine Learning_, Springer, 2006.],
        text(font: mono-font, weight: "bold", fill: vermilion)[\[4\]],
        [K. P. Murphy, _Probabilistic Machine Learning: An Introduction_, MIT Press, 2022.],
        text(font: mono-font, weight: "bold", fill: vermilion)[\[5\]],
        [P. Wagner et al., "PTB-XL, a large publicly available electrocardiography dataset," _Scientific Data_, vol. 7, no. 1, Art. no. 154, 2020.],
      )
    ],
    [
      #grid(
        columns: (2.6em, 1fr),
        column-gutter: 0.35em,
        row-gutter: 1.12em,
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
]