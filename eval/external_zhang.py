"""External one-shot check: composition-only hardness predictors vs MEASURED Vickers hardness (Zhang et al. 2021).

FROZEN PROTOCOL. Written 2026-10-21, before any prediction was compared with these labels. Do not edit it after a
--score run; a different protocol is a different (new) check.

Data: Zhang, Z. et al., Adv. Mater. 33, e2005112 (2021): hv_comp_load.xlsx (composition, hardness [GPa], load [N];
1062 rows) from github.com/ziyan1996/VickersHardnessPrediction. That repo has no license, so the file lives only in
data/raw/external/ (gitignored) and is never committed. Fetch it with scripts/get_external.py, which also builds the
Materials Project moduli cache data/raw/external/zhang_mp_elasticity.csv.

 1. Cleaning: strip whitespace in composition, parse with pymatgen Composition, key = reduced_formula
    (scripts/get_external.py:clean_formula). Unparseable rows are dropped; the count is printed.
 2. Labels, per composition (a composition with no rows in a window has no value for that label; loads are compared
    with a 1e-6 N tolerance):
      hv_lowload   HEADLINE   median measured Hv over rows with 0.49 <= load <= 1.96 N (the three most common loads,
                              0.49 / 0.98 / 1.96 N, and anything in between)
      hv_highload  secondary  median measured Hv over rows with load >= 4.9 N (closer to the load-independent plateau)
 3. Subsets: all = every cleaned composition; novel = compositions whose sorted element set (the make_splits.py group
    key) appears in neither data/splits/train.csv nor data/splits/val.csv.
 4. Predictors, each a function of composition only (the comparator also uses DFT moduli):
      chen_dft    chen_hardness(G_vrh, K_vrh) from scripts/make_splits.py on Materials Project moduli: the lowest-
                  energy_above_hull non-deprecated MP entry with that reduced formula that has elasticity data
                  (fractional stoichiometries cannot match). Defined only where K_vrh > 0 and G_vrh > 0. Not clipped,
                  exactly like the hv_chen training target.
      --formula NAME=EXPR           Hv = EXPR.
      --compose NAME=B_EXPR|K_EXPR  Hv = chen_hardness(k*B, B), B = max(B_EXPR, 1 GPa), k = clip(K_EXPR, 1e-3, k_max),
                  k_max = max G/B over data/splits/train.csv (1.377): the guards of eval/compose_hv.py.
      --svr       svr_magpie: the Magpie (132-feature) SVR of eval/tehrani_baseline.py fitted on train straight on hv_chen
                  (its "direct" route), hyperparameters by its grouped 5-fold CV on train over its full grid (its
                  magpie_all / tuned_svr / element_group are imported, not copied).
    Expressions use the ledger's variable names (m_* Magpie means, d_### descriptors); features come from
    sr/run_pysr.py:featurize and expressions are evaluated with eval/score.py:eval_equation. A predictor is undefined
    for a composition where a feature it uses cannot be computed or its prediction is non-finite; such compositions
    are counted and listed, never imputed.
 5. Metrics (--score only): MAE (GPa), Spearman rho and n per predictor x label x subset, on the compositions where
    that predictor and that label are defined (rows=own); and for every predictor on the common compositions where
    all predictors of the run are defined (rows=common).
 6. Default mode is a dry run: it builds every prediction and prints coverage only. It never computes a label value
    and never compares a prediction with a label. --score requires --confirm-one-shot, computes the metrics once and
    writes ledger/external_zhang_<UTC timestamp>.csv (plus per-composition predictions and labels to
    data/raw/external/, gitignored). It refuses to run if any ledger/external_zhang_*.csv already exists. The predictor
    set is whatever is on that one command line; nothing may be added, dropped or tuned after seeing the result.

Usage (from the repo root):
  uv run --with openpyxl python scripts/get_external.py         # once: xlsx -> csv + MP moduli cache
  .venv/bin/python eval/external_zhang.py --formula NAME="EXPR" --compose NAME="B_EXPR|K_EXPR" --svr           # dry run
  .venv/bin/python eval/external_zhang.py <same predictors> --score --confirm-one-shot                         # one shot
"""
import argparse
import contextlib
import io
import os
import re
import subprocess
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import sympy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from eval.score import eval_equation  # noqa: E402
from eval.tehrani_baseline import element_group  # noqa: E402
from scripts.get_external import DATA_CSV, MP_CSV, XLSX, clean_formula  # noqa: E402
from scripts.make_splits import chen_hardness  # noqa: E402
from sr.run_pysr import DERIVED_TARGETS, add_descriptors, featurize  # noqa: E402

