"""d_009: minimum valence-electron count among constituents, weighted by that element's atomic fraction.

Rationale: the electron-poorest constituent (usually a metal: Li, Mg, Ti, W ...) limits how many
electrons are available to fill bonding states and tends to leave metallic/ionic, easily sheared
bonds. Interpretation (the request was ambiguous): d_009 = NValence of the element with the
fewest valence electrons, times its atomic fraction, i.e. valence electrons per atom contributed
by the weakest-bonding species. It is an extremum over elements, which composition means cannot
express. Units: electrons per atom. For a single-element solid it equals NValence.
Expected sign: negative for compounds with an electron-poor metal minority is NOT assumed;
sign is a hypothesis (likely negative at fixed mean valence electrons).
Uses only df["comp"] and Magpie elemental NValence.
"""
import pandas as pd
from matminer.utils.data import MagpieData

_MD = MagpieData()


def _val(comp):
    d = comp.get_el_amt_dict()
    tot = sum(d.values())
    nv = {el: _MD.get_elemental_property(comp.elements[i], "NValence") for i, el in enumerate(d)}
    low = min(nv, key=nv.get)
    return nv[low] * d[low] / tot


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_val(c) for c in df["comp"]], index=df.index, name="d_009")
