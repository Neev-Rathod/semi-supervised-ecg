"""
presentation/build_wp2_speaker_notes.py
=======================================
Builds Shaurya Suman's focused WP2 Speaker Notes & Viva Defense PDF
(presentation/shaurya_wp2_speaker_notes.pdf) matched to Slides 05-07 of
presentation/main.typ (and noted for exp.typ Slides 06-08).
"""

from pathlib import Path
import subprocess

HTML_OUT = Path(
    "/home/shaurya/.gemini/antigravity/brain/1e0943a9-7357-4ba1-abd5-71d534904893/scratch/shaurya_wp2_notes.html"
)
PDF_OUT = Path(__file__).resolve().parent / "shaurya_wp2_speaker_notes.pdf"

SLIDES = [
    {
        "num": "SLIDE 05 / 17  (exp.typ: 06)",
        "tag": "WP2 (1/3) · CONTROLLED NOISE LAB · ~55 SECONDS",
        "accent": "#18181b",
        "bg": "#ece7dc",
        "title": "Controlled Noise Lab: How Classifiers & Self-Training Fail",
        "figure": "plots/wp2_fig2_uniform_breakdown_small_multiples.png",
        "entry": "Bridge from Neev (WP1): \"Neev just showed that machine-generated ECG labels have 2.7× more heart attacks and heavily overlapping classes. Before we try semi-supervised learning, WP2 builds a controlled test lab to see how each classical model actually breaks under label noise.\"",
        "point": "Explain WHY we need a synthetic lab first, map the 5 models to WP3–WP5, and point out three concrete failure mechanics across the 5 small panels.",
        "say": [
            "<strong>Why a synthetic lab?</strong> Real hospital reports (<code>D_U</code>) never give us the patient's true label, so we cannot measure recovery against ground truth or dial noise smoothly from <code>0%</code> to <code>60%</code>. We create <code>3,000</code> 5-class points across <code>50</code> features (<code>10</code> true signal + <code>5</code> correlated mixtures mimicking correlated ECG leads + <code>35</code> noise dims), rotated orthogonally so models cannot cheat by filtering raw axes.",
            "<strong>Why these 5 models?</strong> Each maps directly downstream: <code>GNB &amp; LR → WP5</code>, <code>7-NN → WP3</code>, <code>Decision Tree &amp; RBF-SVM → WP4</code>. And we corrupt <strong>only <code>D_U</code></strong> while keeping Gold <code>D_L</code> (420 pts) and Validation (450 pts) completely clean.",
            "<strong>Walk left-to-right across the 5 charts (<code>ε: 0 → 60%</code>):</strong> Unpruned <strong>Decision Trees collapse worst (−38.5%)</strong> as trees grow from <code>348 → 641</code> leaves just memorizing wrong labels—directly motivating WP4's shallow <code>max_depth=4</code> trees. <strong>7-NN falls −27.1%</strong>, crossing below <code>gold_only</code> near <code>ε ≈ 32%</code>.",
            "<strong>Two hidden traps:</strong> (1) <strong>RBF-SVM</strong> looks flat (<code>−7.4%</code>), yet support vectors swell from <code>1,318</code> (63%) to <strong><code>2,015</code> (96% of all training data!)</strong> as wrong labels become margin violations. (2) <strong>Self-training</strong> (ignoring <code>ỹ_U</code> and pseudo-labeling own <code>&gt;90%</code> guesses) drops poorly calibrated <strong>GNB by −8.3 pp</strong> below <code>gold_only</code>—proving WP4 needs two independent views.",
        ],
        "handoff": "\"That was purely uniform random noise. What happens when noise isn't random—when specific diseases get systematically confused?\"",
    },
    {
        "num": "SLIDE 06 / 17  (exp.typ: 07)",
        "tag": "WP2 (2/3) · NOISE PHYSICS (Q2) · ~50 SECONDS",
        "accent": "#b91c1c",
        "bg": "#f9eaea",
        "title": "Random Noise Spares Voting; Structured Bias Breaks Everyone",
        "figure": "plots/wp2_fig4_three_noise_types.png",
        "entry": None,
        "point": "This is the core Q2 insight: random errors preserve majority vote, whereas structured pair confusion crushes ALL classifiers—making WP5's confusion matrix mandatory.",
        "say": [
            "<strong>Explain the X-axis cleanly:</strong> We align all three mathematical noise channels by the <strong>exact percentage of <code>D_U</code> labels actually flipped</strong> so the comparison is fair.",
            "<strong>Panel A vs. Panel B (the big twist):</strong> Under <strong>Uniform noise (A)</strong>, errors spread evenly over 4 wrong classes, so even at <code>60.2%</code> flips the true class still wins the majority vote (<code>SVM = 0.814</code>, <code>GNB = 0.608</code>). Under <strong>Asymmetric pair confusion <code>0↔1, 2↔3</code> (B)</strong>—just like confusing specific heart diseases—at <strong><code>48.5%</code> flips every model collapses together</strong>: <code>SVM</code> plunges <code>0.879 → 0.534</code>, <code>LR</code> drops <code>0.761 → 0.440</code>, and even <code>GNB</code> crashes <code>0.649 → 0.464</code>.",
            "<strong>Panel C (Boundary Eq. 3.1):</strong> Flipping hard borderline ECGs near decision boundaries drags <code>SVM-naive_pool</code> (<code>0.794</code>) below its clean <code>gold_only</code> floor (<code>0.813</code>) earlier at <code>40%</code> flips.",
            "<strong>Why it proves WP5 is essential:</strong> Simple regularization cannot fix structured bias when wrong classes outvote truth. WP5 must explicitly model the <code>5 × 5</code> confusion table <code>T</code>—and WP2's asymmetric generator is the exact testbed WP5 uses to prove <code>T_hat</code> converges.",
        ],
        "handoff": "\"Now let us bring these same 5 baselines onto real PTB-XL ECGs to see what changes under real clinical class imbalance.\"",
    },
    {
        "num": "SLIDE 07 / 17  (exp.typ: 08)",
        "tag": "WP2 (3/3) · REAL ECG REALITY CHECK · ~45 SECONDS",
        "accent": "#1d4ed8",
        "bg": "#eaf0fa",
        "title": "PTB-XL Reality Check: MI Bias Shatters Gaussian NB (−9.7 pp)",
        "figure": "plots/wp2_fig5_ptbxl_reality_check.png",
        "entry": None,
        "point": "On real PTB-XL (9,010 Gold + 3,968 Pool), class imbalance and the 28% MI skew flip GNB from most robust to worst damaged, and set Balanced LogReg as the bar for WP3–WP5.",
        "say": [
            "<strong>The surprise on Gaussian NB (left panels):</strong> In synthetic uniform noise, <code>GNB</code> looked resilient (<code>−6.3%</code>). On real PTB-XL at <code>η = 2%</code> Gold, blindly pooling hospital logs <strong>crashes <code>GNB</code> by −9.7 pp</strong> (<code>0.362 → 0.265</code>) across every label fraction—because the <code>28% MI</code> over-alarm directly shifts Gaussian priors and inflates variances.",
            "<strong>Why pooling helps early then saturates:</strong> When Gold is scarce (<code>2% = 180</code> records), most machine labels are still right, so pooling lifts <code>SVM</code> and <code>LR</code>. Once Gold reaches <code>100%</code> (<code>9,010</code> records), clean <code>Balanced LogReg</code> reaches <strong><code>0.494</code> val (<code>0.466</code> test)</strong> and beats naive pooling (<code>0.489</code>).",
            "<strong>Establishing the bar:</strong> Single-view <code>self_training</code> underperforms on real ECGs too (<code>kNN</code> drops <code>0.216 → 0.143</code> at <code>2%</code>). WP2 hands WP3, WP4, and WP5 an honest supervised target to beat.",
        ],
        "handoff": "Pass smoothly to Pratyush (Slide 08): \"Since naive pooling poisons generative priors and single-view self-training fails, Pratyush starts WP3 by discarding those noisy machine labels and propagating Gold labels on an ECG similarity graph.\"",
    },
]