LABELS = {
    "hv_lowload": "median Hv over 0.49 <= load <= 1.96 N (headline)",
    "hv_highload": "median Hv over load >= 4.9 N (secondary)",
}
LOAD_TOL = 1e-6
B_MIN, K_MIN, K_MAX_FROZEN = 1.0, 1e-3, 1.377
RESERVED = {"chen_dft", "svr_magpie"}


# ---------------------------------------------------------------------------------------------------------- data
def load_compositions(with_values):
    """Per-composition table. Label VALUES are computed only if with_values (i.e. under --score)."""
    raw = pd.read_csv(DATA_CSV)
    if not {"composition", "hardness", "load"} <= set(raw.columns):
        raise SystemExit(f"unexpected columns in {DATA_CSV.name}: {list(raw.columns)}")
    n_rows = len(raw)
    raw["reduced_formula"] = raw["composition"].map(clean_formula)
    bad = sorted(set(raw.loc[raw.reduced_formula.isna(), "composition"].astype(str)))
    raw = raw[raw.reduced_formula.notna()].reset_index(drop=True)
    load = pd.to_numeric(raw["load"], errors="coerce")
    hv = pd.to_numeric(raw["hardness"], errors="coerce")
    windows = {
        "hv_lowload": (load >= 0.49 - LOAD_TOL) & (load <= 1.96 + LOAD_TOL),
        "hv_highload": load >= 4.9 - LOAD_TOL,
    }
    t = pd.DataFrame(index=pd.Index(sorted(raw.reduced_formula.unique()), name="reduced_formula"))
    info = dict(rows_raw=n_rows, rows_unparseable=n_rows - len(raw), unparseable=bad,
                rows_clean=len(raw), compositions=len(t))
    for lab, w in windows.items():
        m = w & hv.notna()
        t["has_" + lab] = t.index.isin(raw.reduced_formula[m])
        info["rows_" + lab] = int(m.sum())
        if with_values:
            t[lab] = hv[m].groupby(raw.reduced_formula[m]).median()
    seen = set()
    for s in ("train", "val"):
        seen |= set(pd.read_csv(ROOT / f"data/splits/{s}.csv").formula.map(element_group))
    t["novel"] = ~t.index.map(element_group).isin(seen)
    return t, info


@contextlib.contextmanager
def quiet():
    with warnings.catch_warnings(), contextlib.redirect_stderr(io.StringIO()):
        warnings.simplefilter("ignore")
        yield


def build_features(formulas, descs):
    """featurize() on all compositions; if a descriptor raises, isolate the failing compositions row by row.

    Returns X (index = formulas, NaN where a feature cannot be computed) and {formula: reason} for descriptor failures.
    """
    df = pd.DataFrame({"formula": list(formulas)})
    failures = {}
    with quiet():
        try:
            d, X = featurize(df, descs)
        except Exception:
            d, X = featurize(df, [])
            for name in descs:
                try:
                    X[name] = add_descriptors(d, X, [name])[name].values
                    continue
                except Exception:
                    pass
                col = np.full(len(d), np.nan)
                for i in range(len(d)):
                    try:
                        col[i] = add_descriptors(d.iloc[[i]], X.iloc[[i]], [name])[name].iloc[0]
                    except Exception as e:
                        failures.setdefault(d.formula.iloc[i], []).append(f"{name}: {type(e).__name__} {e}"[:90])
                X[name] = col
    X.index = pd.Index(formulas, name="reduced_formula")
    return X, failures


