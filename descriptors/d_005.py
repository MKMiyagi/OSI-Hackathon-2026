"""d_005: Gao-type ionicity penalty exp(-1.191 f_i), f_i = 1 - exp(-0.25 (chi_max - chi_min)^2).

Rationale: Gao et al. 2003 hardness model Hv ~ N_e^(2/3) d^-2.5 exp(-1.191 f_i); ionicity f_i
(Pauling) of the most polar bond pair, estimated from the electronegativity range of the
composition, suppresses hardness. Dimensionless, in (0.3, 1]; 1 for elemental/homo-polar
compositions. Expected sign: positive (more covalent -> harder).
Uses only df["comp"] (Pauling X).
"""
import numpy as np
import pandas as pd


def compute(df: pd.DataFrame) -> pd.Series:
    def pen(comp):
        chi = [el.X for el in comp.elements]
        dchi = max(chi) - min(chi)
        fi = 1.0 - np.exp(-0.25 * dchi**2)
        return float(np.exp(-1.191 * fi))

    return pd.Series([pen(c) for c in df["comp"]], index=df.index, name="d_005")
