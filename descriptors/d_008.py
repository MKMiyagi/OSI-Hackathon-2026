"""d_008: Pauling electronegativity range, max(chi) - min(chi) over constituent elements.

Rationale: d_001/d_005 used fraction-weighted deviations, which PySR can partly rebuild from
means. The range is an extremum over elements and cannot be built from composition means. The
largest electronegativity difference in the compound sets the most ionic/polar bond present
(Pauling ionicity; Gao 2003 uses it for the ionicity penalty on covalent hardness). A large
range means ionic/polar bonding and lower Hv for a given bond density.
Units: Pauling electronegativity (dimensionless); 0 for elemental solids.
Expected sign: negative (more ionic -> softer), though not strictly monotonic (e.g. TiN, WC).
Uses only df["comp"].
"""
import numpy as np
import pandas as pd


def _range(comp):
    chi = [el.X for el in comp.elements]
    return float(np.max(chi) - np.min(chi))


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_range(c) for c in df["comp"]], index=df.index, name="d_008")