# ---------------------------------------------------------------------------------------------------- predictors
def parse_specs(items, kind):
    out = []
    for it in items:
        name, sep, expr = it.partition("=")
        name, expr = name.strip(), expr.strip()
        if not sep or not re.fullmatch(r"[A-Za-z0-9_.\-]+", name) or not expr:
            raise SystemExit(f"--{kind} expects NAME=EXPR, got {it!r}")
        if kind == "compose":
            b, sep2, k = expr.partition("|")
            if not sep2 or not b.strip() or not k.strip():
                raise SystemExit(f"--compose expects NAME=B_EXPR|K_EXPR, got {it!r}")
            expr = (b.strip(), k.strip())
        out.append((name, kind, expr))
    return out


def expressions(spec):
    return list(spec[2]) if spec[1] == "compose" else [spec[2]]


def used_symbols(expr, columns):
    syms = {c: sympy.Symbol(c) for c in columns}
    return sorted(s.name for s in sympy.sympify(expr, locals=syms).free_symbols)


def evaluate(expr, X):
    with np.errstate(all="ignore"):
        return eval_equation(expr, X)


def predict_spec(spec, X, k_max):
    name, kind, expr = spec
    if kind == "formula":
        return evaluate(expr, X)
    with np.errstate(all="ignore"):
        B = np.clip(evaluate(expr[0], X), B_MIN, None)
        k = np.clip(evaluate(expr[1], X), K_MIN, k_max)
        return chen_hardness(k * B, B)


def chen_dft(formulas):
    mp = pd.read_csv(MP_CSV).set_index("reduced_formula").reindex(formulas)
    K, G = mp.K_vrh.values.astype(float), mp.G_vrh.values.astype(float)
    ok = np.isfinite(K) & np.isfinite(G) & (K > 0) & (G > 0)
    pred = np.full(len(formulas), np.nan)
    with np.errstate(all="ignore"):
        pred[ok] = chen_hardness(G[ok], K[ok])
    n_mp = int(mp.material_id.notna().sum())
    return pred, f"{n_mp} with MP elasticity, {n_mp - int(ok.sum())} of those with K_vrh or G_vrh <= 0"


def svr_magpie(formulas, quick, jobs):
    os.environ["LOKY_MAX_CPU_COUNT"] = str(jobs)  # tuned_svr runs GridSearchCV(n_jobs=-1)
    from eval.tehrani_baseline import magpie_all, tuned_svr

    tr = pd.read_csv(ROOT / "data/splits/train.csv")
    with quiet():
        Xtr = magpie_all(tr)
        gs = tuned_svr(Xtr, tr.hv_chen.values, tr.formula.map(element_group).values, quick)
        try:
            Xz = magpie_all(pd.DataFrame({"formula": list(formulas)}))
        except Exception:
            rows = []
            for f in formulas:
                try:
                    rows.append(magpie_all(pd.DataFrame({"formula": [f]})).iloc[0])
                except Exception:
                    rows.append(pd.Series(np.nan, index=Xtr.columns))
            Xz = pd.DataFrame(rows).reset_index(drop=True)
    Xz = Xz[Xtr.columns].astype(float)
    ok = np.isfinite(Xz.values).all(axis=1)
    pred = np.full(len(formulas), np.nan)
    pred[ok] = gs.predict(Xz.values[ok])
    note = f"train grouped-CV MAE (hv_chen) {-gs.best_score_:.3f}, {gs.best_params_}{' [QUICK GRID]' if quick else ''}"
    return pred, note


# ------------------------------------------------------------------------------------------------------- report
def coverage(t, defined):
    common = np.logical_and.reduce(list(defined.values()))
    rows = {name: m for name, m in defined.items()}
    rows["common (all predictors)"] = common
    rows["(compositions)"] = np.ones(len(t), bool)
    out = {}
    for name, m in rows.items():
        r = {}
        for sub in ("all", "novel"):
            s = m & (t.novel.values if sub == "novel" else True)
            r[(sub, "any")] = int(s.sum())
            for lab in LABELS:
                r[(sub, lab)] = int((s & t["has_" + lab].values).sum())
        out[name] = r
    df = pd.DataFrame(out).T
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=["subset", "label"])
    return df


