"""d_014: fraction-weighted electronegativity deviation from the most electronegative element.

    d_014 = sum_i x_i (chi_max - chi_i),  chi = Pauling electronegativity, x_i atomic fraction.

Rationale: d_008 (range) only sees the two extremes; this is the composition-averaged distance
of all constituents from the most electronegative one, i.e. the mean polarity "pull" toward the
anion-like element. It is not a function of the composition means alone (chi_max is an extremum).
Large values = most atoms are far from the anion in chi = ionic/metallic character, weaker
directional covalent bonding.
Units: Pauling electronegativity (dimensionless); 0 for elemental solids.
Expected sign: negative. Uses only df["comp"].
"""
import numpy as np
import pandas as pd


def _d(comp):
    d = comp.get_el_amt_dict()
    tot = sum(d.values())
    chi = {el.symbol: el.X for el in comp.elements}
    cmax = max(chi.values())
    return float(sum(d[s] / tot * (cmax - chi[s]) for s in d))


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_d(c) for c in df["comp"]], index=df.index, name="d_014")
