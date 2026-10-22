"""Overnight-5 before/after per-family table (val only). Before = d_023 c8 (cycles 020-023, 3.6939); after = tonight's
best new-descriptor formulas. Writes ledger/residuals_overnight5.csv and prints a markdown table."""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import eval.residuals_d023 as R  # noqa: E402
from eval.score import eval_equation  # noqa: E402
from sr.run_pysr import featurize  # noqa: E402

FORMULAS = {
    "c8_before": "(d_023 / (m_NdValence + sqrt(m_Column))) + m_NpUnfilled",
    "c12_d031": "(d_023 / (sqrt(m_Column) + m_NdValence)) + ((m_NsValence - d_031) * m_NpUnfilled)",
    "c15_d031": "((d_023 / (m_NdValence + sqrt(m_Column))) + ((m_NUnfilled / exp(d_031)) * m_NpUnfilled)) * 0.83485895",
    "c14_nonew": "(d_023 / (m_NdValence + (m_Electronegativity - (m_NUnfilled * -0.26943633)))) + (sqrt(m_NdUnfilled) * m_NpUnfilled)",
}
if __name__ == "__main__":
    val = pd.read_csv(ROOT / "data/splits/val.csv")
    val, X = featurize(val, ["d_023", "d_031"])
    val["family"] = [R.family(c) for c in val["comp"]]
    base = pd.read_csv(ROOT / "ledger/baseline_val_preds.csv", index_col=0)
    val["pred_svr"] = base["svr_magpie_BG"].values
    for k, eq in FORMULAS.items():
        val[f"pred_{k}"] = eval_equation(eq, X)
    t = R.table(val, ["svr"] + list(FORMULAS))
    t.to_csv(ROOT / "ledger/residuals_overnight5.csv", index=False, float_format="%.4f")
    cols = ["family", "n", "mae_svr"] + [f"{p}_{k}" for k in FORMULAS for p in ("mae", "bias")]
    print(t[cols].round(2).to_string(index=False))
