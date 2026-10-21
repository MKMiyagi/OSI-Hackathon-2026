"""d_010: fraction-weighted harmonic mean of elemental covalent radii (bond-length proxy), in Angstrom.

Rationale: hardness falls steeply with bond length (Gao 2003: Hv ~ d^-2.5; Simunek & Vackar
2006). The harmonic mean 1/sum(x_i / r_i) is dominated by the smallest atoms (B, C, N), which
set the shortest, strongest bonds, unlike the arithmetic Magpie mean radius. Uses Magpie
CovalentRadius (pm) / 100.
Units: Angstrom. Expected sign: negative (shorter bond -> harder). See d_011 for the d^-2.5 form.
Uses only df["comp"].
"""
import pandas as pd
from matminer.utils.data import MagpieData

_MD = MagpieData()


def harmonic_radius(comp):
    d = comp.get_el_amt_dict()
    tot = sum(d.values())
    inv = sum(
        (d[el] / tot) / _MD.get_elemental_property(comp.elements[i], "CovalentRadius")
        for i, el in enumerate(d)
    )
    return 1.0 / inv / 100.0


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([harmonic_radius(c) for c in df["comp"]], index=df.index, name="d_010")
