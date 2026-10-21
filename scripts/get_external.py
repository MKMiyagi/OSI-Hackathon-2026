"""Fetch the external Zhang et al. 2021 hardness set and its Materials Project moduli into data/raw/external/.

Usage (from the repo root):
    .venv/bin/python scripts/get_external.py [--copy-from PATH] [--refresh-xlsx] [--refresh-mp]

1. hv_comp_load.xlsx: Zhang, Ziyan et al., Adv. Mater. 33, e2005112 (2021), downloaded from
   github.com/ziyan1996/VickersHardnessPrediction (columns composition, hardness [GPa], load [N]).
   That repo has NO license, so the file stays in data/raw/ (gitignored) and is never committed.
   --copy-from copies a local copy instead of downloading. The sha256 is checked against the one
   recorded when the external check was frozen (a mismatch is a warning: the upstream file changed).
2. zhang_mp_elasticity.csv: for each cleaned Zhang composition (eval/external_zhang.py step 1), the
   lowest-energy_above_hull Materials Project entry (non-deprecated) that has elasticity data, i.e.
   a finite K_VRH and G_VRH (elasticity docs: bulk_modulus.vrh, shear_modulus.vrh, GPa). Ties are broken
   by material_id. Formulas with no such entry are kept with empty material_id / moduli. Columns:
   reduced_formula, material_id, energy_above_hull, K_vrh, G_vrh.

This script reads ONLY the composition column of the xlsx; it never touches the hardness labels.
The MP key is read from .env (MP_API_KEY) and is never printed or written anywhere.
"""
import argparse
import hashlib
import os
import shutil
import sys
import urllib.request
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
EXT = ROOT / "data/raw/external"
XLSX = EXT / "hv_comp_load.xlsx"
# CSV copy written once from the xlsx, so eval/external_zhang.py does not need openpyxl (not in uv.lock)
DATA_CSV = EXT / "hv_comp_load.csv"
MP_CSV = EXT / "zhang_mp_elasticity.csv"
URL = "https://raw.githubusercontent.com/ziyan1996/VickersHardnessPrediction/master/hv_comp_load.xlsx"
XLSX_SHA256 = "6905591ad50832cfea26b3d8459dbe2c849221b6875b13769cc8406bbcaaf6be"
MP_COLS = ["reduced_formula", "material_id", "energy_above_hull", "K_vrh", "G_vrh"]


def clean_formula(s):
    """Protocol step 1: strip whitespace, parse with pymatgen, return reduced_formula (None if unparseable)."""
    from pymatgen.core import Composition

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            comp = Composition(str(s).strip())
        if comp.num_atoms <= 0 or any(a < 0 for a in comp.values()):
            return None
        return comp.reduced_formula
    except Exception:
        return None


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def get_xlsx(copy_from=None, refresh=False):
    EXT.mkdir(parents=True, exist_ok=True)
    if XLSX.exists() and not refresh:
        print(f"have {XLSX.relative_to(ROOT)}")
    elif copy_from:
        shutil.copyfile(copy_from, XLSX)
        print(f"copied {copy_from} -> {XLSX.relative_to(ROOT)}")
    else:
        urllib.request.urlretrieve(URL, XLSX)
        print(f"downloaded {URL} -> {XLSX.relative_to(ROOT)}")
    h = sha256(XLSX)
    print(f"sha256 {h} ({'matches frozen copy' if h == XLSX_SHA256 else 'WARNING: differs from the frozen copy'})")
    if not DATA_CSV.exists() or refresh:
        pd.read_excel(XLSX).to_csv(DATA_CSV, index=False)  # needs openpyxl, this one time only
        print(f"wrote {DATA_CSV.relative_to(ROOT)}")
    return XLSX


def zhang_formulas():
    """Sorted unique cleaned reduced formulas (composition column only)."""
    comp = pd.read_csv(DATA_CSV, usecols=["composition"])["composition"]
    red = comp.map(clean_formula)
    return sorted(red.dropna().unique())


def _vrh(mod):
    if mod is None:
        return np.nan
    v = mod.get("vrh") if isinstance(mod, dict) else getattr(mod, "vrh", None)
    return float(v) if v is not None else np.nan


