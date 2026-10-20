"""d_006: valence-electron density times Gao ionicity penalty, per-element bond-density form.

Rationale: Gao 2003 / Simunek 2006: Hv ~ n_e^(2/3) exp(-1.191 f_i) with n_e the valence-electron
density. Here n_e = m_NValence / m_GSvolume_pa [e/A^3] and f_i = 1 - exp(-0.25 (chi_max-chi_min)^2).
Output = n_e^(2/3) * exp(-1.191 f_i), units (e/A^3)^(2/3) -- a single combined product that PySR
failed to assemble from d_002 and d_005 separately. Expected sign: positive.
Uses df["comp"] (Pauling X) and m_* Magpie means.
"""
import numpy as np
import pandas as pd


def compute(df: pd.DataFrame) -> pd.Series:
    ne = df["m_NValence"] / df["m_GSvolume_pa"]
    pen = []
    for comp in df["comp"]:
        chi = [el.X for el in comp.elements]
        fi = 1.0 - np.exp(-0.25 * (max(chi) - min(chi)) ** 2)
        pen.append(np.exp(-1.191 * fi))
    return pd.Series(ne.values ** (2.0 / 3.0) * np.array(pen), index=df.index, name="d_006")
