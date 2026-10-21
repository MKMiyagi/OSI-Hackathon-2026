"""d_025: atomic size mismatch, delta = sqrt(sum_i x_i (1 - r_i / r_bar)^2), covalent radii, r_bar = sum_i x_i r_i.

Rationale: interstitial carbides, nitrides and borides (a small nonmetal in a metal lattice: TiC, WC, ZrB2) are the
stiff, high-Pugh-ratio compounds; a large radius mismatch marks that motif, which no mean or EN-range descriptor
encodes (Hume-Rothery / high-entropy-alloy delta parameter). Pre-registered in wiki/HYPOTHESES_T1.md (H3).
Units: dimensionless. Expected sign: positive on k = G/B (low confidence: in solid solutions mismatch lowers
stiffness; record either sign).
Uses only df["comp"].
"""
import numpy as np
import pandas as pd
from matminer.utils.data import MagpieData

_MD = MagpieData()


def _delta(comp):
    x = np.array([comp.get_atomic_fraction(el) for el in comp.elements])
    r = np.array([_MD.get_elemental_property(el, "CovalentRadius") for el in comp.elements], dtype=float)
    rbar = float(np.sum(x * r))
    return float(np.sqrt(np.sum(x * (1.0 - r / rbar) ** 2)))


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_delta(c) for c in df["comp"]], index=df.index, name="d_025")
