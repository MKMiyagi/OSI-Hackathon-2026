"""Progress figures from ledger/results.csv -> wiki/figures/*.png (light and dark).

Usage: uv run python scripts/progress_plots.py

1. mae_vs_complexity: val MAE of every run's Pareto front vs complexity, the 9-seed Magpie-only reference
   band, the best observed front, and the constant / SVR baselines.
2. mae_over_time: best-so-far val MAE at c<=9/12/15 over the agent's runs, with each run's own value.
3. descriptor_cycles: best c<=12 val MAE per descriptor cycle (per seed + mean) vs the reference band and the
   adopted improvement bar (reference mean - 0.08 GPa).

Formulas using m_MeltingT or m_SpaceGroupNumber (hidden from later searches as unphysical) are dropped.
All MAEs are development-set (val, reused for selection) numbers.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "wiki/figures"
REF_RUNS = [f"v008_wo_s{i}" for i in range(5)] + [f"ref_s{i}" for i in range(5, 9)]
# val MAE of non-formula comparators (wiki/DATA_AUDIT.md; eval/tehrani_baseline.py on t1/tehrani-baseline)
BASELINES = {"train-median constant": 5.044, "Magpie SVR (black box)": 2.817}
PHASES = [("overnight 1", "smoke search"), ("overnight 2", ""), ("overnight 3", "")]

THEMES = {
    "light": dict(surface="#fcfcfb", text="#0b0b0b", text2="#52514e", muted="#898781", grid="#e1e0d9",
                  axis="#c3c2b7", context="#d3d2cb", series=["#2a78d6", "#eb6834", "#1baf7a"]),
    "dark": dict(surface="#1a1a19", text="#f0efec", text2="#c3c2b7", muted="#898781", grid="#2c2c2a",
                 axis="#383835", context="#4a4a46", series=["#3987e5", "#d95926", "#199e70"]),
}


def load():
    r = pd.read_csv(ROOT / "ledger/results.csv")
    r = r[(r.complexity > 0) & ~r.formula.str.contains("MeltingT|SpaceGroup", na=False)].copy()
    r["ts"] = pd.to_datetime(r.timestamp).dt.tz_convert("America/Chicago")
    return r


def phase_of(run_id, search):
    if search == "smoke":
        return 0
    if run_id.startswith(("t003", "c007", "c008", "c009", "c010", "c011")):
        return 1
    return 2


def style(ax, t):
    ax.set_facecolor(t["surface"])
    ax.grid(axis="y", color=t["grid"], linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(t["axis"])
    ax.tick_params(colors=t["text2"], labelsize=9, length=0, pad=6)
    ax.xaxis.label.set_color(t["text2"])
    ax.yaxis.label.set_color(t["text2"])


def title(fig, t, head, sub):
    fig.text(0.06, 0.955, head, color=t["text"], fontsize=13, fontweight="semibold", va="top")
    fig.text(0.06, 0.905, sub, color=t["text2"], fontsize=9.5, va="top")


def legend(ax, t, **kw):
    leg = ax.legend(frameon=False, fontsize=8.5, borderaxespad=0.8, **kw)
    for txt in leg.get_texts():
        txt.set_color(t["text2"])


def baseline_lines(ax, t, x_right):
    for name, v in BASELINES.items():
        ax.axhline(v, color=t["muted"], linewidth=1, zorder=1)
        ax.text(x_right, v + 0.04, f"{name}  {v:.2f}", color=t["text2"], fontsize=8.5, ha="right", va="bottom")


def fig_complexity(r, t):
    fig, ax = plt.subplots(figsize=(9, 5.6), facecolor=t["surface"])
    fig.subplots_adjust(left=0.08, right=0.97, top=0.82, bottom=0.11)
    style(ax, t)
    main = r[r.search != "smoke"]
    for _, g in main.groupby("run_id"):
        g = g.sort_values("complexity")
        ax.plot(g.complexity, g.val_mae, color=t["context"], linewidth=0.8, zorder=2)

    ref = main[main.run_id.isin(REF_RUNS)].pivot_table(index="complexity", columns="run_id", values="val_mae")
    ref = ref[ref.notna().sum(axis=1) >= 5]
    c1 = t["series"][0]
    ax.fill_between(ref.index, ref.min(axis=1), ref.max(axis=1), color=c1, alpha=0.18, linewidth=0, zorder=3)
    ax.plot(ref.index, ref.mean(axis=1), color=c1, linewidth=2, zorder=4,
            label="Magpie-only reference, 9 seeds (mean and range)")

    best = main.groupby("complexity").val_mae.min()
    c2 = t["series"][1]
    ax.plot(best.index, best.values, "-o", color=c2, linewidth=2, markersize=6, markeredgecolor=t["surface"],
            markeredgewidth=2, zorder=6, label="best observed at each complexity, any descriptor")
    ax.plot([], [], color=t["context"], linewidth=1, label="one run's Pareto front")
    legend(ax, t, loc="upper right", bbox_to_anchor=(1.0, 0.76))
    ax.text(4, 4.95, "c1-7: every run finds the same equations", color=t["text2"], fontsize=8.5, ha="center")

    baseline_lines(ax, t, 15.4)
    for c, label in ((8, "d_008 (EN range), recurs in 9 runs"), (12, "c018_s0: 94% of gain from 10 rows")):
        v = best.loc[c]
        ax.annotate(f"{v:.2f}  {label}", (c, v), xytext=(c - 0.4, v - 0.42), color=t["text2"], fontsize=8.5,
                    ha="right", arrowprops=dict(arrowstyle="-", color=t["muted"], linewidth=0.8))
    ax.set_xlim(0.5, 15.6)
    ax.set_ylim(2.5, 5.6)
    ax.set_xticks(range(1, 16))
    ax.set_xlabel("formula complexity (PySR nodes)")
    ax.set_ylabel("val MAE vs hv_chen (GPa)")
    n = main.run_id.nunique()
    title(fig, t, "Formulas improve fast up to complexity ~9, then flatten about 1 GPa above the black box",
          f"Val MAE of each Pareto-front equation, {n} runs (gray), niter 22k/120k searches. "
          "Development-set numbers: val was reused for selection.")
    return fig


def fig_time(r, t):
    fig, ax = plt.subplots(figsize=(9, 5.6), facecolor=t["surface"])
    fig.subplots_adjust(left=0.08, right=0.97, top=0.82, bottom=0.11)
    style(ax, t)
    runs = r.groupby("run_id").agg(ts=("ts", "min"), search=("search", "first")).sort_values("ts")
    runs["phase"] = [phase_of(i, s) for i, s in zip(runs.index, runs.search)]
    for cap, color in zip((9, 12, 15), t["series"]):
        runs[f"b{cap}"] = r[r.complexity <= cap].groupby("run_id").val_mae.min()
        runs[f"cum{cap}"] = runs[f"b{cap}"].cummin()
    end = runs.ts.iloc[-1] + pd.Timedelta(minutes=8)
    for cap, color in zip((9, 12, 15), t["series"]):
        x = list(runs.ts) + [end]
        y = list(runs[f"cum{cap}"]) + [runs[f"cum{cap}"].iloc[-1]]
        ax.step(x, y, where="post", color=color, linewidth=2, zorder=4, label=f"best so far, complexity ≤ {cap}")
    ax.plot(runs.ts, runs.b12, "o", color=t["context"], markersize=5, zorder=2,
            label="one run's own best at complexity ≤ 12")
    finals = {cap: round(runs[f"cum{cap}"].iloc[-1], 2) for cap in (9, 12, 15)}
    for v in sorted(set(finals.values())):
        caps = ", ".join(f"c≤{c}" for c, f in finals.items() if f == v)
        ax.text(end + pd.Timedelta(minutes=4), v, f"{caps}  {v:.2f}", color=t["text2"], fontsize=8.5, va="center")
    legend(ax, t, loc="lower left", bbox_to_anchor=(0, 0.12))
    for p, (name, note) in enumerate(PHASES):
        sub = runs[runs.phase == p]
        if p:
            ax.axvline(sub.ts.iloc[0] - pd.Timedelta(minutes=4), color=t["axis"], linewidth=0.8, zorder=1)
        ax.text(sub.ts.iloc[0], 5.62, name + (f"\n{note}" if note else ""), color=t["text2"], fontsize=8.5,
                va="top")
    for name, v in BASELINES.items():
        ax.axhline(v, color=t["muted"], linewidth=1, zorder=1)
        ax.text(runs.ts.iloc[-1], v + 0.04, f"{name}  {v:.2f}", color=t["text2"], fontsize=8.5, ha="right",
                va="bottom")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=runs.ts.dt.tz))
    ax.set_xlim(runs.ts.iloc[0] - pd.Timedelta(minutes=10), end + pd.Timedelta(minutes=50))
    ax.set_ylim(2.5, 5.7)
    ax.set_xlabel("time the run was scored (CDT, Oct 20-21)")
    ax.set_ylabel("val MAE vs hv_chen (GPa)")
    title(fig, t, "Most of the gain came from search calibration in overnight 2, not from descriptors",
          "Best-so-far val MAE at each complexity cap (lines); gray dots = each run's own best at c≤12. "
          "Development-set numbers.")
    return fig


def fig_cycles(r, t):
    main = r[r.search == "niter22k"]
    b12 = main.groupby("run_id").apply(lambda g: g[g.complexity <= 12].val_mae.min(), include_groups=False)
    dset = main.groupby("run_id").descriptor_set.first()
    ref = b12[REF_RUNS]
    df = pd.DataFrame({"b12": b12, "dset": dset}).drop(REF_RUNS)
    df = df[df.dset != "magpie_only"]
    order = df.groupby("dset").b12.mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(9, 0.42 * len(order) + 2.2), facecolor=t["surface"])
    fig.subplots_adjust(left=0.2, right=0.97, top=1 - 1.25 / (0.42 * len(order) + 2.2), bottom=0.09)
    style(ax, t)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=t["grid"], linewidth=0.8)
    m, sd = ref.mean(), ref.std()
    c1 = t["series"][0]
    ax.axvspan(m - sd, m + sd, color=c1, alpha=0.15, linewidth=0, zorder=1)
    ax.axvline(m, color=c1, linewidth=1.5, zorder=2)
    ax.axvline(m - 0.08, color=t["text2"], linewidth=1, zorder=2)
    ypos = {d: i for i, d in enumerate(order.index)}
    ax.plot(df.b12, df.dset.map(ypos), "o", color=t["context"], markersize=5, zorder=3)
    ax.plot(order.values, range(len(order)), "o", color=c1, markersize=8, markeredgecolor=t["surface"],
            markeredgewidth=2, zorder=4)
    top = len(order) - 0.45
    ax.text(m + 0.004, top, f"reference {m:.2f} ± {sd:.2f}", color=t["text2"], fontsize=8.5, va="bottom")
    ax.text(m - 0.084, top, f"improvement bar {m - 0.08:.2f}", color=t["text2"], fontsize=8.5, va="bottom",
            ha="right")
    ax.annotate("3.911 = the recurring Magpie-only c12 equation\n(38 runs, with or without a descriptor)",
                (3.9114, len(order) - 1), xytext=(4.14, len(order) - 2.9), color=t["text2"], fontsize=8.5,
                ha="center", arrowprops=dict(arrowstyle="-", color=t["muted"], linewidth=0.8))
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([f"{d}  (n={int((df.dset == d).sum())})" for d in order.index])
    ax.set_ylim(-0.6, len(order) - 0.1)
    ax.set_xlabel("best val MAE at complexity ≤ 12 (GPa)")
    title(fig, t, "No descriptor cleared the improvement bar at complexity ≤ 12",
          "Large dot = mean over seeds, small dots = individual seeds (niter 22k). "
          "Band = 9-seed Magpie-only reference mean ± 1 sd.")
    return fig


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    r = load()
    for theme, t in THEMES.items():
        plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"]})
        for name, fn in (("mae_vs_complexity", fig_complexity), ("mae_over_time", fig_time),
                         ("descriptor_cycles", fig_cycles)):
            fig = fn(r, t)
            suffix = "" if theme == "light" else "_dark"
            fig.savefig(OUT / f"{name}{suffix}.png", dpi=160, facecolor=t["surface"])
            plt.close(fig)
    print("wrote", sorted(p.name for p in OUT.glob("*.png")))


if __name__ == "__main__":
    main()
