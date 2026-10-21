"""Secondary-metric figures from ledger/metrics_extra.csv -> wiki/figures/*.png (light and dark).

Usage: uv run python eval/metrics_extra.py --all && uv run python scripts/metrics_plots.py

a. metrics_mase_vs_complexity: MASE vs the SVR (1.0 = black box) against complexity, every descriptor set.
b. metrics_binned_mae: stratified MAE (bins of the true value) for the 3 frozen compact candidates + SVR + constant.
c. metrics_scatter_best_c9: predicted vs true for the best c<=9 formula, coloured by bin, y >= 20 GPa tail ringed.
d. metrics_rank_vs_complexity: precision at the top 10% vs complexity.
Also writes ledger/metrics_extra_summary.csv (the table view of figures a-d: per arm and complexity budget).
Smoke runs and equations using m_MeltingT / m_SpaceGroupNumber are dropped, as in scripts/progress_plots.py.
All numbers are development-set (val, reused) numbers; the best-so-far envelopes select on val MAE (optimistic).
"""
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from scripts.progress_plots import REF_RUNS, THEMES, legend, style, title  # noqa: E402

OUT = ROOT / "wiki/figures"
TAIL = 20.0  # GPa; same tail definition as eval/tehrani_baseline.py (val_mae_tail20)
VIOLET = {"light": "#6250d6", "dark": "#9085e9"}  # categorical slot 7 (4th bar colour in fig b)
BIN_LABELS = ["<5", "5-15", "15-25", ">=25"]
BIN_COLS = ["mae_lt5", "mae_5_15", "mae_15_25", "mae_ge25"]
# ordinal blue steps (palette.md sequential hue), light-surface and dark-surface
BIN_RAMP = {"light": ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"], "dark": ["#184f95", "#2a78d6", "#6da7ec", "#cde2fb"]}
ARMS = {  # arm name -> run ids (headline arms of CLAUDE.md / OVERNIGHT_4_SUMMARY)
    "Magpie only (9-seed reference)": REF_RUNS,
    "+ d_023 (cycle 020)": [f"c020_s{i}" for i in range(3)],
    "+ d_023, units-constrained (027)": [f"c027_s{i}" for i in range(3)],
}
# frozen candidates (OVERNIGHT_4_SUMMARY: CANDIDATE_FORMULAS overnight-4 #8 c5, #1 c8, #4 c9 unit-consistent)
CANDIDATES = [("c5  d_023/(NdVal+k)", "c020_s0", 5), ("c8  d_023/(NdVal+sqrt(Col))+NpUnf", "c020_s0", 8),
              ("c9  unit-consistent", "c027_s0", 9)]


def heading(fig, t, head, sub, width=105):
    title(fig, t, head, textwrap.fill(sub, width))


def load():
    m = pd.read_csv(ROOT / "ledger/metrics_extra.csv")
    base = m[m.run_id == "baseline"].set_index("descriptor_set")
    eq = m[(m.run_id != "baseline") & ~m.uses_excluded_feature & (m.run_id != "smoke_001")].copy()
    eq["complexity"] = eq.complexity.astype(int)
    eq["set"] = np.where(eq.run_id.str.startswith("c027"), "d_023 [units, 027]", eq.descriptor_set)
    return eq, base


def envelope(g, col, cmax=15):
    """Running best (min of col over complexity <= c) for one run, c = 1..cmax."""
    best = g.groupby("complexity")[col].min().reindex(range(1, cmax + 1))
    return best.cummin().ffill()


def mean_envelope(eq, runs, col="mase_svr"):
    env = pd.DataFrame({r: envelope(eq[eq.run_id == r], col) for r in runs})
    return env


def pick(eq, run, c):
    x = eq[(eq.run_id == run) & (eq.complexity == c)]
    assert len(x) == 1, (run, c, len(x))
    return x.iloc[0]


def predict(formula, descs):
    from eval.score import eval_equation
    from sr.run_pysr import add_descriptors, magpie_means

    va = pd.read_csv(ROOT / "data/splits/val.csv")
    df, X0 = magpie_means(va.copy(), "formula")
    return va.hv_chen.values, eval_equation(formula, add_descriptors(df, X0, descs))


def fig_mase(eq, base, t, th):
    fig, ax = plt.subplots(figsize=(9, 5.6), facecolor=t["surface"])
    fig.subplots_adjust(left=0.08, right=0.97, top=0.80, bottom=0.11)
    style(ax, t)
    highlighted = {"magpie_only", "d_023"}
    for s, g in eq.groupby("set"):
        if s in highlighted:
            continue
        env = pd.DataFrame({r: envelope(h, "mase_svr") for r, h in g.groupby("run_id")}).mean(axis=1)
        ax.plot(env.index, env.values, color=t["context"], linewidth=0.8, zorder=2)
    ax.plot([], [], color=t["context"], linewidth=1, label="other descriptor sets (one line per set)")
    for (name, runs), color in zip(ARMS.items(), t["series"]):
        env = mean_envelope(eq, runs)
        if len(runs) > 3:
            ax.fill_between(env.index, env.min(axis=1), env.max(axis=1), color=color, alpha=0.18, linewidth=0, zorder=3)
        ax.plot(env.index, env.mean(axis=1), color=color, linewidth=2, zorder=4, label=name,
                linestyle="--" if "units" in name else "-")
    svr = base.loc["svr_magpie_BG", "mase_svr"]
    ax.axhline(1.0, color=t["text"], linewidth=1.2, zorder=1)
    ax.text(15.4, 1.0 - 0.012, "1.0 = black box (Magpie SVR, log B, log G -> Chen)", color=t["text"], fontsize=8.5,
            ha="right", va="top")
    cst = base.loc["train_median", "mase_svr"]
    ax.axhline(cst, color=t["muted"], linewidth=1, zorder=1)
    ax.text(15.4, cst + 0.012, f"train-median constant  {cst:.2f}", color=t["text2"], fontsize=8.5, ha="right", va="bottom")
    legend(ax, t, loc="upper right", bbox_to_anchor=(1.0, 0.86))
    ax.set_xlim(0.5, 15.6)
    ax.set_ylim(0.9, 1.85)
    ax.set_xticks(range(1, 16))
    ax.set_xlabel("formula complexity (PySR nodes), best-so-far envelope")
    ax.set_ylabel("MASE vs SVR  (val MAE / SVR val MAE)")
    heading(fig, t, "No formula reaches the black box: the best is 1.27x its MAE",
          "val MAE / SVR val MAE, best-so-far over complexity, mean over seeds (band = range, 9-seed arm). "
          "Development-set numbers; envelope selects on val.")
    return fig


def fig_binned(eq, base, t, th):
    models = [("train-median constant", base.loc["train_median", BIN_COLS].values.astype(float), t["context"]),
              ("Magpie SVR (black box)", base.loc["svr_magpie_BG", BIN_COLS].values.astype(float), t["series"][1])]
    for (label, run, c), color in zip(CANDIDATES, (t["series"][0], t["series"][2], VIOLET[th])):
        models.append((label, pick(eq, run, c)[BIN_COLS].values.astype(float), color))
    n = base.loc["svr_magpie_BG", ["n_lt5", "n_5_15", "n_15_25", "n_ge25"]].astype(int).values
    fig, ax = plt.subplots(figsize=(9.6, 5.6), facecolor=t["surface"])
    fig.subplots_adjust(left=0.08, right=0.97, top=0.80, bottom=0.14)
    style(ax, t)
    w = 0.16
    for i, (label, vals, color) in enumerate(models):
        x = np.arange(4) + (i - (len(models) - 1) / 2) * (w + 0.015)
        ax.bar(x, vals, width=w, color=color, label=label, linewidth=0, zorder=3)
    ax.set_xticks(range(4))
    ax.set_xticklabels([f"{b} GPa\n(n = {k})" for b, k in zip(BIN_LABELS, n)])
    ax.set_xlabel("bin of the TRUE hv_chen value")
    ax.set_ylabel("MAE within bin (GPa)")
    legend(ax, t, loc="upper left")
    heading(fig, t, "In the bulk, formulas barely beat the constant and trail the SVR",
            "Binned MAE on val (c5 / c8 / c9 candidates). Conditioning on the true value flatters flat predictors in the "
            "middle bins; the >=25 bin has n = 10, so its ranking of the models is not reliable.")
    return fig


def fig_scatter(eq, base, t, th):
    best = eq[eq.complexity <= 9].sort_values("mae").iloc[0]
    run = best.run_id
    import json
    descs = json.loads((ROOT / f"ledger/runs/{run}.json").read_text())["descriptors"]
    y, p = predict(best.formula, descs)
    assert abs(np.mean(np.abs(y - p)) - best.mae) < 1e-4
    idx = np.digitize(y, (5, 15, 25))
    fig, ax = plt.subplots(figsize=(7.4, 6.4), facecolor=t["surface"])
    fig.subplots_adjust(left=0.1, right=0.97, top=0.82, bottom=0.11)
    style(ax, t)
    ax.grid(axis="x", color=t["grid"], linewidth=0.8)
    lim = (-5, 52)
    ax.plot(lim, lim, color=t["muted"], linewidth=1, zorder=1)
    for b, (lab, col) in enumerate(zip(BIN_LABELS, BIN_RAMP[th])):
        s = idx == b
        ax.scatter(y[s], p[s], s=26, color=col, edgecolor=t["surface"], linewidth=0.8, zorder=3,
                   label=f"true {lab} GPa (n = {s.sum()})")
    tail = y >= TAIL
    ax.scatter(y[tail], p[tail], s=95, facecolor="none", edgecolor=t["text"], linewidth=1.4, zorder=4,
               label=f"tail, true >= {TAIL:.0f} GPa (n = {tail.sum()}): MAE {np.mean(np.abs(y[tail]-p[tail])):.1f}, "
                     f"mean signed error {np.mean(p[tail]-y[tail]):+.1f}")
    ax.set_xlim(*lim)
    ax.set_ylim(*lim)
    ax.set_xlabel("true hv_chen (GPa)")
    ax.set_ylabel("predicted (GPa)")
    legend(ax, t, loc="upper left")
    sgn = np.mean(p[tail] - y[tail])
    heading(fig, t, f"Best c<=9 formula underpredicts the tail by {-sgn:.1f} GPa",
            f"{run}, c{int(best.complexity)}, val MAE {best.mae:.2f} (development-set val): "
            + best.formula.replace("m_", ""), width=78)
    return fig, best


def fig_rank(eq, base, t, th):
    fig, ax = plt.subplots(figsize=(9, 5.6), facecolor=t["surface"])
    fig.subplots_adjust(left=0.08, right=0.97, top=0.80, bottom=0.11)
    style(ax, t)
    ax.scatter(eq.complexity, eq.prec_top10, s=14, color=t["context"], zorder=2, linewidth=0,
               label="every Pareto equation, all runs")
    for (name, runs), color in zip(ARMS.items(), t["series"]):
        g = eq[eq.run_id.isin(runs)].groupby("complexity").prec_top10.mean()
        ax.plot(g.index, g.values, "-o", color=color, linewidth=2, markersize=6, markeredgecolor=t["surface"],
                markeredgewidth=2, zorder=4, label=name + " (mean over seeds)")
    svr = base.loc["svr_magpie_BG", "prec_top10"]
    ax.axhline(svr, color=t["text"], linewidth=1.2, zorder=1)
    ax.text(15.4, svr + 0.008, f"Magpie SVR  {svr:.2f}", color=t["text"], fontsize=8.5, ha="right", va="bottom")
    ch = base.loc["train_median", "prec_top10"]
    ax.axhline(ch, color=t["muted"], linewidth=1, zorder=1)
    ax.text(15.4, ch + 0.008, f"chance / constant  {ch:.2f}", color=t["text2"], fontsize=8.5, ha="right", va="bottom")
    legend(ax, t, loc="lower right", bbox_to_anchor=(1.0, 0.16))
    ax.set_xlim(0.5, 15.6)
    ax.set_ylim(0, 0.8)
    ax.set_xticks(range(1, 16))
    ax.set_xlabel("formula complexity (PySR nodes)")
    ax.set_ylabel("precision at top 10% (38 of 374 val rows)")
    heading(fig, t, "Only with d_023 do formulas approach the SVR's top-decile precision",
          "Fraction of the 38 highest predictions that are in the true top 38. One miss = 0.026; sampling SE is about 0.08. "
          "Development-set val.")
    return fig


def summary(eq, base):
    rows = []
    for name, runs in ARMS.items():
        for c in (9, 12, 15):
            picked = []
            for r in runs:
                x = eq[(eq.run_id == r) & (eq.complexity <= c)]
                picked.append(x.loc[x.mae.idxmin()])
            d = pd.DataFrame(picked)
            row = dict(arm=name, budget=f"c<={c}", n_seeds=len(d))
            row.update({k: d[k].mean() for k in ["mae", "mase_const", "mase_svr", "gap_closed", "log_mae", *BIN_COLS,
                                                  "spearman", "prec_top10"]})
            row["n_log_fail"] = int(d.n_log_fail.sum())
            rows.append(row)
    for name in base.index:
        r = base.loc[name]
        row = dict(arm=name, budget="baseline", n_seeds=1)
        row.update({k: r[k] for k in ["mae", "mase_const", "mase_svr", "gap_closed", "log_mae", *BIN_COLS, "spearman", "prec_top10"]})
        row["n_log_fail"] = int(r.n_log_fail)
        rows.append(row)
    s = pd.DataFrame(rows)
    s.to_csv(ROOT / "ledger/metrics_extra_summary.csv", index=False, float_format="%.4f")
    return s


def main():
    OUT.mkdir(exist_ok=True)
    eq, base = load()
    s = summary(eq, base)
    for th, t in THEMES.items():
        sfx = "" if th == "light" else "_dark"
        fig_scatter_, best = fig_scatter(eq, base, t, th)
        for name, fig in (("metrics_mase_vs_complexity", fig_mase(eq, base, t, th)),
                          ("metrics_binned_mae", fig_binned(eq, base, t, th)),
                          ("metrics_scatter_best_c9", fig_scatter_),
                          ("metrics_rank_vs_complexity", fig_rank(eq, base, t, th))):
            fig.savefig(OUT / f"{name}{sfx}.png", dpi=160, facecolor=t["surface"])
            plt.close(fig)
    print(s.round(3).to_string())
    print("best c<=9:", best.run_id, best.complexity, best.mae, best.formula)
    for label, run, c in CANDIDATES:
        print(label, "->", pick(eq, run, c).formula)


if __name__ == "__main__":
    main()
