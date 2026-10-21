"""Cycle score under the adopted CLAUDE.md rule (>=3 seeds vs the stored 9-seed no-descriptor reference).

Usage: uv run python sr/cycle_summary3.py --cycle 020 --descriptor "d_020 name" --runs c020_s0 c020_s1 c020_s2 --uses d_020
Appends to ledger/cycle_scores4.csv (cycle_scores.csv and cycle_scores3.csv, written by earlier versions with a
different column set, are left untouched).

Rule, exactly as in CLAUDE.md:
  * per-seed score = best val_mae over Pareto rows with 1 <= complexity <= W, for W in (9, 12, 15)
  * reference = all 9 stored no-descriptor runs (v008_wo_s0-4, ref_s5-8); mean and sample sd (ddof=1) per W
  * headline = mean over seeds at c<=12
  * improvement = headline mean is >= 0.08 GPa below the reference c<=12 mean
                  AND the descriptor appears in a Pareto equation in a majority (> half) of seeds
"""
import argparse
import csv
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ledger/cycle_scores4.csv"
WINDOWS = (9, 12, 15)
HEADLINE = 12
MIN_DROP = 0.08
REF = [f"v008_wo_s{i}" for i in range(5)] + [f"ref_s{i}" for i in range(5, 9)]
HEADER = ["cycle", "descriptor", "runs"] + [f"best_c{w}_per_seed" for w in WINDOWS] + [f"mean_c{w}" for w in WINDOWS] + \
         [f"ref_mean_c{w}" for w in WINDOWS] + [f"diff_c{w}_vs_ref" for w in WINDOWS] + \
         ["selected_seeds", "n_selected", "min_complexity_used", "improvement"]


def best(res, run, w):
    d = res[(res.run_id == run) & (res.complexity >= 1) & (res.complexity <= w) & (res.descriptor_set != "baseline_mean")]
    if d.empty:
        raise SystemExit(f"no scored rows for {run}")
    return float(d.val_mae.min())


def reference_stats(res, ref=REF):
    """{w: (mean, sample sd)} over the stored reference runs."""
    out = {}
    for w in WINDOWS:
        v = [best(res, r, w) for r in ref]
        out[w] = (float(np.mean(v)), float(np.std(v, ddof=1)))
    return out


def selection(res, runs, uses):
    """Per run: (descriptor appears in any Pareto equation, min complexity of such an equation or None)."""
    pat = "|".join(re.escape(u) for u in uses) or "$^"
    sel, minc = [], []
    for r in runs:
        d = res[(res.run_id == r) & (res.complexity >= 1)]
        u = d[d.formula.astype(str).str.contains(pat)]
        sel.append(len(u) > 0)
        minc.append(int(u.complexity.min()) if len(u) else None)
    return sel, minc


def is_improvement(head_mean, ref_head_mean, n_selected, n_seeds):
    return bool(ref_head_mean - head_mean >= MIN_DROP and n_selected > n_seeds / 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", required=True)
    ap.add_argument("--descriptor", default="")
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--uses", nargs="*", default=[], help="descriptor names to search for in equations")
    a = ap.parse_args()
    if len(a.runs) < 3:
        raise SystemExit("need >=3 seeds")
    res = pd.read_csv(ROOT / "ledger/results.csv")
    ref = reference_stats(res)
    per = {w: [best(res, r, w) for r in a.runs] for w in WINDOWS}
    mean = {w: float(np.mean(per[w])) for w in WINDOWS}
    sel, minc = selection(res, a.runs, a.uses)
    imp = is_improvement(mean[HEADLINE], ref[HEADLINE][0], sum(sel), len(sel))
    row = [a.cycle, a.descriptor, "+".join(a.runs)] + ["/".join(f"{x:.4f}" for x in per[w]) for w in WINDOWS] + \
          [f"{mean[w]:.4f}" for w in WINDOWS] + [f"{ref[w][0]:.4f}" for w in WINDOWS] + \
          [f"{mean[w] - ref[w][0]:+.4f}" for w in WINDOWS] + \
          ["/".join(str(s) for s in sel), f"{sum(sel)}/{len(sel)}", "/".join(str(m) for m in minc), imp]
    new = not OUT.exists() or OUT.stat().st_size == 0
    with open(OUT, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(HEADER)
        w.writerow(row)
    print(dict(zip(HEADER, row)))
    print(f"headline c<={HEADLINE} mean {mean[HEADLINE]:.4f} vs reference {ref[HEADLINE][0]:.4f} (sd {ref[HEADLINE][1]:.4f}); improvement={imp}")


if __name__ == "__main__":
    main()
