"""d_026: squared distance from the carbonitride valence-electron optimum, (m_NValence - 4.2)^2.

Rationale: Jhi, Ihm, Louie & Cohen 1999 (Nature 399, 132): C44 and hardness of transition-metal carbonitrides peak at
a valence-electron count of ~8.4 per MX formula unit (4.2 per atom), where the sigma-bonding p-d states are filled
and the shear-unstable d-t2g states are empty. SR could build this from m_NValence (5 nodes); supplying it tests
whether a known optimum is too expensive to discover at maxsize 15. Pre-registered in wiki/HYPOTHESES_T1.md (H4).
Units: (electrons/atom)^2, treated as dimensionless. Expected sign: negative on G and k.
Uses df["m_NValence"].
"""
import pandas as pd


def compute(df: pd.DataFrame) -> pd.Series:
    return ((df["m_NValence"] - 4.2) ** 2).rename("d_026")
