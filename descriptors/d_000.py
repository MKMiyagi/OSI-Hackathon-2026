"""d_000: template descriptor (Pugh ratio placeholder).

Rationale: Pugh ratio k = G/B correlates with bond directionality and hardness
(Chen 2011, Tian 2012). Expected sign: positive.

NOTE: B and G are the *targets* of this dataset, not inputs. Composition-only
descriptors must not use them; this placeholder therefore returns NaN. Real
descriptors must be computed from df["comp"] (pymatgen Composition) or the
m_* Magpie columns only.
"""
import numpy as np
import pandas as pd


def compute(df: pd.DataFrame) -> pd.Series:
    return pd.Series(np.nan, index=df.index, name="d_000")
