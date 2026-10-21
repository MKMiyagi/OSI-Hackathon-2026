"""d_013: valence electron density with an oxygen-corrected volume (e/Angstrom^3).

Rationale: d_002 divided mean NValence by the mean Magpie GSvolume_pa. Magpie's ground-state
volume for O comes from the molecular O2 solid, which does not represent O in a condensed oxide
lattice where O sits as a space-filling anion. Here the O volume is replaced by the sphere
volume of the Shannon O2- radius, 4/3 pi (1.40 A)^3 = 11.49 A^3 (a fixed literature constant, not
fitted); other elements keep Magpie GSvolume_pa. Then
    d_013 = <NValence> / <V>, with <V> = sum_i x_i V_i  (V_O corrected).
Units: e/A^3. Expected sign: positive (Gao 2003 Hv ~ N_e^(2/3)). Low-confidence correction;
it only moves rows containing O. Uses only df["comp"] and Magpie elemental NValence, GSvolume_pa.
"""
import numpy as np
import pandas as pd
from matminer.utils.data import MagpieData

_MD = MagpieData()
V_O = 4.0 / 3.0 * np.pi * 1.40**3


def _ved(comp):
    d = comp.get_el_amt_dict()
    tot = sum(d.values())
    nv = vol = 0.0
    for i, el in enumerate(d):
        x = d[el] / tot
        e = comp.elements[i]
        nv += x * _MD.get_elemental_property(e, "NValence")
        vol += x * (V_O if el == "O" else _MD.get_elemental_property(e, "GSvolume_pa"))
    return nv / vol


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_ved(c) for c in df["comp"]], index=df.index, name="d_013")
