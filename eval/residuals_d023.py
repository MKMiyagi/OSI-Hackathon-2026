"""Step 0 of overnight 5: per-chemical-family residuals of the d_023 c8 and c5 formulas on data/splits/val.csv.

Usage: uv run python eval/residuals_d023.py [--tag before]
Reads val only (never the test file). Families are assigned by fixed rules (first match wins):
  binary_CNB   exactly two elements, one of them B, C or N, the other not B/C/N/O
  oxide        contains O
  pnictide_chalcogenide  contains P, As, Sb, S, Se or Te (no O)
  intermetallic  every element is in descriptors.d_031.METALS
  other        everything else (halides, silicides/germanides, ternary B/C/N compounds without O, ...)
Comparators: train-median constant and the primary Magpie SVR (B, G -> Chen) from ledger/baseline_val_preds.csv.
"""
import argparse
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from descriptors.d_031 import METALS  # noqa: E402
from eval.score import eval_equation  # noqa: E402
from sr.run_pysr import featurize  # noqa: E402

FORMULAS = {
    "c8": "(d_023 / (m_NdValence + sqrt(m_Column))) + m_NpUnfilled",
    "c5": "d_023 / (m_NdValence - -2.4609854)",
}
FAMILIES = ["binary_CNB", "oxide", "pnictide_chalcogenide", "intermetallic", "other"]


def family(comp):
    els = {e.symbol for e in comp.elements}
    if len(els) == 2 and els & {"B", "C", "N"} and not els & {"O"} and len(els & {"B", "C", "N"}) == 1:
        return "binary_CNB"
    if "O" in els:
        return "oxide"
    if els & {"P", "As", "Sb", "S", "Se", "Te"}:
        return "pnictide_chalcogenide"
    if els <= METALS:
        return "intermetallic"
    return "other"


def build(val_descs=("d_023",)):
    val = pd.read_csv(ROOT / "data/splits/val.csv")
    val, X = featurize(val, list(val_descs))
    val["family"] = [family(c) for c in val["comp"]]
    base = pd.read_csv(ROOT / "ledger/baseline_val_preds.csv", index_col=0)
    val["pred_const"] = base["train_median"].values
    val["pred_svr"] = base["svr_magpie_BG"].values
    for k, eq in FORMULAS.items():
        val[f"pred_{k}"] = eval_equation(eq, X)
    return val


def table(val, preds):
    rows = []
    for fam in FAMILIES + ["ALL"]:
        s = val if fam == "ALL" else val[val.family == fam]
        r = dict(family=fam, n=len(s), mean_hv=s.hv_chen.mean())
        for p in preds:
            e = s[f"pred_{p}"] - s.hv_chen
            r[f"mae_{p}"], r[f"bias_{p}"] = e.abs().mean(), e.mean()
        rows.append(r)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "ledger/residuals_d023.csv"))
    args = ap.parse_args()
    val = build()
    preds = ["const", "svr", "c8", "c5"]
    t = table(val, preds)
    t.to_csv(args.out, index=False, float_format="%.4f")
    pd.set_option("display.width", 250)
    print(t.round(2).to_string(index=False))
    for k in ("c8", "c5"):
        val[f"abs_{k}"] = (val[f"pred_{k}"] - val.hv_chen).abs()
        print(f"\n20 worst rows, {k}")
        w = val.sort_values(f"abs_{k}", ascending=False).head(20)
        print(w[["formula", "family", "hv_chen", f"pred_{k}", "pred_svr"]].round(2).to_string(index=False))
    val.drop(columns=["comp"]).to_csv(ROOT / "ledger/residuals_d023_rows.csv", index=False, float_format="%.4f")
