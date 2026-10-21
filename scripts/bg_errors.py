"""Composition -> B and G errors on data/splits/val.csv, for wiki/COMPARISON_TO_LITERATURE.md.

Usage: uv run python scripts/bg_errors.py [--git-ref origin/t1/wed]

Reports MAE, RMSE (GPa) and R^2 for
  - the SVR baselines' B and G (ledger/baseline_val_preds.csv, written by eval/metrics_extra.py; refit of
    eval/tehrani_baseline.py), and
  - every Pareto equation of any bulk_modulus / shear_modulus symbolic run: those found in ledger/runs/ of this
    branch, plus (with --git-ref) those read from another ref via `git show`, without checking anything out.
Tehrani 2018 report RMSE and r^2 under 10-fold CV, so RMSE and R^2 are given next to MAE for like-for-like reading.
Bootstrap CIs (SVR rows only) resample element-set groups of val. Reads val only. Writes ledger/bg_errors.csv.
"""
import argparse
import io
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
TARGETS = {"bulk_modulus": "B", "shear_modulus": "G"}


def errs(y, p):
    y, p = np.asarray(y, float), np.asarray(p, float)
    return dict(mae=float(np.mean(np.abs(y - p))), rmse=float(np.sqrt(np.mean((y - p) ** 2))),
                r2=float(1 - np.sum((y - p) ** 2) / np.sum((y - y.mean()) ** 2)))


def boot_ci(y, p, groups, n=2000, seed=0):
    """95% percentile CI of RMSE and R^2, resampling element-set groups (the split's own grouping)."""
    y, p = np.asarray(y, float), np.asarray(p, float)
    idx = pd.Series(np.arange(len(y))).groupby(np.asarray(groups)).apply(np.array).tolist()
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        take = np.concatenate([idx[i] for i in rng.integers(0, len(idx), len(idx))])
        e = errs(y[take], p[take])
        out.append((e["rmse"], e["r2"]))
    lo, hi = np.percentile(np.array(out), [2.5, 97.5], axis=0)
    return dict(rmse_lo=lo[0], rmse_hi=hi[0], r2_lo=lo[1], r2_hi=hi[1])


def git_show(ref, path):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT, text=True)


def run_sources(ref):
    """(run_id, meta dict, equations DataFrame, origin) for every bulk/shear modulus run."""
    out = []
    for p in sorted((ROOT / "ledger/runs").glob("*.json")):
        meta = json.loads(p.read_text())
        if meta["target"] in TARGETS:
            out.append((p.stem, meta, pd.read_csv(p.with_suffix(".csv")), "this branch"))
    if ref:
        names = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", ref, "ledger/runs/"], cwd=ROOT, text=True).split()
        have = {r[0] for r in out}
        for n in names:
            if n.endswith(".json") and Path(n).stem not in have:
                meta = json.loads(git_show(ref, n))
                if meta["target"] in TARGETS:
                    out.append((Path(n).stem, meta, pd.read_csv(io.StringIO(git_show(ref, n[:-5] + ".csv"))), ref))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-ref", default=None)
    args = ap.parse_args()
    va = pd.read_csv(ROOT / "data/splits/val.csv")
    rows = []

    from eval.tehrani_baseline import element_group

    groups = va.formula.map(element_group).values
    base = pd.read_csv(ROOT / "ledger/baseline_val_preds.csv", index_col=0)
    for col in base.columns:
        if col.endswith(("_B", "_G")):
            q = "bulk_modulus" if col.endswith("_B") else "shear_modulus"
            rows.append(dict(model=col[:-2] + " SVR (log-target)", quantity=TARGETS[q], complexity=np.nan, run_id="baseline",
                             formula="", **errs(va[q], base[col]), **boot_ci(va[q], base[col], groups)))

    runs = run_sources(args.git_ref)
    if runs:
        from eval.score import eval_equation
        from sr.run_pysr import add_descriptors, magpie_means

        df, X0 = magpie_means(va.copy(), "formula")
        feats = {}
        for rid, meta, eqs, origin in runs:
            d = tuple(meta["descriptors"])
            if d not in feats:
                feats[d] = add_descriptors(df, X0, list(d))
            q = meta["target"]
            for _, e in eqs.iterrows():
                p = eval_equation(e["equation"], feats[d])
                rows.append(dict(model=f"SR ({'+'.join(d) if d else 'magpie_only'}), {origin}", quantity=TARGETS[q],
                                 complexity=int(e["complexity"]), run_id=rid, formula=e["equation"], **errs(va[q], p)))
    else:
        print("no bulk/shear-modulus symbolic runs found (pass --git-ref to read another ref)")
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "ledger/bg_errors.csv", index=False, float_format="%.5g")
    print(out[out.run_id == "baseline"][["model", "quantity", "mae", "rmse", "rmse_lo", "rmse_hi", "r2", "r2_lo", "r2_hi"]].round(3).to_string(index=False))
    sr = out[out.run_id != "baseline"]
    print(f"\n{len(sr)} SR rows from {sr.run_id.nunique()} runs")
    return out


if __name__ == "__main__":
    main()
