"""PySR runner: Magpie mean features + requested descriptors -> Pareto front CSV.

Usage:
    uv run python sr/run_pysr.py --descriptors d_001 d_002 --run-id r001

Reads data/splits/train.csv only. Writes ledger/runs/<run-id>.csv with columns
complexity, loss, equation.
"""
import argparse
import importlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# Unphysical for a hardness law (reviewer recommendation, overnight 1)
DEFAULT_EXCLUDE = "m_MeltingT,m_SpaceGroupNumber"


def magpie_means(df, formula_col):
    from matminer.featurizers.composition import ElementProperty
    from matminer.featurizers.conversions import StrToComposition

    stc = StrToComposition(target_col_id="comp")
    stc.set_n_jobs(1)
    df = stc.featurize_dataframe(df, formula_col, ignore_errors=True)
    ep = ElementProperty.from_preset("magpie")
    ep.set_n_jobs(1)
    df = ep.featurize_dataframe(df, "comp", ignore_errors=True)
    feats = [c for c in df.columns if c.startswith("MagpieData mean")]
    # m_ prefix keeps names sympy-safe (e.g. "Number")
    out = pd.DataFrame(
        {"m_" + c.replace("MagpieData mean ", "").replace(" ", "_"): df[c] for c in feats}
    )
    return df, out


def add_descriptors(df, X, descriptors):
    """Append descriptors/<name>.compute() columns to X. Shared with eval/score.py."""
    # descriptors see only composition + Magpie means, never target/modulus columns
    view = X.copy()
    view["comp"] = df["comp"].values
    view.index = df.index
    X = X.copy()
    X.index = df.index
    for name in descriptors:
        mod = importlib.import_module(f"descriptors.{name}")
        d = pd.Series(mod.compute(view))
        if not d.index.equals(df.index):
            raise ValueError(f"{name}: returned index does not match input rows")
        X[name] = pd.to_numeric(d, errors="coerce").astype(float)
    return X


def featurize(df, descriptors, formula_col="formula"):
    """Full feature pipeline: formula -> Magpie means (+ descriptors). Returns (df, X)."""
    df, X = magpie_means(df, formula_col)
    return df, add_descriptors(df, X, descriptors)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--descriptors", nargs="*", default=[], help="module names in descriptors/, e.g. d_001")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--niterations", type=int, default=22000)
    ap.add_argument("--maxsize", type=int, default=15)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=900, help="timeout_in_seconds per fit")
    ap.add_argument(
        "--exclude-features",
        default=DEFAULT_EXCLUDE,
        help="comma list of feature columns hidden from PySR (still computed, so score.py is unaffected); '' for none",
    )
    ap.add_argument("--target", default="hv_chen", help="target column in train.csv")
    ap.add_argument("--formula-col", default="formula")
    args = ap.parse_args()

    from pysr import PySRRegressor

    df = pd.read_csv(ROOT / "data/splits/train.csv")
    df, X = featurize(df, args.descriptors, args.formula_col)

    exclude = [c.strip() for c in args.exclude_features.split(",") if c.strip()]
    unknown = [c for c in exclude if c not in X.columns]
    if unknown:
        raise SystemExit(f"--exclude-features names not in feature set: {unknown}")
    X = X.drop(columns=exclude)

    y = df[args.target].astype(float).values
    Xv = X.astype(float).values
    keep = np.isfinite(y) & np.isfinite(Xv).all(axis=1)
    print(f"rows kept: {keep.sum()}/{len(keep)}; features: {X.shape[1]}")
    if keep.sum() == 0:
        raise SystemExit("no finite training rows remain (placeholder descriptor d_000 returns NaN?)")

    model = PySRRegressor(
        niterations=args.niterations,
        maxsize=args.maxsize,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["sqrt", "log", "exp"],
        nested_constraints={op: {"sqrt": 0, "log": 0, "exp": 0} for op in ("sqrt", "log", "exp")},
        procs=args.procs,
        timeout_in_seconds=args.timeout,
        random_state=args.seed,
        deterministic=False,
        progress=False,
        temp_equation_file=True,
    )
    t0 = time.time()
    model.fit(Xv[keep], y[keep], variable_names=list(X.columns))
    wall = time.time() - t0
    print(f"fit wall-clock: {wall:.1f}s")

    out = ROOT / "ledger/runs"
    out.mkdir(parents=True, exist_ok=True)
    model.equations_[["complexity", "loss", "equation"]].to_csv(out / f"{args.run_id}.csv", index=False)
    (out / f"{args.run_id}.json").write_text(
        json.dumps(
            {
                "descriptors": args.descriptors,
                "target": args.target,
                "formula_col": args.formula_col,
                "seed": args.seed,
                "exclude_features": exclude,
                "niterations": args.niterations,
                "maxsize": args.maxsize,
                "timeout_in_seconds": args.timeout,
                "fit_seconds": round(wall, 1),
            }
        )
    )
    print(f"wrote {out / (args.run_id + '.csv')}")


if __name__ == "__main__":
    main()
