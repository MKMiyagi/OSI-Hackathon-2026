"""d_023: cohesive-energy density, 160.2 * sum_i x_i E_coh,i / m_GSvolume_pa, in GPa.

Rationale: an elastic modulus is a curvature of energy per volume, so B ~ E_coh / V (universal
binding-energy relation, Rose, Smith, Guinea & Ferrante 1984). E_coh,i is the elemental
cohesive energy (Kittel; matminer utils/data_files/cohesive_energies.json, which covers every
element in the dataset), averaged with atomic fractions x_i. V is the Magpie fraction-weighted
ground-state volume per atom (A^3), so 1 eV/A^3 = 160.2 GPa. This is the only descriptor with the
target's dimension (it matters under --dimensionless-constants; plain --units lets constants carry units).
The table covers every element in the full matminer dataset; a composition with an element missing from it
(H, He, Pm, At, Fr, Pa) gets NaN rather than an exception.
Units: GPa (UNITS = "Pa" for PySR --units; only the dimension matters).
Expected sign: positive on B and G, power ~1 (train-only fit B = 3.26 d_023^0.994).
Uses df["comp"] and df["m_GSvolume_pa"].
"""
import json
from pathlib import Path

import matminer
import pandas as pd

UNITS = "Pa"
EV_PER_A3_IN_GPA = 160.2177
_ECOH = json.loads((Path(matminer.__file__).parent / "utils/data_files/cohesive_energies.json").read_text())


def _mean_ecoh(comp):
    if any(el.symbol not in _ECOH for el in comp.elements):
        return float("nan")
    return sum(comp.get_atomic_fraction(el) * _ECOH[el.symbol] for el in comp.elements)


def compute(df: pd.DataFrame) -> pd.Series:
    ecoh = pd.Series([_mean_ecoh(c) for c in df["comp"]], index=df.index)
    return (EV_PER_A3_IN_GPA * ecoh / df["m_GSvolume_pa"]).rename("d_023")
