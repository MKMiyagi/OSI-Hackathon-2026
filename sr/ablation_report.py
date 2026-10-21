"""Paired with/without ablation report from ledger/results.csv.

Usage: uv run python sr/ablation_report.py --with v008_w_s0 ... --without v008_wo_s0 ... [--desc d_008]

Runs are paired by position (the i-th --with run and i-th --without run share a seed). For each
complexity window c<=W reports best val_mae mean +- sd (ddof=1) per arm, the paired per-seed
difference (with - without; negative = descriptor helps), how many seeds selected the descriptor
(in any Pareto equation) and at what minimum complexity, plus the single best c<=9 equation per arm.
"""
import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
WINDOWS = (6, 9, 12, 15)


def best(res, run, w):
    d = res[(res.run_id == run) & (res.complexity >= 1) & (res.complexity <= w) & (res.descriptor_set != "baseline_mean")]
    if d.empty:
        raise SystemExit(f"no scored rows for {run}")
    return d.loc[d.val_mae.idxmin()]


def ms(x):
    x = np.asarray(x, float)
    return f"{x.mean():.4f} +- {x.std(ddof=1) if len(x) > 1 else float('nan'):.4f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--with", dest="w", nargs="+", required=True)
    ap.add_argument("--without", dest="wo", nargs="+", required=True)
    ap.add_argument("--desc", default="d_008")
    a = ap.parse_args()
    if len(a.w) != len(a.wo):
        raise SystemExit("--with and --without must have equal length (paired by seed)")
    res = pd.read_csv(ROOT / "ledger/results.csv")
    n = len(a.w)

    print(f"| window | with (mean +- sd, n={n}) | without (mean +- sd) | paired diff with-without (mean +- sd) | seeds with<without |")
    print("|---|---|---|---|---|")
    for W in WINDOWS:
        bw = [float(best(res, r, W).val_mae) for r in a.w]
        bo = [float(best(res, r, W).val_mae) for r in a.wo]
        diff = np.array(bw) - np.array(bo)
        print(f"| c<={W} | {ms(bw)} | {ms(bo)} | {ms(diff)} | {(diff < -1e-4).sum()}/{n} (ties {(abs(diff) <= 1e-4).sum()}) |")

    print(f"\nPer-seed best val_mae (with / without):")
    for W in WINDOWS:
        print(f"  c<={W}: " + ", ".join(f"{best(res, x, W).val_mae:.4f}/{best(res, y, W).val_mae:.4f}" for x, y in zip(a.w, a.wo)))

    print(f"\nSelection of {a.desc} in the 'with' arm:")
    sel = 0
    for r in a.w:
        d = res[(res.run_id == r) & (res.complexity >= 1)]
        u = d[d.formula.astype(str).str.contains(a.desc)]
        sel += len(u) > 0
        print(f"  {r}: {len(u)}/{len(d)} Pareto points use it; min complexity "
              f"{int(u.complexity.min()) if len(u) else '-'}")
    print(f"  seeds selecting {a.desc}: {sel}/{n}")

    for name, runs in (("with", a.w), ("without", a.wo)):
        cands = [best(res, r, 9) for r in runs]
        b = min(cands, key=lambda s: s.val_mae)
        print(f"\nBest compact (c<=9) equation, {name} arm: run {b.run_id} c{int(b.complexity)} val {b.val_mae:.4f}\n  {b.formula}")
        # structure only: fitted constants differ run to run, so mask numeric literals
        eqs = pd.Series([re.sub(r"(?<![\w.])\d+\.?\d*(e-?\d+)?", "C", c.formula) for c in cands]).value_counts()
        print(f"  distinct textual forms of per-seed c<=9 winners (constants masked; NOT algebraic equivalence): {len(eqs)}; most common ({eqs.iloc[0]}/{n}): {eqs.index[0]}")


if __name__ == "__main__":
    main()
