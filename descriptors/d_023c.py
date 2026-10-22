"""d_023c: d_023 restricted to the rows where d_030 (hence d_028 and d_029) is finite; NaN elsewhere.

Supplement only (covered-subset comparison of d_023 vs d_023 + d_030 / d_028, wiki/RESIDUALS_D023.md): run_pysr.py drops
non-finite rows, so offering d_023c instead of d_023 trains the d_023-only arm on exactly the rows the d_030 / d_028 arms
train on. Identical to d_023 where finite (same units: GPa, UNITS = "Pa"; same sign). Composition-only.
"""
import numpy as np
import pandas as pd

from descriptors import d_023, d_030

UNITS = "Pa"


def compute(df: pd.DataFrame) -> pd.Series:
    d = d_023.compute(df)
    return d.where(np.isfinite(d_030.compute(df))).rename("d_023c")
