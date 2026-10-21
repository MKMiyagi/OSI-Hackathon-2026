"""d_018: squared Pauling electronegativity range, (chi_max - chi_min)^2  (= d_008^2).

Rationale: tests whether PySR wanted a nonlinearity in d_008 that is expensive to build (a square
costs 3 nodes: d*d). Also the argument of Pauling's ionic-character exponent. Not new information
beyond d_008; any gain is a search-efficiency effect.
Units: Pauling chi^2 (dimensionless). Expected sign: negative. Uses only df["comp"].
"""
import numpy as np
import pandas as pd


def _sq(comp):
    chi = [el.X for el in comp.elements]
    return float((np.max(chi) - np.min(chi)) ** 2)


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_sq(c) for c in df["comp"]], index=df.index, name="d_018")
