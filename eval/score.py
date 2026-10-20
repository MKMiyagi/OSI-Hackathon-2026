"""Score a PySR Pareto run on data/splits/val.csv (MAE in GPa) and append to the ledger.

Usage: uv run python eval/score.py --run <id>

Reads ledger/runs/<id>.csv (+ <id>.json sidecar with the descriptor list), featurizes val
with the same pipeline as run_pysr.py (imported, not duplicated), evaluates each equation,
and appends one row per equation to ledger/results.csv. Also logs the train-mean baseline.
Fails loudly on any NaN/inf prediction.
"""
import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import sympy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from sr.run_pysr import featurize  # noqa: E402

HEADER = ["run_id", "timestamp", "branch", "descriptor_set", "split", "complexity", "val_mae", "formula", "notes"]


def append_rows(rows):
    path = ROOT / "ledger/results.csv"
    new = not path.exists() or path.stat().st_size == 0
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(HEADER)
        w.writerows(rows)


def eval_equation(eq, X):
    syms = {c: sympy.Symbol(c) for c in X.columns}
    expr = sympy.sympify(eq, locals=syms)
    used = sorted(expr.free_symbols, key=lambda s: s.name)
    fn = sympy.lambdify(used, expr, modules="numpy")
    pred = fn(*[X[s.name].values for s in used])
    return np.broadcast_to(np.asarray(pred, dtype=float), (len(X),)).copy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    args = ap.parse_args()

    run_csv = ROOT / f"ledger/runs/{args.run}.csv"
    meta = json.loads((ROOT / f"ledger/runs/{args.run}.json").read_text())
    target = meta["target"]
    descs = meta["descriptors"]
    eqs = pd.read_csv(run_csv)

    val = pd.read_csv(ROOT / "data/splits/val.csv")
    val, X = featurize(val, descs, meta.get("formula_col", "formula"))
    y = val[target].astype(float).values
    if not np.isfinite(X.astype(float).values).all():
        bad = (~np.isfinite(X.astype(float).values)).any(axis=1).sum()
        raise SystemExit(f"{bad}/{len(X)} val rows have non-finite features; refusing to score")

    train_mean = pd.read_csv(ROOT / "data/splits/train.csv")[target].mean()
    base_mae = float(np.mean(np.abs(y - train_mean)))
    print(f"baseline (train-mean {train_mean:.3f}) val MAE: {base_mae:.4f} GPa")

    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        branch = "unknown"
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    dset = "+".join(descs) if descs else "magpie_only"

    rows = []
    existing = (ROOT / "ledger/results.csv").read_text() if (ROOT / "ledger/results.csv").exists() else ""
    if "baseline_mean" not in existing:
        rows.append([args.run, ts, branch, "baseline_mean", "val", 0, f"{base_mae:.6f}", f"{train_mean:.6f}", "predict train-mean target"])

    for _, r in eqs.iterrows():
        pred = eval_equation(r["equation"], X)
        if not np.isfinite(pred).all():
            raise SystemExit(f"non-finite predictions for equation (complexity {r['complexity']}): {r['equation']}")
        mae = float(np.mean(np.abs(y - pred)))
        rows.append([args.run, ts, branch, dset, "val", int(r["complexity"]), f"{mae:.6f}", r["equation"], f"train_loss={r['loss']:.6g}"])
        print(f"complexity {int(r['complexity']):>2}  val_mae {mae:8.4f}  {r['equation']}")
    append_rows(rows)
    print(f"appended {len(rows)} rows to ledger/results.csv")


if __name__ == "__main__":
    main()
