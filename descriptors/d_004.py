"""d_004: atomic fraction of d-block transition metals (metallicity proxy).

Rationale: partially filled d bands give delocalized metallic bonding that is non-directional
and plastically soft, lowering hardness (Tian 2012 metallic term; Mazhnik & Oganov 2019 treat
metallicity as hardness-reducing). Dimensionless atomic fraction (0..1), including Sc-Zn,
Y-Cd, Hf-Hg; pymatgen is_transition_metal, lanthanoids/actinoids excluded. Expected sign: negative.
Uses only df["comp"].
"""
import pandas as pd


def compute(df: pd.DataFrame) -> pd.Series:
    def frac(comp):
        tot = sum(comp.get_el_amt_dict().values())
        n = sum(comp[el] for el in comp.elements if el.is_transition_metal and not el.is_lanthanoid and not el.is_actinoid)
        return n / tot

    return pd.Series([frac(c) for c in df["comp"]], index=df.index, name="d_004")
