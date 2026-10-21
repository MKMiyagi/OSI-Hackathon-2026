"""d_012: composition-only Pugh-ratio proxy k = G/B from Mendeleev-number spread.

Rationale: Chen (2011) Hv = 2 (k^2 G)^0.585 - 3 with k = G/B. G and B need DFT, but k is a
shape factor that is high (brittle, directional covalent bonding) for chemically similar atoms
and low (ductile, metallic/ionic) for chemically dissimilar ones. The Mendeleev number places
elements along a chemical-similarity axis, so its fraction-weighted mean absolute deviation
is a composition-only stand-in for that dissimilarity. Here
    k_proxy = 1 / (1 + 10 * MAD(MendeleevNumber) / 103)
(103 = max Mendeleev number; factor 10 is a fixed scale, not fitted to the target), mapping the
spread onto k in (0, 1], with k = 1 for an elemental solid (an upper-bound proxy; real k <~ 1.2).
PySR can then build a Chen-like form, e.g. k^1.17 * f(other features).
Dimensionless. Expected sign: positive.
Uses only df["comp"] and Magpie elemental MendeleevNumber.
"""
import numpy as np
import pandas as pd
from matminer.utils.data import MagpieData

_MD = MagpieData()


def _k(comp):
    d = comp.get_el_amt_dict()
    tot = sum(d.values())
    x = np.array([v / tot for v in d.values()])
    m = np.array([_MD.get_elemental_property(comp.elements[i], "MendeleevNumber") for i in range(len(d))])
    mad = float(np.sum(x * np.abs(m - np.sum(x * m))))
    return 1.0 / (1.0 + 10.0 * mad / 103.0)


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_k(c) for c in df["comp"]], index=df.index, name="d_012")