VIVA_QS = [
    ("1. Why build a 50-D synthetic dataset if it doesn't match PTB-XL's 84 ECG features?",
     "PTB-XL never tells us the true diagnosis inside <code>D_U</code>, so you cannot compute true <code>T_hat</code> recovery error or vary noise cleanly from 0% to 60%. Removing class imbalance isolates pure label-noise laws in Slides 05–06; then Slide 07 runs the exact same baselines on real PTB-XL (<code>ptbxl_baselines.csv</code>) to expose the <code>−9.7 pp</code> GNB shift from real <code>28% MI</code> bias."),
    ("2. What do 10 informative, 5 redundant, and 35 noise dims mean—and why orthogonally rotate?",
     "Only <code>10</code> axes separate the 5 diseases, <code>5</code> are linear mixtures of those 10 (just like correlated 12 ECG leads), and <code>35</code> carry zero class signal. A random QR orthogonal rotation mixes all 50 coordinates so classifiers cannot cheat by picking specific raw columns; additive <code>N(0, 0.1²)</code> jitter matches realistic measurement noise."),
    ("3. In synthetic data, Gold (420) and Pool (1,680) start from the same clean split—why keep them separate?",
     "To isolate <strong>label corruption alone</strong> from sampling shift: keeping <code>X</code> from the same manifold ensures any gap between <code>gold_only</code> and <code>naive_pool</code> is 100% caused by flipping labels in <code>D_U</code>. Only <code>D_U</code> gets corrupted across <code>ε</code> because <code>D_L</code> models cardiologist-verified anchors and Val is the clean evaluation key."),
    ("4. Why did GNB survive uniform noise (−6.3%) yet collapse (−9.7 pp) on real PTB-XL naive_pool?",
     "Uniform random flips cancel symmetrically around global Gaussian means and keep equal priors (1/5 each). Real PTB-XL's <code>D_U</code> has <strong>asymmetric class shift</strong> (<code>28% MI</code> vs. <code>10.4%</code> in Gold), which directly pulls GNB's priors and inflates its <code>MI</code> covariance."),
    ("5. SVM F1 only dropped −7.4% under uniform noise—why call that a failure mode?",
     "Look at accuracy vs. margin structure: to tolerate wrong labels in the pool, <code>SVM-naive_pool</code> had to turn <strong><code>2,015</code> out of <code>2,100</code> training samples (96%) into support vectors</strong> (up from <code>1,318</code>). Nearly every point became a margin boundary/violation—precisely why WP4 TSVM must filter to the top 35% margin confidence and cap <code>C_U ≤ 0.30</code>."),
    ("6. How do WP2's outputs concretely feed into WP3, WP4, and WP5?",
     "(a) Proves unpruned trees memorize noise (<code>348 → 641</code> leaves) and <code>self_training</code> collapses GNB → motivates WP4's <code>max_depth=4</code> dual-view consensus; (b) Proves SV bloat → informs WP4 TSVM's capped <code>C_U</code>; (c) Proves asymmetric confusion breaks everyone → motivates WP5's <code>5 × 5</code> matrix <code>T</code>, and WP2's <code>synthetic_generator.py</code> directly benchmarks WP5's Frobenius recovery (<code>0.364 → 0.135</code>)."),
]


