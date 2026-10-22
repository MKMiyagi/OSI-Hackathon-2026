"""d_030: elemental Pugh ratio of the composition-weighted moduli, d_028 / d_029 (dimensionless).

Rationale: Pugh's criterion, G/B > ~0.57 brittle/hard-bonded, < ~0.57 ductile (Pugh 1954); Chen's k = G/B (Chen 2011) is the
same ratio. Ratio of two weighted means (not weighted mean of ratios), so it is not a linear function of x.
Units: dimensionless. Expected sign: positive on Hv.
Coverage: needs BOTH moduli, so it is NaN whenever either d_028 or d_029 is NaN (the union of their missing elements).
Fallback = NaN, row dropped; never imputed.
Uses only df["comp"].
"""
import pandas as pd

from descriptors._elastic import weighted_mean


def compute(df: pd.DataFrame) -> pd.Series:
    out = [weighted_mean(c, "rigidity_modulus") / weighted_mean(c, "bulk_modulus") for c in df["comp"]]
    return pd.Series(out, index=df.index, name="d_030")
