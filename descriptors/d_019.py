"""d_019: anion/cation atomic-fraction ratio R_ac = sum_anions x_i / sum_cations x_i (HYPOTHESES_4 H4.1).

Anion = Pauling chi >= 2.0 (declared convention, descriptors/_bondcount.py); 0 when no anion, 10 when no cation.
Rationale: stoichiometry sets whether the nonmetal sublattice percolates into covalent networks (BN, B4C: high R_ac,
hard) or sits as isolated interstitials in a metallic matrix (Ti2N, Mo2C: low R_ac). A ratio of group sums, not a Magpie mean.
Units: dimensionless. Expected sign: positive on Chen-proxy hardness, saturating, non-monotonic above ~1.5.
Uses only df["comp"].
"""
import pandas as pd

from descriptors._bondcount import is_anion


def _rac(comp):
    a = sum(comp.get_atomic_fraction(el) for el in comp.elements if is_anion(el))
    c = sum(comp.get_atomic_fraction(el) for el in comp.elements if not is_anion(el))
    if a == 0:
        return 0.0
    if c == 0:
        return 10.0
    return a / c


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_rac(c) for c in df["comp"]], index=df.index, name="d_019")
