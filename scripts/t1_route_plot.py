"""Compare hardness routes from the T1 experiment (scripts/t1_queue.sh) -> wiki/figures/t1_routes*.png.

Usage: uv run python scripts/t1_route_plot.py --seeds 0 1 2 [--plot-only]

Scores each arm with eval/compose_hv.py over complexity budgets 1-30 (train-selected val MAE; for the composed route
the budget is c_B + c_k), writes ledger/t1_routes/<arm>.csv, and plots mean over seeds with the across-seed range.
The stored 9-seed reference (niter 22k, L2, no units: a different, longer search) is drawn as gray context only.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from scripts.progress_plots import BASELINES, REF_RUNS, THEMES, legend, style, title  # noqa: E402

ARMS = {  # name: (label, compose_hv arguments with {s} = seed)
    "direct": ("direct on Hv, Magpie only", ["--direct", "t1_hv_s{s}"]),
    "direct_d023": ("direct on Hv + d_023 (cohesive-energy density)", ["--direct", "t1_hvd23_s{s}"]),
    "composed_d023": ("Chen(B, k): B with d_023, k Magpie only", ["--B", "t1_Bd23_s{s}", "--k", "t1_k_s{s}"]),
}
OUT = ROOT / "ledger/t1_routes"
REF_ARM = ("stored reference: Magpie only, 9 seeds, 22k iterations, L2 (longer search)", ["--direct", *REF_RUNS])


def score(seeds):
    OUT.mkdir(parents=True, exist_ok=True)
    for arm, (_, spec) in {**ARMS, "stored_ref": REF_ARM}.items():
        if arm == "stored_ref" and (OUT / "stored_ref.csv").exists():
            continue
        args = []
        for a in spec:
            args += [a.format(s=s) for s in seeds] if "{s}" in a else [a]
        cmd = [sys.executable, "-W", "ignore", "eval/compose_hv.py", *args, "--budgets", *map(str, range(1, 31)),
               "--out", str((OUT / f"{arm}.csv").relative_to(ROOT))]
        subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True)
        print("scored", arm)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="+", default=["0", "1", "2"])
    ap.add_argument("--plot-only", action="store_true")
    args = ap.parse_args()
    if not args.plot_only:
        score(args.seeds)

    ref_front = pd.read_csv(OUT / "stored_ref.csv").groupby("budget").trainsel_val_mae.mean()
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"]})
    for theme, t in THEMES.items():
        fig, ax = plt.subplots(figsize=(9, 5.6), facecolor=t["surface"])
        fig.subplots_adjust(left=0.08, right=0.97, top=0.82, bottom=0.11)
        style(ax, t)
        ax.plot(ref_front.index, ref_front.values, color=t["context"], linewidth=1.5, zorder=2,
                label=REF_ARM[0])
        for (arm, (label, _)), color in zip(ARMS.items(), t["series"]):
            d = pd.read_csv(OUT / f"{arm}.csv")
            g = d.groupby("budget").trainsel_val_mae
            n = d.seed.nunique()
            ax.fill_between(g.min().index, g.min(), g.max(), color=color, alpha=0.15, linewidth=0, zorder=3)
            ax.plot(g.mean().index, g.mean().values, color=color, linewidth=2, zorder=4, label=f"{label} (n={n})")
        for name, v in BASELINES.items():
            ax.axhline(v, color=t["muted"], linewidth=1, zorder=1)
            ax.text(24.3, v + 0.04, f"{name}  {v:.2f}", color=t["text2"], fontsize=8.5, ha="right", va="bottom")
        legend(ax, t, loc="upper right", bbox_to_anchor=(1.0, 0.76))
        ax.set_xlim(0.5, 24.5)
        ax.set_ylim(2.5, 5.6)
        ax.set_xlabel("complexity budget (direct: formula nodes; Chen route: nodes in B + nodes in k)")
        ax.set_ylabel("val MAE vs hv_chen (GPa)")
        title(fig, t, "One energy-density descriptor moves the whole Pareto front down",
              "Formula picked on train per budget, scored on val. Line = mean over seeds, band = range. "
              "T1 arms: L1, --units, 900 s (~4-5k iterations).")
        fig.savefig(ROOT / f"wiki/figures/t1_routes{'' if theme == 'light' else '_dark'}.png", dpi=160,
                    facecolor=t["surface"])
        plt.close(fig)
    print("wrote wiki/figures/t1_routes.png and t1_routes_dark.png")


if __name__ == "__main__":
    main()
