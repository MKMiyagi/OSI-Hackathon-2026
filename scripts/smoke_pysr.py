"""PySR smoke test. First run downloads Julia + precompiles (10+ min). Small on purpose."""
import numpy as np
import pandas as pd
from matminer.featurizers.composition import ElementProperty
from matminer.featurizers.conversions import StrToComposition
from pysr import PySRRegressor

df = pd.read_csv("data/raw/brgoch_superhard_training.csv")
print("columns:", list(df.columns))

# brgoch_superhard_training uses 'composition' (string) and 'hardness'; fall back if names differ
formula_col = "formula" if "formula" in df.columns else "composition"
target_col = "hardness"

if df[formula_col].dtype == object:
    df = StrToComposition(target_col_id="comp").featurize_dataframe(df, formula_col, ignore_errors=True)
    comp_col = "comp"
else:
    comp_col = formula_col

ep = ElementProperty.from_preset("magpie")
df = ep.featurize_dataframe(df, comp_col, ignore_errors=True)
feats = [c for c in df.columns if c.startswith("MagpieData mean")]
X = df[feats].fillna(0).values
y = df[target_col].values

model = PySRRegressor(
    niterations=20,
    maxsize=15,
    procs=4,
    binary_operators=["+", "-", "*", "/"],
    unary_operators=["sqrt", "log", "exp"],
    progress=False,
    temp_equation_file=True,
)
model.fit(X, y, variable_names=[f.replace("MagpieData mean ", "") for f in feats])
print(model.equations_[["complexity", "loss", "equation"]])
