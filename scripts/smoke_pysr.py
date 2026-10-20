"""PySR smoke test. First run downloads Julia + precompiles (10+ min). Small on purpose.

NOTE: brgoch_superhard_training has bulk_modulus and shear_modulus (GPa) but NO
measured hardness. Tehrani 2018 gets hardness by feeding predicted B, G into
Chen 2011: Hv = 2 (k^2 G)^0.585 - 3, k = G/B. We add that column as 'hv_chen'
and fit shear_modulus here just to prove the pipeline runs.
"""
import numpy as np
import pandas as pd
from matminer.featurizers.composition import ElementProperty
from matminer.featurizers.conversions import StrToComposition
from pysr import PySRRegressor


def chen_hardness(G, B):
    k = G / B
    return 2.0 * (k**2 * G) ** 0.585 - 3.0


def main():
    df = pd.read_csv("data/raw/brgoch_superhard_training.csv")
    print("columns:", list(df.columns))
    df = df[["formula", "bulk_modulus", "shear_modulus"]].dropna()
    df = df[(df.bulk_modulus > 0) & (df.shear_modulus > 0)].reset_index(drop=True)
    df["hv_chen"] = chen_hardness(df.shear_modulus, df.bulk_modulus)
    print(df[["bulk_modulus", "shear_modulus", "hv_chen"]].describe().round(1))

    # n_jobs=1 avoids macOS multiprocessing spawn issues
    stc = StrToComposition(target_col_id="comp")
    stc.set_n_jobs(1)
    df = stc.featurize_dataframe(df, "formula", ignore_errors=True)

    ep = ElementProperty.from_preset("magpie")
    ep.set_n_jobs(1)
    df = ep.featurize_dataframe(df, "comp", ignore_errors=True)

    feats = [c for c in df.columns if c.startswith("MagpieData mean")]
    X = df[feats].fillna(0).values
    y = df["shear_modulus"].values
    # prefix so names like "Number" don't collide with sympy functions
    names = ["m_" + f.replace("MagpieData mean ", "") for f in feats]

    model = PySRRegressor(
        niterations=20,
        maxsize=15,
        procs=4,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["sqrt", "log", "exp"],
        progress=False,
        temp_equation_file=True,
    )
    model.fit(X, y, variable_names=names)
    print(model.equations_[["complexity", "loss", "equation"]])


if __name__ == "__main__":
    main()
