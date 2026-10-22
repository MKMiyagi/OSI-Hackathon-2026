"""d_028: composition-weighted elemental shear (rigidity) modulus, sum_i x_i G_i, pymatgen Element.rigidity_modulus (GPa).

Rationale: Chen's Hv = 2 (k^2 G)^0.585 - 3 needs G and k = G/B; nothing in the composition features proxies shear
resistance. G_i is the elemental-solid rigidity modulus (WebElements/CRC). Averaging elemental moduli is a rule-of-mixtures
estimate, blind to bonding changes on compound formation (a compound of two soft elements can be hard, e.g. borides, nitrides).
Units: GPa (UNITS = "Pa"). Expected sign: positive on Hv (G is a direct factor of Chen's form).
Coverage (see wiki/RESIDUALS_D023.md): pymatgen has NO rigidity modulus for B, C, N, O, F, Si, P, S, Cl, As, Ge, Ga, In,
Br, I, Cs, Rb, Hg, Mn, Tc (and others); published handbooks (CRC, Kaye & Laby) have no value for these elements either, so
no cited fallback exists. Fallback = NaN for the whole composition, row dropped (descriptors/_elastic.py). Consequence:
only 41% of train and 37% of val rows are finite (d_030: 37% / 32%), and none of the covalent B/C/N/Si compounds the hypothesis cares most about.
Uses only df["comp"].
"""
import pandas as pd

from descriptors._elastic import weighted_mean

UNITS = "Pa"


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series([weighted_mean(c, "rigidity_modulus") for c in df["comp"]], index=df.index, name="d_028")
