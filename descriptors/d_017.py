"""d_017: electronegativity-weighted content of anion-like constituents, sum_{chi_i > 2.5} x_i chi_i.

Equals (mean Pauling chi of the anion-like elements, those with chi > 2.5: C, N, O, S, Cl, Br, ...)
times (their total atomic fraction). Rationale: hard covalent/ionic ceramics are carbides, nitrides,
oxides; the anion-like fraction sets how much of the structure is a strongly bonded
non-metal sublattice, and chi weights its electron-withdrawing strength. Threshold 2.5 is a fixed
a-priori cut (not tuned). Units: Pauling electronegativity (dimensionless); 0 if no anion-like
element (metals, intermetallics). Expected sign: positive. Uses only df["comp"].
"""
import pandas as pd

THRESH = 2.5


def _a(comp):
    d = comp.get_el_amt_dict()
    tot = sum(d.values())
    chi = {el.symbol: el.X for el in comp.elements}
    return float(sum(d[s] / tot * chi[s] for s in d if chi[s] > THRESH))


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_a(c) for c in df["comp"]], index=df.index, name="d_017")