def _integral(f):
    from pymatgen.core import Composition

    return all(abs(a - round(a)) < 1e-8 for a in Composition(f).values())


def _plain(f):
    from pymatgen.core import Composition

    return Composition(f).reduced_composition.alphabetical_formula.replace(" ", "")


def fetch_mp(formulas, chunk=50):
    from dotenv import load_dotenv
    from mp_api.client import MPRester

    load_dotenv(ROOT / ".env")
    key = os.environ.get("MP_API_KEY")
    if not key:
        raise SystemExit("MP_API_KEY not found in .env")

    # MP entries are ordered crystals with integer stoichiometry, so fractional (solid-solution / doped)
    # compositions cannot match and are not queried. Queries use a parenthesis-free formula (pymatgen's
    # reduced_formula can be e.g. Al3(B24C)2); results are mapped back through clean_formula(formula_pretty).
    query = sorted({_plain(f) for f in formulas if _integral(f)})
    print(f"querying MP for {len(query)} integer-stoichiometry compositions "
          f"({len(formulas) - len(query)} fractional ones skipped)")
    summ = []
    with MPRester(api_key=key, mute_progress_bars=True) as mpr:
        for i in range(0, len(query), chunk):
            docs = mpr.materials.summary.search(
                formula=query[i:i + chunk], deprecated=False,
                fields=["material_id", "formula_pretty", "energy_above_hull"])
            summ += [dict(material_id=str(d.material_id), formula_pretty=d.formula_pretty,
                          energy_above_hull=d.energy_above_hull) for d in docs]
        print(f"MP summary: {len(summ)} entries")
        ids = sorted({s["material_id"] for s in summ})
        el = []
        for i in range(0, len(ids), 500):
            docs = mpr.materials.elasticity.search(
                material_ids=ids[i:i + 500], fields=["material_id", "bulk_modulus", "shear_modulus"])
            el += [dict(material_id=str(d.material_id), K_vrh=_vrh(d.bulk_modulus), G_vrh=_vrh(d.shear_modulus))
                   for d in docs]
        print(f"MP elasticity: {len(el)} docs")

    s = pd.DataFrame(summ, columns=["material_id", "formula_pretty", "energy_above_hull"])
    s["reduced_formula"] = s.formula_pretty.map(clean_formula)
    e = pd.DataFrame(el, columns=["material_id", "K_vrh", "G_vrh"]).drop_duplicates("material_id")
    m = s.merge(e, on="material_id", how="inner")
    m = m[np.isfinite(m.K_vrh) & np.isfinite(m.G_vrh) & m.reduced_formula.isin(formulas)]
    m = m.sort_values(["reduced_formula", "energy_above_hull", "material_id"]).drop_duplicates("reduced_formula")
    out = pd.DataFrame({"reduced_formula": formulas}).merge(m, on="reduced_formula", how="left")[MP_COLS]
    n_any = s.reduced_formula.isin(formulas).groupby(s.reduced_formula).any().sum()
    return out, int(n_any)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--copy-from", help="local copy of hv_comp_load.xlsx instead of downloading")
    ap.add_argument("--refresh-xlsx", action="store_true")
    ap.add_argument("--refresh-mp", action="store_true")
    args = ap.parse_args()

    get_xlsx(args.copy_from, args.refresh_xlsx)
    formulas = zhang_formulas()
    print(f"{len(formulas)} cleaned Zhang compositions")
    if MP_CSV.exists() and not args.refresh_mp:
        out = pd.read_csv(MP_CSV)
        print(f"have {MP_CSV.relative_to(ROOT)} (use --refresh-mp to re-query)")
    else:
        out, n_any = fetch_mp(formulas)
        out.to_csv(MP_CSV, index=False)
        print(f"compositions with any MP entry: {n_any}/{len(formulas)}")
        print(f"wrote {MP_CSV.relative_to(ROOT)}")
    ok = out.material_id.notna()
    pos = ok & (out.K_vrh > 0) & (out.G_vrh > 0)
    print(f"compositions with MP elasticity: {ok.sum()}/{len(out)}; with K_vrh > 0 and G_vrh > 0: {pos.sum()}")


if __name__ == "__main__":
    sys.exit(main())
