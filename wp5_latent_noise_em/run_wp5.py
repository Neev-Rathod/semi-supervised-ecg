"""Run the three WP5 experiments on WP1 features and the WP2 generator."""
import argparse
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from threadpoolctl import threadpool_limits

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared.data_utils import load_standard_split, SUPERCLASSES
from shared.metrics import evaluate_model, frobenius_error
from wp2_synthetic_baselines.synthetic_generator import generate_manifold, inject_uniform_noise, inject_asymmetric_noise
from wp3_graph_propagation.label_propagation import GraphLabelPropagator
from wp4_cotraining_tsvm.cotraining import CoTrainer
from wp5_latent_noise_em.latent_noise_em import LatentNoiseEM


def heatmap(table, title, xlabel, ylabel, path, difference=False, ranked=()):
    fig, ax = plt.subplots(figsize=(8, 6))
    lim = max(abs(table.values).max(), 0.001) if difference else 1
    im = ax.imshow(table, cmap="RdBu" if difference else "Blues",
                   vmin=-lim if difference else 0, vmax=lim, aspect="auto")
    ax.set(xticks=range(len(table.columns)), xticklabels=table.columns,
           yticks=range(len(table)), yticklabels=table.index, title=title, xlabel=xlabel, ylabel=ylabel)
    for (i, j), value in np.ndenumerate(table.values):
        rank = f" (#{ranked.index((i,j))+1})" if (i,j) in ranked else ""
        ax.text(j, i, f"{value:.3f}{rank}", ha="center", va="center",
                color="white" if abs(value)>0.65*lim else "black")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run_grid(s, etas, epsilons, out, seed):
    rows = []
    for eta in etas:
        x, _, y, _ = train_test_split(s["X_train_L"], s["y_train_L"], train_size=eta,
                                      stratify=s["y_train_L"], random_state=seed)
        def score(model, labels=None):
            model.fit(x, y, s["X_train_U"], labels)
            metrics = evaluate_model(model, s["X_val"], s["y_val"])
            metrics.pop("confusion_matrix")
            metrics.update({f"f1_{k}": v for k,v in metrics.pop("per_class_f1").items()})
            if isinstance(model, LatentNoiseEM):
                metrics.update(em_iterations=model.n_iter_, em_delta=model.delta_)
            return metrics
        graph = score(GraphLabelPropagator())
        co = score(CoTrainer(random_state=seed))
        for eps in epsilons:
            noisy = inject_uniform_noise(s["y_train_U"], eps, seed=seed)
            em = score(LatentNoiseEM(), noisy)
            for name, metrics in [("EM", em), ("GraphLP", graph), ("CoTrain", co)]:
                rows.append(dict(eta=eta, epsilon=eps, n_gold=len(y), method=name, **metrics))
            print(f"eta={eta} eps={eps} n_gold={len(y)} F1 EM={em['macro_f1']} GraphLP={graph['macro_f1']} CoTrain={co['macro_f1']}", flush=True)
    table = pd.DataFrame(rows)
    table.to_csv(out/"discard_vs_correct.csv", index=False)
    pivot = table.pivot(index="eta", columns=["method","epsilon"], values="macro_f1")
    heatmap(pivot.EM-pivot.GraphLP, "Validation macro F1 difference (EM minus GraphLP)",
            "Additional pool label corruption", "Fraction of WP1 gold set", out/"discard_vs_correct_heatmap.png", True)


def run_audit(s, mask, out):
    model = LatentNoiseEM(max_iter=50).fit(s["X_train_L"], s["y_train_L"], s["X_train_U"][mask], s["y_train_U"][mask])
    table = pd.DataFrame(model.T_hat_, index=SUPERCLASSES, columns=SUPERCLASSES)
    table.to_csv(out/"T_hat.csv")
    ranked = sorted(((i,j) for i,j in np.ndindex(5,5) if i!=j), key=lambda ij: -model.T_hat_[ij])[:3]
    print(f"Audit: {sum(mask)} pool records, {model.n_iter_} iterations, delta={model.delta_:.6g}\n{table}", flush=True)
    heatmap(table, "Estimated PTB-XL label transitions", "Observed label", "Latent class", out/"T_hat_heatmap.png", ranked=ranked)


def run_recovery(out, seed):
    x, y = generate_manifold(5500, seed=seed)
    truth = np.full((5,5), 0.075)
    np.fill_diagonal(truth, 0.70)
    noisy = inject_asymmetric_noise(y[500:], truth, seed=seed+1)
    rows = []
    for n in [100,300,500,1000,2000,5000]:
        model = LatentNoiseEM(max_iter=50).fit(x[:500], y[:500], x[500:500+n], noisy[:n])
        error = frobenius_error(model.T_hat_, truth)
        rows.append((n,error,model.n_iter_,model.delta_))
        print(f"Recovery n={n}, Frobenius error={error:.5f}", flush=True)
    frame = pd.DataFrame(rows, columns=["n_pool","frobenius_error","em_iterations","em_delta"])
    frame.to_csv(out/"frobenius_recovery.csv", index=False)
    ax = frame.plot(x="n_pool", y="frobenius_error", marker="o", legend=False)
    ax.set(xlabel="Noisy pool size", ylabel="Frobenius error", title="Synthetic transition matrix recovery")
    ax.figure.tight_layout()
    ax.figure.savefig(out/"frobenius_recovery.png", dpi=150)
    plt.close(ax.figure)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("features_path","labels_path"):
        p.add_argument("--"+name, required=True)
    p.add_argument("--meta_path", help="Raw ptbxl_database.csv for automated-only audit")
    p.add_argument("--out_dir", type=Path, default=Path("../outputs/wp5"))
    p.add_argument("--eta_values", default="0.02,0.05,0.10,0.20,0.50")
    p.add_argument("--epsilon_values", default="0,0.15,0.30,0.45")
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    s = load_standard_split(a.features_path, a.labels_path)
    print("Split sizes:", {k:len(v) for k,v in s.items() if k.startswith("X_")}, flush=True)
    mask = np.ones(len(s["X_train_U"]), dtype=bool)
    if a.meta_path:
        z = np.load(a.labels_path)
        m = pd.read_csv(a.meta_path).set_index("ecg_id").loc[z["ecg_ids"]]
        if not np.array_equal(m.strat_fold, z["fold"]):
            raise ValueError("WP1/raw fold mismatch")
        pool = np.isin(z["fold"], range(1,9)) & ~z["gold_mask"] & (z["y"]!=-1)
        mask = (m.initial_autogenerated_report.eq(True) & m.validated_by_human.eq(False)).to_numpy()[pool]
    with threadpool_limits(limits=1):
        run_recovery(a.out_dir, a.seed)
        run_audit(s, mask, a.out_dir)
        run_grid(s, list(map(float,a.eta_values.split(","))), list(map(float,a.epsilon_values.split(","))), a.out_dir, a.seed)


if __name__ == "__main__":
    main()
