"""d_029: composition-weighted elemental bulk modulus, sum_i x_i B_i, pymatgen Element.bulk_modulus (GPa).

Rationale: same rule-of-mixtures proxy as d_028 for the bulk half of Chen's inputs (k = G/B). Expected to be partly redundant
with d_023 (cohesive-energy density, B ~ E_coh/V). pymatgen/CRC note: the carbon value (33 GPa) is graphite-like, not diamond.
Units: GPa (UNITS = "Pa"). Expected sign: positive on Hv.
Coverage: no bulk modulus for N, O, F, Ga, Ge, In, Tc, Os, Sr, Zr (pymatgen); handbooks add values for only a few of them.
Fallback = NaN for the whole composition, row dropped (descriptors/_elastic.py); never imputed.
Uses only df["comp"].
"""
import pandas as pd

from descriptors._elastic import weighted_mean

UNITS = "Pa"


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([weighted_mean(c, "bulk_modulus") for c in df["comp"]], index=df.index, name="d_029")
