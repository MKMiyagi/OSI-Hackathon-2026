"""d_007: atomic fraction of B, C, N (O excluded).

Rationale: d_003 (B, C, N, O) was the best overnight-1 cycle but reviewers noted that O mostly
forms ionic/molecular oxides, which weakens the covalent-network argument. This is the control:
if d_003's signal was real it should survive (or sharpen) with O removed; if it collapses, the
d_003 gain came from O or from search noise. Superhard B/C/N phases (diamond, c-BN, B4C, BC2N)
have short directional bonds (Gao 2003; Chen 2011; Tian 2012).
Dimensionless atomic fraction in [0, 1]. Expected sign: positive.
Uses only df["comp"].
"""
import pandas as pd

LIGHT = {"B", "C", "N"}


def compute(df: pd.DataFrame) -> pd.Series:
    def frac(comp):
        d = comp.get_el_amt_dict()
        return sum(v for k, v in d.items() if k in LIGHT) / sum(d.values())

    return pd.Series([frac(c) for c in df["comp"]], index=df.index, name="d_007")
