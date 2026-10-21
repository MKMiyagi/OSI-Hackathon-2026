"""d_027: relative spread of elemental cohesive energies, (max_i E_coh,i - min_i E_coh,i) / sum_i x_i E_coh,i.

Rationale: shear resistance is limited by the weakest bonds. Mixing a very cohesive element (W, C, B) with a weakly
bound one (alkali, Zn, halogen) leaves soft shear paths even when the average energy density (d_023) is high. Not an
EN-range variant (that family is retired): cohesive energy and Pauling chi are only weakly correlated across the
d-block. Cohesive energies as in d_023 (Kittel, matminer); NaN if an element is missing. Pre-registered in
wiki/HYPOTHESES_T1.md (H5).
Units: dimensionless. Expected sign: negative on k = G/B.
Uses only df["comp"].
"""
import pandas as pd

from descriptors.d_023 import _ECOH, _mean_ecoh


def _spread(comp):
    if any(el.symbol not in _ECOH for el in comp.elements):
        return float("nan")
    e = [_ECOH[el.symbol] for el in comp.elements]
    return (max(e) - min(e)) / _mean_ecoh(comp)


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_spread(c) for c in df["comp"]], index=df.index, name="d_027")
