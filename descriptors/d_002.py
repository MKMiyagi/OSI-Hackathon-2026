"""d_002: valence electron density, mean valence electrons per mean ground-state atomic volume.

Rationale: hardness scales with the density of bonding electrons (Gao 2003: Hv ~ N_e^(2/3);
Simunek & Vackar 2006 bond-strength models). Mean NValence [electrons/atom] divided by mean
GSvolume_pa [A^3/atom] gives electrons per A^3. Units: e/A^3. Expected sign: positive.
Uses only m_* Magpie means.
"""
import pandas as pd


def compute(df: pd.DataFrame) -> pd.Series:
    return (df["m_NValence"] / df["m_GSvolume_pa"]).rename("d_002")