def metrics(t, preds, defined):
    from scipy.stats import spearmanr

    common = np.logical_and.reduce(list(defined.values()))
    rows = []
    for lab in LABELS:
        y = t[lab].values.astype(float)
        has = np.isfinite(y)
        for sub in ("all", "novel"):
            smask = t.novel.values if sub == "novel" else np.ones(len(t), bool)
            for rowset in ("own", "common"):
                for name, p in preds.items():
                    sel = smask & has & (defined[name] if rowset == "own" else common)
                    n = int(sel.sum())
                    mae = float(np.mean(np.abs(p[sel] - y[sel]))) if n else np.nan
                    rho = float(spearmanr(p[sel], y[sel]).statistic) if n >= 3 else np.nan
                    rows.append(dict(predictor=name, label=lab, subset=sub, rows=rowset, n=n, mae_gpa=mae,
                                     spearman_rho=rho))
    return pd.DataFrame(rows)


def git(*args):
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


# --------------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--formula", action="append", default=[], metavar="NAME=EXPR", help="direct Hv formula")
    ap.add_argument("--compose", action="append", default=[], metavar="NAME=B_EXPR|K_EXPR",
                    help="Hv = Chen(k*B, B) from a bulk-modulus and a Pugh-ratio formula")
    ap.add_argument("--svr", action="store_true", help="add the Magpie SVR (direct hv_chen) refitted on train")
    ap.add_argument("--svr-quick", action="store_true", help="smoke test only: small SVR grid (refused with --score)")
    ap.add_argument("--jobs", type=int, default=2, help="CPU cores for the SVR grid search (default 2)")
    ap.add_argument("--score", action="store_true", help="THE one-shot scoring run (needs --confirm-one-shot)")
    ap.add_argument("--confirm-one-shot", action="store_true")
    args = ap.parse_args()

    if args.score:
        if not args.confirm_one_shot:
            raise SystemExit("--score is the one-shot external check; add --confirm-one-shot to run it")
        if args.svr_quick:
            raise SystemExit("--svr-quick is for smoke tests; the frozen protocol uses the full SVR grid")
        prev = sorted((ROOT / "ledger").glob("external_zhang_*.csv"))
        if prev:
            raise SystemExit(f"refusing: the one shot was already taken ({prev[0].relative_to(ROOT)})")
    for p in (DATA_CSV, MP_CSV):
        if not p.exists():
            raise SystemExit(f"missing {p.relative_to(ROOT)}; run scripts/get_external.py first")

    specs = parse_specs(args.formula, "formula") + parse_specs(args.compose, "compose")
    names = [s[0] for s in specs]
    clash = sorted({n for n in names if names.count(n) > 1 or n in RESERVED})
    if clash:
        raise SystemExit(f"predictor names must be unique and not {sorted(RESERVED)}: {clash}")
    descs = sorted({d for s in specs for e in expressions(s) for d in re.findall(r"\bd_\d{3}\b", e)})
    missing = [d for d in descs if not (ROOT / f"descriptors/{d}.py").exists()]
    if missing:
        raise SystemExit(f"unknown descriptors: {missing}")

    t, info = load_compositions(with_values=args.score)
    formulas = list(t.index)
    print(f"Zhang 2021: {info['rows_raw']} rows, {info['rows_unparseable']} unparseable "
          f"{info['unparseable'] if info['unparseable'] else ''}-> {info['rows_clean']} rows, "
          f"{info['compositions']} compositions; novel (element set not in train/val): {int(t.novel.sum())}")
    for lab, desc in LABELS.items():
        print(f"  {lab:12s} {desc}: {info['rows_' + lab]} rows -> {int(t['has_' + lab].sum())} compositions "
              f"({int((t['has_' + lab] & t.novel).sum())} novel)")

    k_max = float(DERIVED_TARGETS["pugh_k"](pd.read_csv(ROOT / "data/splits/train.csv")).max())
    if abs(k_max - K_MAX_FROZEN) > 1e-3:
        raise SystemExit(f"train k_max {k_max:.4f} != frozen {K_MAX_FROZEN}: the splits changed")

    preds, notes, kinds = {}, {}, {}
    preds["chen_dft"], notes["chen_dft"] = chen_dft(formulas)
    kinds["chen_dft"] = "chen(G_vrh, K_vrh) on Materials Project moduli"

    if specs:
        X, failures = build_features(formulas, descs)
        print(f"featurized {len(formulas)} compositions with Magpie means + {descs or 'no descriptors'}")
        for f, why in sorted(failures.items()):
            print(f"  descriptor failed for {f}: {'; '.join(why)}")
        for spec in specs:
            name, kind, expr = spec
            used = sorted({u for e in expressions(spec) for u in used_symbols(e, X.columns)})
            unknown = [u for u in used if u not in X.columns]
            if unknown:
                raise SystemExit(f"{name}: unknown variables {unknown}")
            preds[name] = predict_spec(spec, X, k_max)
            kinds[name] = f"{kind}: {expr if kind == 'formula' else ' | '.join(expr)}"
            nan_feat = ~np.isfinite(X[used].values.astype(float)).all(axis=1)
            bad_out = ~np.isfinite(preds[name]) & ~nan_feat
            msg = f"{int(nan_feat.sum())} with a non-finite input feature"
            if nan_feat.any():
                per = {u: int((~np.isfinite(X[u].values.astype(float))).sum()) for u in used}
                msg += f" {{{', '.join(f'{u}: {n}' for u, n in per.items() if n)}}}"
            msg += f", {int(bad_out.sum())} with a non-finite output"
            if 0 < (nan_feat | bad_out).sum() <= 12:
                msg += f" {sorted(np.array(formulas)[nan_feat | bad_out])}"
            notes[name] = msg

    if args.svr or args.svr_quick:
        print(f"fitting Magpie SVR on train ({'quick' if args.svr_quick else 'full'} grid, {args.jobs} cores) ...")
        preds["svr_magpie"], notes["svr_magpie"] = svr_magpie(formulas, args.svr_quick, args.jobs)
        kinds["svr_magpie"] = "Magpie SVR, direct hv_chen, refit on train"

    defined = {n: np.isfinite(p) for n, p in preds.items()}
    print("\npredictors (undefined compositions are excluded, never imputed):")
    for n in preds:
        print(f"  {n:14s} defined for {int(defined[n].sum())}/{len(formulas)}; {kinds[n]}")
        print(f"  {'':14s} {notes[n]}")
    print("\ncoverage: number of compositions where the predictor AND the label are defined")
    print(coverage(t, defined).to_string())

    if not args.score:
        print("\nDRY RUN: no label values computed, no metrics. The one shot is --score --confirm-one-shot.")
        return

    ts = datetime.now(timezone.utc)
    stamp = ts.strftime("%Y%m%dT%H%M%SZ")
    res = metrics(t, preds, defined)
    res.insert(0, "expression", res.predictor.map(kinds))
    for col, val in (("commit", git("rev-parse", "HEAD")), ("branch", git("rev-parse", "--abbrev-ref", "HEAD")),
                     ("timestamp", ts.isoformat(timespec="seconds"))):
        res.insert(0, col, val)
    out = ROOT / f"ledger/external_zhang_{stamp}.csv"
    res.to_csv(out, index=False, float_format="%.4f")
    pr = t[["novel", *LABELS]].copy()
    for n, p in preds.items():
        pr[n] = p
    pr.to_csv(XLSX.parent / f"zhang_predictions_{stamp}.csv", float_format="%.4f")
    show = res.drop(columns=["timestamp", "branch", "commit", "expression"])
    print("\nEXTERNAL CHECK (one shot): MAE in GPa, Spearman rho")
    print(show.set_index(["label", "subset", "rows", "predictor"]).round(3).to_string())
    print(f"\nwrote {out.relative_to(ROOT)} and {(XLSX.parent / f'zhang_predictions_{stamp}.csv').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
