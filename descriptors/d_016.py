"""d_016: electronegativity range on the Allen (spectroscopic) scale, max - min.

Rationale: d_008 uses Pauling chi (thermochemical, fitted to bond energies). Allen's scale is the
average valence-electron ionization energy (configuration energy), independent of bond data. If the
d_008 signal is physical it should survive a change of scale; if it is a Pauling-table artefact it
should not. Allen values (Allen 1989 / Mann et al. 2000, Pauling-like units) are a hard-coded
literature table entered from memory for the 63 elements in train/val; they are NOT fitted to
anything and should be spot-checked against the published tables before publication.
Units: Allen electronegativity (dimensionless, ~Pauling-like magnitude). Expected sign: negative.
Uses only df["comp"]. An element missing from the table raises (no silent fallback).
"""
import numpy as np
import pandas as pd

ALLEN = {
    "H": 2.300, "Li": 0.912, "Be": 1.576, "B": 2.051, "C": 2.544, "N": 3.066, "O": 3.610, "F": 4.193,
    "Na": 0.869, "Mg": 1.293, "Al": 1.613, "Si": 1.916, "P": 2.253, "S": 2.589, "Cl": 2.869,
    "K": 0.734, "Ca": 1.034, "Sc": 1.19, "Ti": 1.38, "V": 1.53, "Cr": 1.65, "Mn": 1.75, "Fe": 1.80,
    "Co": 1.84, "Ni": 1.88, "Cu": 1.85, "Zn": 1.588, "Ga": 1.756, "Ge": 1.994, "As": 2.211,
    "Se": 2.424, "Br": 2.685,
    "Rb": 0.706, "Sr": 0.963, "Y": 1.12, "Zr": 1.32, "Nb": 1.41, "Mo": 1.47, "Tc": 1.51, "Ru": 1.54,
    "Rh": 1.56, "Pd": 1.58, "Ag": 1.87, "Cd": 1.521, "In": 1.656, "Sn": 1.824, "Sb": 1.984,
    "Te": 2.158, "I": 2.359,
    "Cs": 0.659, "Ba": 0.881, "Hf": 1.16, "Ta": 1.34, "W": 1.47, "Re": 1.60, "Os": 1.65, "Ir": 1.68,
    "Pt": 1.72, "Au": 1.92, "Hg": 1.765, "Tl": 1.789, "Pb": 1.854, "Bi": 2.01,
}


def _rng(comp):
    chi = [ALLEN[el.symbol] for el in comp.elements]
    return float(np.max(chi) - np.min(chi))


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_rng(c) for c in df["comp"]], index=df.index, name="d_016")
