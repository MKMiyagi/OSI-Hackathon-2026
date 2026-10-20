"""Grouped 70/15/15 split (seed 42) of the Brgoch B,G data with hv_chen target.

Group key = sorted set of elements, so e.g. all Ti-O compositions land in one split
(held-out *chemical families*). train/val go to data/splits/; test goes OUTSIDE the
repo to ~/quarantine/test.csv, with its sha256 recorded in data/test.sha256.
"""
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from pymatgen.core import Composition

ROOT = Path(__file__).resolve().parent.parent
SEED = 42
FRACS = (0.70, 0.15, 0.15)


def chen_hardness(G, B):
    k = G / B
    return 2.0 * (k**2 * G) ** 0.585 - 3.0


def main():
    df = pd.read_csv(ROOT / "data/raw/brgoch_superhard_training.csv")
    n0 = len(df)
    df = df[~df["suspect_value"].astype(bool)]
    df = df[["formula", "bulk_modulus", "shear_modulus"]].dropna()
    df = df[(df.bulk_modulus > 0) & (df.shear_modulus > 0)].reset_index(drop=True)
    print(f"rows: {n0} raw -> {len(df)} after filtering")
    df["hv_chen"] = chen_hardness(df.shear_modulus, df.bulk_modulus)

    df["group"] = [
        "-".join(sorted(el.symbol for el in Composition(f).elements)) for f in df.formula
    ]
    groups = df["group"].unique()
    rng = np.random.default_rng(SEED)
    rng.shuffle(groups)
    sizes = df["group"].value_counts()

    # fill train, then val, then test by cumulative row count over shuffled groups
    targets = np.cumsum(FRACS) * len(df)
    assign, cum, k = {}, 0, 0
    for g in groups:
        if cum >= targets[k] and k < 2:
            k += 1
        assign[g] = k
        cum += sizes[g]
    df["split"] = df["group"].map(assign)

    cols = ["formula", "bulk_modulus", "shear_modulus", "hv_chen"]
    out = ROOT / "data/splits"
    out.mkdir(parents=True, exist_ok=True)
    df[df.split == 0][cols].to_csv(out / "train.csv", index=False)
    df[df.split == 1][cols].to_csv(out / "val.csv", index=False)

    q = Path.home() / "quarantine"
    q.mkdir(exist_ok=True)
    test_path = q / "test.csv"
    df[df.split == 2][cols].to_csv(test_path, index=False)
    (ROOT / "data/test.sha256").write_text(hashlib.sha256(test_path.read_bytes()).hexdigest() + "\n")

    for name, i in (("train", 0), ("val", 1), ("test", 2)):
        s = df[df.split == i]
        print(f"{name}: {len(s)} rows, {s.group.nunique()} element-set groups")
    sets = [set(df[df.split == i].group) for i in range(3)]
    assert not (sets[0] & sets[1] or sets[0] & sets[2] or sets[1] & sets[2]), "group leakage"


if __name__ == "__main__":
    main()
