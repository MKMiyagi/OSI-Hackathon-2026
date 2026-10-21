"""Paired cluster-bootstrap CI for 'fraction of the constant-to-SVR gap closed' (a rewriting of pre-registered metrics 1-3).

Usage: uv run python scripts/gap_closed_ci.py
Resamples val element-set groups (the split's grouping) with replacement; on each draw recomputes the MAE of the
formula, the train-median constant and the primary SVR (Magpie, log B, log G -> Chen) on the same rows, then
gap = (MAE_const - MAE_formula) / (MAE_const - MAE_svr). 5000 draws, seed 0, percentile 95% interval.
Formulas: the three frozen candidates (c5, c8, c9 unit-consistent) and the saturated no-descriptor c9 equation.
Development-set numbers (val, reused); the intervals do not include seed or selection variance.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from eval.tehrani_baseline import element_group  # noqa: E402
from scripts.metrics_plots import predict  # noqa: E402

CANDS = [("c5  d_023/(NdVal+k)", "c020_s0", 5), ("c8  d_023/(NdVal+sqrt(Col))+NpUnf", "c020_s0", 8),
         ("c9  unit-consistent", "c027_s0", 9), ("no-descriptor c9 (reference)", "ref_s5", 9)]


def main():
    m = pd.read_csv(ROOT / "ledger/metrics_extra.csv")
    base = pd.read_csv(ROOT / "ledger/baseline_val_preds.csv", index_col=0)
    va = pd.read_csv(ROOT / "data/splits/val.csv")
    y = va.hv_chen.values
    groups = va.formula.map(element_group).values
    idx = pd.Series(np.arange(len(y))).groupby(groups).apply(np.array).tolist()
    rng = np.random.default_rng(0)
    draws = [np.concatenate([idx[i] for i in rng.integers(0, len(idx), len(idx))]) for _ in range(5000)]
    cst, svr = base["train_median"].values, base["svr_magpie_BG"].values
    rows = []
    for label, run, c in CANDS:
        e = m[(m.run_id == run) & (m.complexity == c)]
        assert len(e) == 1, (run, c)
        descs = json.loads((ROOT / f"ledger/runs/{run}.json").read_text())["descriptors"]
        _, p = predict(e.iloc[0].formula, descs)
        ae = lambda q: np.abs(y - q)
        a_f, a_c, a_s = ae(p), ae(cst), ae(svr)
        point = (a_c.mean() - a_f.mean()) / (a_c.mean() - a_s.mean())
        g = np.array([(a_c[t].mean() - a_f[t].mean()) / (a_c[t].mean() - a_s[t].mean()) for t in draws])
        mase = np.array([a_f[t].mean() / a_s[t].mean() for t in draws])
        lo, hi = np.percentile(g, [2.5, 97.5])
        mlo, mhi = np.percentile(mase, [2.5, 97.5])
        rows.append(dict(formula=label, run=run, c=c, mae=a_f.mean(), gap_closed=point, gap_lo=lo, gap_hi=hi,
                         mase_svr=a_f.mean() / a_s.mean(), mase_lo=mlo, mase_hi=mhi))
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "ledger/gap_closed_ci.csv", index=False, float_format="%.4f")
    print(out.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
