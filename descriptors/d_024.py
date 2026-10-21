"""d_024: Cohen covalent bulk-modulus estimate, (1971 - 220 lam) * d^-3.5, in GPa.

Rationale: Cohen 1985 (PRB 32, 7988) predicts B of tetrahedral covalent solids within ~10% from the bond length d (A)
and an ionicity index lam (0 for IV-IV, 1 for III-V, 2 for II-VI). Composition-only proxy: d = 2 * the
fraction-weighted harmonic-mean covalent radius (d_010), lam = (max group - min group) / 2 over the constituents
(pymatgen Element.group, 1-18), clipped to [0, 2]. Pre-registered in wiki/HYPOTHESES_T1.md (H2); meant for B, and
expected to matter only for covalent (B, C, N, Si) compounds, as a negative control against d_023.
Units: GPa (UNITS = "Pa"). Expected sign: positive.
Uses only df["comp"].
"""
import numpy as np
import pandas as pd

from descriptors.d_010 import harmonic_radius

UNITS = "Pa"


def _cohen(comp):
    groups = [el.group for el in comp.elements]
    lam = float(np.clip((max(groups) - min(groups)) / 2.0, 0.0, 2.0))
    return (1971.0 - 220.0 * lam) * (2.0 * harmonic_radius(comp)) ** -3.5


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_cohen(c) for c in df["comp"]], index=df.index, name="d_024")
