"""d_015: Pauling ionic character of the most polar pair, 1 - exp(-(chi_max - chi_min)^2 / 4).

Rationale: Pauling's bond ionicity (fractional ionic character) evaluated on the composition's
largest electronegativity difference. A bounded, saturating transform of d_008, so PySR gets the
nonlinearity ready-made. 0 = purely covalent/metallic, -> 1 = fully ionic.
Units: dimensionless in [0, 1). Expected sign: negative (ionic bonds are softer, less directional).
Uses only df["comp"].
"""
import numpy as np
import pandas as pd


def _ic(comp):
    chi = [el.X for el in comp.elements]
    return float(1.0 - np.exp(-((max(chi) - min(chi)) ** 2) / 4.0))


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([_ic(c) for c in df["comp"]], index=df.index, name="d_015")
