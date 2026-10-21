"""Overnight-3 cycle score: 3 seeds, reports mean best val_mae at c<=9 AND c<=12, plus descriptor selection.

Usage: uv run python sr/cycle_summary3.py --cycle 012 --descriptor "d_014 EN deviation" --runs c012_s0 c012_s1 c012_s2 --uses d_014
Appends to ledger/cycle_scores3.csv (the overnight-2 file cycle_scores.csv is untouched).
Reference arms (no descriptor, same search) are the v008_wo_s0..s2 / ref_s5..s8 runs; improvement vs the
same-seed reference is reported as a paired difference (seeds 0-2 of v008_wo).
"""
import argparse
import csv
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ledger/cycle_scores3.csv"
HEADER = ["cycle", "descriptor", "runs", "best_c9_per_seed", "mean_c9", "best_c12_per_seed", "mean_c12",
          "paired_diff_c9_vs_v008_wo", "paired_diff_c12_vs_v008_wo", "selected_seeds", "min_complexity_used"]
REF = ["v008_wo_s0", "v008_wo_s1", "v008_wo_s2"]


def best(res, run, w):
    d = res[(res.run_id == run) & (res.complexity >= 1) & (res.complexity <= w) & (res.descriptor_set != "baseline_mean")]
    if d.empty:
        raise SystemExit(f"no scored rows for {run}")
    return float(d.val_mae.min())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", required=True)
    ap.add_argument("--descriptor", default="")
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--uses", nargs="*", default=[], help="descriptor names to search for in equations")
    a = ap.parse_args()
    res = pd.read_csv(ROOT / "ledger/results.csv")
    out = {}
    for w in (9, 12):
        b = [best(res, r, w) for r in a.runs]
        ref = [best(res, r, w) for r in REF[: len(a.runs)]]
        out[w] = (b, sum(b) / len(b), sum(x - y for x, y in zip(b, ref)) / len(b))
    sel, minc = [], []
    for r in a.runs:
        d = res[(res.run_id == r) & (res.complexity >= 1)]
        pat = "|".join(re.escape(u) for u in a.uses) or "$^"
        u = d[d.formula.astype(str).str.contains(pat)]
        sel.append(len(u) > 0)
        minc.append(int(u.complexity.min()) if len(u) else None)
    row = [a.cycle, a.descriptor, "+".join(a.runs), "/".join(f"{x:.4f}" for x in out[9][0]), f"{out[9][1]:.4f}",
           "/".join(f"{x:.4f}" for x in out[12][0]), f"{out[12][1]:.4f}", f"{out[9][2]:+.4f}", f"{out[12][2]:+.4f}",
           "/".join(str(s) for s in sel), "/".join(str(m) for m in minc)]
    new = not OUT.exists() or OUT.stat().st_size == 0
    with open(OUT, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(HEADER)
        w.writerow(row)
    print(dict(zip(HEADER, row)))


if __name__ == "__main__":
    main()
