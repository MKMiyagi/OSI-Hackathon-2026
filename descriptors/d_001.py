"""d_001: mean absolute electronegativity deviation from the composition mean.

Rationale: covalency proxy. Large spread in Pauling electronegativity means ionic /
polar bonding; small spread between strongly bonded light elements (B, C, N) gives
directional covalent bonds, the hallmark of superhard materials (Gao 2003, Chen 2011,
Tian 2012). Computed as sum_i x_i |chi_i - chi_mean| over atomic fractions x_i.
Units: Pauling electronegativity (dimensionless). Expected sign: positive with hardness
per the task hypothesis (note: pure covalent -> 0, so the relation may be non-monotonic).
Uses only df["comp"].
"""
import numpy as np
import pandas as pd


def _spread(comp):
    els = comp.get_el_amt_dict()
    tot = sum(els.values())
    chi = {e: comp.elements[i].X for i, e in enumerate(els)}
    x = np.array([els[e] / tot for e in els])
    c = np.array([chi[e] for e in els], dtype=float)
    return float(np.sum(x * np.abs(c - np.sum(x * c))))


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_spread(c) for c in df["comp"]], index=df.index, name="d_001")
