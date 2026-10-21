"""Two-seed cycle score from ledger/results.csv (reads it, never edits score.py or splits).

Usage: uv run python sr/cycle_summary.py --cycle 007 --descriptor "d_007 BCN fraction" --runs c007_s0 c007_s1
       uv run python sr/cycle_summary.py --cycle ref_d003 --reference --runs t003b_s0 t003b_s1

Cycle score = mean over seeds of the best val_mae at complexity <= MAX_C (9). Improvement = score is
>= MIN_DROP (0.05 GPa) below the best previous non-reference-or-reference score in ledger/cycle_scores.csv.
Appends one row to ledger/cycle_scores.csv and prints the streak of consecutive non-improving cycles.
"""
import argparse
import csv
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
MAX_C, MIN_DROP = 9, 0.05
OUT = ROOT / "ledger/cycle_scores.csv"
HEADER = ["cycle", "descriptor", "runs", "per_seed_best", "mean_best", "best_previous", "improved", "streak", "reference"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", required=True)
    ap.add_argument("--descriptor", default="")
    ap.add_argument("--runs", nargs=2, required=True)
    ap.add_argument("--reference", action="store_true", help="starting reference; not counted toward the streak")
    a = ap.parse_args()

    res = pd.read_csv(ROOT / "ledger/results.csv")
    best = []
    for r in a.runs:
        d = res[(res.run_id == r) & (res.complexity >= 1) & (res.complexity <= MAX_C) & (res.split == "val")]
        d = d[d.descriptor_set != "baseline_mean"]
        if d.empty:
            raise SystemExit(f"no scored rows for run {r}")
        best.append(float(d.val_mae.min()))
    mean = sum(best) / len(best)

    prev = pd.read_csv(OUT) if OUT.exists() and OUT.stat().st_size else pd.DataFrame(columns=HEADER)
    best_prev = float(prev.mean_best.min()) if len(prev) else float("nan")
    improved = bool(len(prev) == 0 or mean <= best_prev - MIN_DROP)
    if a.reference:
        streak = 0
    else:
        streak = 0 if improved else int(prev.streak.iloc[-1]) + 1 if len(prev) else 0
    row = [a.cycle, a.descriptor, "+".join(a.runs), "/".join(f"{b:.4f}" for b in best), f"{mean:.4f}",
           f"{best_prev:.4f}", improved, streak, a.reference]
    new = not OUT.exists() or OUT.stat().st_size == 0
    with open(OUT, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(HEADER)
        w.writerow(row)
    print(f"cycle {a.cycle}: per-seed best (c<={MAX_C}) {best} mean {mean:.4f}; best previous {best_prev:.4f}; "
          f"improved={improved}; consecutive non-improving={streak}")


if __name__ == "__main__":
    main()
