"""d_020: estimated bonds per atom, B_pa = 0.5 * sum_i x_i b_i (HYPOTHESES_4 H4.2; base variant, no anion cap).

b_i = min(v_i, 8 - v_i) for p-block (octet capacity), v_i for metals (descriptors/_bondcount.py); each bond shared by two atoms.
Rationale: covalent hardness scales with bond density; the fold-over min(v, 8-v) is a per-element nonlinearity applied
before averaging, which fraction-weighted means of valence or unfilled counts cannot reproduce.
Units: bonds per atom (dimensionless). Expected sign: positive. Likely highly correlated with m_NValence.
Uses only df["comp"].
"""
import pandas as pd

from descriptors._bondcount import capacity


def _bpa(comp):
    return 0.5 * sum(comp.get_atomic_fraction(el) * capacity(el) for el in comp.elements)


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_bpa(c) for c in df["comp"]], index=df.index, name="d_020")