def render_html() -> str:
    slide_blocks = []
    for s in SLIDES:
        lis = "".join(f"<li>{x}</li>" for x in s["say"])
        entry_html = (
            f'<div class="handoff top-bridge"><strong>Entry From WP1:</strong> <em>{s["entry"]}</em></div>'
            if s["entry"] else ""
        )
        slide_blocks.append(f"""
        <section class="card" style="border-top: 3px solid {s["accent"]};">
          <div class="meta">
            <span class="badge" style="background:{s["bg"]}; color:{s["accent"]}; border:1px solid {s["accent"]};">{s["num"]}</span>
            <span class="tag" style="color:{s["accent"]};">{s["tag"]}</span>
            <span class="fig-ref">Figure: <code>{s["figure"]}</code></span>
          </div>
          <h2>{s["title"]}</h2>
          {entry_html}
          <div class="point" style="background:{s["bg"]}; border-left: 3px solid {s["accent"]};">
            <strong>Goal of This Slide:</strong> {s["point"]}
          </div>
          <ul>{lis}</ul>
          <div class="handoff"><strong>Next Slide Transition:</strong> <em>{s["handoff"]}</em></div>
        </section>
        """)

    q_blocks = "".join(
        f"""
        <div class="qa-card">
          <div class="qa-q">{q}</div>
          <div class="qa-a">{a}</div>
        </div>
        """
        for q, a in VIVA_QS
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>WP2 Speaker Notes — Shaurya Suman</title>
<style>
  @page {{
    size: A4;
    margin: 9.5mm 11.5mm 10mm 11.5mm;
    @top-right {{
      content: "SHAURYA SUMAN · WP2 SPEAKER NOTES & Q&A";
      font-family: "Liberation Sans", "DejaVu Sans", sans-serif;
      font-size: 7.2pt;
      color: #71717a;
      letter-spacing: 0.05em;
    }}
    @bottom-left {{
      content: "BITS F464 · Semi-Supervised ECG (main.typ Slides 05–07)";
      font-family: "Liberation Sans", "DejaVu Sans", sans-serif;
      font-size: 7.5pt;
      color: #71717a;
    }}
    @bottom-right {{
      content: "Page " counter(page) " of " counter(pages);
      font-family: "Liberation Sans", "DejaVu Sans", sans-serif;
      font-size: 7.5pt;
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
    font-size: 8.35pt;
    line-height: 1.30;
  }}
  .banner {{
    background: #f6f3ec;
    border: 1px solid #d4cfc2;
    border-left: 5px solid #b91c1c;
    padding: 7px 12px;
    margin-bottom: 7px;
  }}
  .kicker {{
    font-size: 7.3pt;
    font-weight: bold;
    letter-spacing: 0.08em;
    color: #b91c1c;
    margin-bottom: 2px;
  }}
  h1 {{
    font-family: "DejaVu Serif", Georgia, serif;
    font-size: 13.0pt;
    margin: 0 0 2px 0;
    color: #18181b;
  }}
  .sub {{
    margin: 0;
    font-size: 8.2pt;
    color: #3f3f46;
  }}
  .card {{
    background: #fcfbf8;
    border: 1px solid #e4dfd3;
    border-radius: 3px;
    padding: 6px 10px;
    margin-bottom: 6.5px;
    break-inside: avoid;
    page-break-inside: avoid;
  }}
  .meta {{
    display: flex;
    align-items: center;
    gap: 7px;
    margin-bottom: 2px;
  }}
  .badge {{
    font-size: 7.2pt;
    font-weight: bold;
    padding: 1px 5px;
    border-radius: 2px;
    white-space: nowrap;
  }}
  .tag {{
    font-size: 7.2pt;
    font-weight: bold;
    letter-spacing: 0.04em;
    white-space: nowrap;
  }}
  .fig-ref {{
    margin-left: auto;
    font-size: 7.0pt;
    color: #71717a;
    white-space: nowrap;
  }}
  h2 {{
    font-family: "DejaVu Serif", Georgia, serif;
    font-size: 10.2pt;
    margin: 1px 0 4px 0;
    color: #18181b;
  }}
  .point {{
    padding: 3px 7px;
    font-size: 8.1pt;
    margin-bottom: 4px;
  }}
  ul {{
    margin: 3px 0 4px 0;
    padding-left: 14px;
  }}
  li {{
    margin-bottom: 2px;
    color: #27272a;
  }}
  code {{
    font-family: "DejaVu Sans Mono", monospace;
    font-size: 7.6pt;
    background: #f1ede4;
    padding: 0 2.5px;
    border-radius: 2px;
  }}
  .handoff {{
    border-top: 1px dashed #d4cfc2;
    padding-top: 3px;
    margin-top: 3px;
    font-size: 8.0pt;
    color: #3f3f46;
  }}
  .top-bridge {{
    border-top: none;
    border-bottom: 1px dashed #d4cfc2;
    padding-top: 0;
    padding-bottom: 3px;
    margin-top: 0;
    margin-bottom: 4px;
  }}
  .page-break {{
    page-break-before: always;
    break-before: page;
  }}
  .qa-card {{
    background: #f6f3ec;
    border: 1px solid #d4cfc2;
    border-top: 2.5px solid #18181b;
    padding: 8px 11px;
    margin-bottom: 9px;
    break-inside: avoid;
    page-break-inside: avoid;
  }}
  .qa-q {{
    font-weight: bold;
    color: #b91c1c;
    font-size: 9.3pt;
    margin-bottom: 3px;
  }}
  .qa-a {{
    color: #27272a;
    font-size: 8.9pt;
    line-height: 1.38;
  }}
</style>
</head>
<body>
  <div class="banner">
    <div class="kicker">PERSONAL SPEAKER SCRIPT · SHAURYA SUMAN (WP2 · 2024A7PS0589G)</div>
    <h1>WP2 Presentation Guide: Synthetic Lab, Noise Physics &amp; PTB-XL Baselines</h1>
    <p class="sub">Aligned to <code>main.typ</code> <strong>Slides 05–07</strong> (also fits <code>exp.typ</code> Slides 06–08). Target pacing: <strong>~2 min 30 sec</strong>.</p>
  </div>

  {"".join(slide_blocks)}

  <div class="page-break">
    <div class="banner" style="border-left-color:#18181b;">
      <div class="kicker" style="color:#18181b;">WP2 VIVA DEFENSE SHEET · SHAURYA SUMAN</div>
      <h1>Top 6 Questions Professors Will Ask You on WP2</h1>
      <p class="sub">Direct, jargon-free defenses grounded in verified <code>outputs/wp2/</code> runs and downstream handoffs to WP3–WP5.</p>
    </div>
    {q_blocks}
  </div>
</body>
</html>
"""


def main():
    HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text(render_html(), encoding="utf-8")
    subprocess.run(
        [
            "/usr/bin/google-chrome",
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--print-to-pdf={PDF_OUT}",
            HTML_OUT.as_uri(),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    print("Generated:", PDF_OUT, "bytes:", PDF_OUT.stat().st_size)


if __name__ == "__main__":
    main()
