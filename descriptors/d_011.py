"""d_011: harmonic-mean covalent radius to the -2.5 power, r_h^-2.5 (1/Angstrom^2.5).

Rationale: companion to d_010. Gao/Simunek-style bond-strength models give Hv ~ d^-2.5 with d
the bond length, and PySR's operator set has no general power, so the exponent form is supplied
directly. r_h is the fraction-weighted harmonic mean covalent radius in Angstrom (d_010).
Units: Angstrom^-2.5. Expected sign: positive.
Uses only df["comp"].
"""
import pandas as pd

from descriptors.d_010 import harmonic_radius


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([harmonic_radius(c) ** -2.5 for c in df["comp"]], index=df.index, name="d_011")
