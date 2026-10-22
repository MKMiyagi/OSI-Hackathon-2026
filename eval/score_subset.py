"""Supplementary scorer for covered-subset runs (does NOT touch eval/score.py or ledger/results.csv).

Usage: uv run python eval/score_subset.py --runs c0s0_s0 ... [--require d_030]
Scores each Pareto equation of the given runs on the val rows where every offered descriptor is finite (the same rows for
every arm; eval/score.py refuses non-finite val features), appends to ledger/subset_results.csv, and prints the train-median
constant and primary-SVR MAE on the same rows. Val only; the test file is never read.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from eval.score import eval_equation  # noqa: E402
from sr.run_pysr import featurize  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--mask", nargs="+", default=["d_030"], help="descriptors that define the covered rows")
    args = ap.parse_args()
    val = pd.read_csv(ROOT / "data/splits/val.csv")
    val, X = featurize(val, sorted(set(args.mask) | {"d_023"}))
    cover = np.isfinite(X[args.mask].values).all(axis=1)
    y = val.hv_chen.values
    base = pd.read_csv(ROOT / "ledger/baseline_val_preds.csv", index_col=0)
    print(f"covered val rows {cover.sum()}/{len(cover)}; const MAE {np.mean(np.abs(y[cover]-base.train_median.values[cover])):.4f}; "
          f"SVR MAE {np.mean(np.abs(y[cover]-base.svr_magpie_BG.values[cover])):.4f}")
    rows = []
    for run in args.runs:
        meta = json.loads((ROOT / f"ledger/runs/{run}.json").read_text())
        _, Xr = featurize(pd.read_csv(ROOT / "data/splits/val.csv"), meta["descriptors"])
        for _, r in pd.read_csv(ROOT / f"ledger/runs/{run}.csv").iterrows():
            pred = eval_equation(r["equation"], Xr)[cover]
            if not np.isfinite(pred).all():
                raise SystemExit(f"non-finite prediction on covered rows: {run} c{r['complexity']}")
            rows.append(dict(run_id=run, descriptors="+".join(meta["descriptors"]), complexity=int(r["complexity"]),
                             val_mae_covered=float(np.mean(np.abs(y[cover] - pred))), n_rows=int(cover.sum()), equation=r["equation"]))
    out = pd.DataFrame(rows)
    path = ROOT / "ledger/subset_results.csv"
    if path.exists():
        old = pd.read_csv(path)
        out = pd.concat([old[~old.run_id.isin(args.runs)], out], ignore_index=True)
    out.to_csv(path, index=False)
    print(f"wrote {len(rows)} rows to ledger/subset_results.csv")
