"""Check that the frozen splits are unchanged and group-disjoint. Safe for agents to run.

Usage: uv run python scripts/verify_splits.py              # train/val only
       uv run python scripts/verify_splits.py --test PATH  # T1 only: also hash-check the quarantined test file

Checks: sha256 of data/splits/train.csv and val.csv against data/splits/SHA256SUMS; no shared element-set
group or reduced formula between train and val. The test file is never opened unless --test is given, and
even then only its bytes are hashed against data/test.sha256 (contents are not parsed or printed).
Exit code 1 on any failure.
"""
import argparse
import hashlib
import sys
from pathlib import Path

import pandas as pd
from pymatgen.core import Composition

ROOT = Path(__file__).resolve().parent.parent


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", help="path to the quarantined test.csv (T1 only)")
    args = ap.parse_args()

    ok = True
    for line in (ROOT / "data/splits/SHA256SUMS").read_text().split("\n"):
        if not line.strip():
            continue
        digest, name = line.split()
        match = sha256(ROOT / "data/splits" / name) == digest
        ok &= match
        print(f"{name}: {'OK' if match else 'CHANGED'}")

    tr = pd.read_csv(ROOT / "data/splits/train.csv")
    va = pd.read_csv(ROOT / "data/splits/val.csv")
    group = lambda f: "-".join(sorted(el.symbol for el in Composition(f).elements))
    reduced = lambda f: Composition(f).reduced_formula
    for label, key in (("element-set groups", group), ("reduced formulas", reduced)):
        shared = set(tr.formula.map(key)) & set(va.formula.map(key))
        ok &= not shared
        print(f"train/val shared {label}: {len(shared)}")

    # eval/chen.py must reproduce the frozen labels (it is the side-effect-free copy of make_splits.chen_hardness)
    sys.path.insert(0, str(ROOT))
    from eval.chen import chen_hardness
    dev = max(float(abs(chen_hardness(d.shear_modulus, d.bulk_modulus) - d.hv_chen).max()) for d in (tr, va))
    ok &= dev < 1e-9
    print(f"eval/chen.py reproduces hv_chen: max |diff| {dev:.1e}")

    if args.test:
        match = sha256(args.test) == (ROOT / "data/test.sha256").read_text().strip()
        ok &= match
        print(f"test file hash: {'OK' if match else 'MISMATCH'}")

    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
