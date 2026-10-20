"""d_003: atomic fraction of light covalent-network formers (B, C, N, O).

Rationale: superhard materials (diamond, c-BN, B4C, BC2N, B6O) are dominated by short, strong,
directional bonds between light second-row elements (Gao 2003; Chen 2011; Tian 2012). The
count fraction is a per-element feature that Magpie composition means cannot express exactly.
Dimensionless (atomic fraction, 0..1). Expected sign: positive.
Uses only df["comp"].
"""
import pandas as pd

LIGHT = {"B", "C", "N", "O"}


def compute(df: pd.DataFrame) -> pd.Series:
    def frac(comp):
        d = comp.get_el_amt_dict()
        return sum(v for k, v in d.items() if k in LIGHT) / sum(d.values())

    return pd.Series([frac(c) for c in df["comp"]], index=df.index, name="d_003")
