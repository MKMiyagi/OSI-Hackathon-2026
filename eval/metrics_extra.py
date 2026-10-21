"""Secondary metrics (pre-registered in wiki/DECISIONS.md, "Secondary metrics (pre-registered Wed 15:30)").

Usage:
  uv run python eval/metrics_extra.py --run c020_s0 [c020_s1 ...]   # Pareto equations of the given runs
  uv run python eval/metrics_extra.py --all                          # every hv_chen run in ledger/runs/
Baseline rows (Magpie-SVR variants, train-median constant) are always (re)computed with the first call and
cached in ledger/baseline_val_preds.csv; delete that file to refit.

For every Pareto equation, the SVR baseline and the train-median constant, on data/splits/val.csv (never the test
file), against hv_chen:
  mae          MAE in GPa (the frozen headline; must equal eval/score.py's val_mae, checked against the ledger)
  mase_const   mae / val MAE of the train-median constant
  mase_svr     mae / val MAE of the primary SVR (Magpie features, log B, log G -> Chen); 1.0 = black box
  gap_closed   (MAE_const - mae) / (MAE_const - MAE_svr)  (rewriting of the three MAEs, not a new metric)
  log_mae      mean |log(y+3) - log(yhat+3)| over rows with yhat > -3; n_log_fail = rows with yhat <= -3
  mae_<bin>    MAE within bins of the TRUE value: <5, [5,15), [15,25), >=25 GPa (n_<bin> = bin sizes)
  spearman     Spearman rho(yhat, y) (NaN for a constant prediction)
  prec_top10   fraction of the ceil(0.1 n) highest predictions that are in the true top ceil(0.1 n); ties in yhat
               are broken at random in expectation, so a constant scores chance level
Does not edit score.py or the splits. Writes ledger/metrics_extra.csv (rows for the requested runs are replaced).
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

BIN_EDGES = (5.0, 15.0, 25.0)
BIN_NAMES = ("lt5", "5_15", "15_25", "ge25")
EXCLUDED_FEATURES = ("m_MeltingT", "m_SpaceGroupNumber")
OUT = ROOT / "ledger/metrics_extra.csv"
BASELINE_CACHE = ROOT / "ledger/baseline_val_preds.csv"
PRIMARY_SVR = "svr_magpie_BG"
CONST = "train_median"


# ---------------------------------------------------------------- pure metric functions
def mae(y, p):
    return float(np.mean(np.abs(np.asarray(y, float) - np.asarray(p, float))))


def log_mae(y, p):
    """(MAE of log(y+3) over non-failures, number of failures). Failure = prediction <= -3."""
    y, p = np.asarray(y, float), np.asarray(p, float)
    if (y <= -3).any():
        raise ValueError("target below -3: log(y+3) undefined")
    ok = np.isfinite(p) & (p > -3)
    n_fail = int((~ok).sum())
    if not ok.any():
        return float("nan"), n_fail
    return float(np.mean(np.abs(np.log(y[ok] + 3) - np.log(p[ok] + 3)))), n_fail


def bin_index(y):
    return np.digitize(np.asarray(y, float), BIN_EDGES)  # 0: <5, 1: [5,15), 2: [15,25), 3: >=25


def binned_mae(y, p):
    y, p = np.asarray(y, float), np.asarray(p, float)
    idx = bin_index(y)
    return [mae(y[idx == b], p[idx == b]) if (idx == b).any() else float("nan") for b in range(4)], \
           [int((idx == b).sum()) for b in range(4)]


def spearman(y, p):
    y, p = np.asarray(y, float), np.asarray(p, float)
    if np.ptp(p) == 0 or np.ptp(y) == 0:
        return float("nan")
    return float(np.corrcoef(rankdata(y), rankdata(p))[0, 1])


def precision_top(y, p, frac=0.1):
    """Expected overlap of the top-k predictions with the true top-k (k = ceil(frac n)); ties in p random."""
    y, p = np.asarray(y, float), np.asarray(p, float)
    n = len(y)
    k = math.ceil(frac * n)
    true_top = np.zeros(n, bool)
    true_top[np.argsort(-y, kind="stable")[:k]] = True
    thr = np.sort(p)[::-1][k - 1]
    above = p > thr
    tied = p == thr
    expected = true_top[above].sum() + (k - above.sum()) * true_top[tied].sum() / tied.sum()
    return float(expected / k)


def all_metrics(y, p, const_mae, svr_mae):
    m = mae(y, p)
    lm, nf = log_mae(y, p)
    bm, bn = binned_mae(y, p)
    row = dict(mae=m, mase_const=m / const_mae, mase_svr=m / svr_mae,
               gap_closed=(const_mae - m) / (const_mae - svr_mae), log_mae=lm, n_log_fail=nf)
    row.update({f"mae_{n}": v for n, v in zip(BIN_NAMES, bm)})
    row.update({f"n_{n}": v for n, v in zip(BIN_NAMES, bn)})
    row.update(spearman=spearman(y, p), prec_top10=precision_top(y, p))
    return row


# ---------------------------------------------------------------- baselines
def load_data():
    tr = pd.read_csv(ROOT / "data/splits/train.csv")
    va = pd.read_csv(ROOT / "data/splits/val.csv")
    return tr, va


def fit_baselines(tr, va):
    """Refit the Tehrani-style SVR arms exactly as eval/tehrani_baseline.py does (same grid, CV, log-moduli)."""
    from eval.tehrani_baseline import element_group, feature_sets, tuned_svr
    from scripts.make_splits import chen_hardness

    groups = tr.formula.map(element_group).values
    preds = {CONST: np.full(len(va), float(np.median(tr.hv_chen)))}
    names = {"magpie": "svr_magpie", "tehrani_comp": "svr_tehranicomp", "tehrani150": "svr_tehrani150"}
    for fs, (Xtr, Xva) in feature_sets(tr, va).items():
        fits = {}
        for tgt in ("bulk_modulus", "shear_modulus", "hv_chen"):
            log = tgt != "hv_chen"
            y = np.log(tr[tgt].values) if log else tr[tgt].values
            gs = tuned_svr(Xtr, y, groups, quick=False)
            fits[tgt] = np.exp(gs.predict(Xva.values)) if log else gs.predict(Xva.values)
        preds[f"{names[fs]}_BG"] = chen_hardness(fits["shear_modulus"], fits["bulk_modulus"])
        preds[f"{names[fs]}_direct"] = fits["hv_chen"]
        preds[f"{names[fs]}_B"] = fits["bulk_modulus"]  # B, G kept for the literature comparison
        preds[f"{names[fs]}_G"] = fits["shear_modulus"]
    return pd.DataFrame(preds, index=va.index)


def get_baselines(tr, va):
    if BASELINE_CACHE.exists():
        c = pd.read_csv(BASELINE_CACHE, index_col=0)
        if len(c) == len(va) and c.index.equals(va.index):
            return c
    c = fit_baselines(tr, va)
    c.to_csv(BASELINE_CACHE, float_format="%.8g")
    return c


def check_against_recorded(base, va):
    """Refit must reproduce eval/tehrani_baseline.csv val MAE (to 1e-3); report otherwise."""
    rec = pd.read_csv(ROOT / "eval/tehrani_baseline.csv")
    rec = rec[rec.quantity == "hv_chen"]
    cols = {("magpie", "BG"): "svr_magpie_BG", ("magpie", "direct"): "svr_magpie_direct",
            ("tehrani_comp", "BG"): "svr_tehranicomp_BG", ("tehrani_comp", "direct"): "svr_tehranicomp_direct",
            ("tehrani150", "BG"): "svr_tehrani150_BG", ("tehrani150", "direct"): "svr_tehrani150_direct"}
    ok = True
    for (fs, route), col in cols.items():
        r = float(rec[(rec.features == fs) & (rec.route == route)].val_mae.iloc[0])
        got = mae(va.hv_chen, base[col])
        flag = "ok" if abs(got - r) < 1e-3 else "MISMATCH"
        ok &= flag == "ok"
        print(f"  baseline refit {col:26s} val MAE {got:.4f} vs recorded {r:.4f}  {flag}")
    return ok


# ---------------------------------------------------------------- equations
def score_runs(run_ids, va, const_mae, svr_mae):
    from eval.score import eval_equation
    from sr.run_pysr import add_descriptors, magpie_means

    df, X0 = magpie_means(va.copy(), "formula")
    y = va.hv_chen.astype(float).values
    ledger = pd.read_csv(ROOT / "ledger/results.csv")
    ledger = ledger[ledger.split == "val"]
    led = {}
    for r in ledger.itertuples():
        led.setdefault((r.run_id, int(r.complexity), str(r.formula)), []).append(float(r.val_mae))

    feats, rows, mismatches = {}, [], 0
    for rid in run_ids:
        meta = json.loads((ROOT / f"ledger/runs/{rid}.json").read_text())
        if meta["target"] != "hv_chen":
            print(f"skip {rid}: target {meta['target']}")
            continue
        descs = tuple(meta["descriptors"])
        if descs not in feats:
            X = add_descriptors(df, X0, list(descs))
            if not np.isfinite(X.astype(float).values).all():
                raise SystemExit(f"{rid}: non-finite val features; refusing to score")
            feats[descs] = X
        X = feats[descs]
        eqs = pd.read_csv(ROOT / f"ledger/runs/{rid}.csv")
        dset = "+".join(descs) if descs else "magpie_only"
        for _, e in eqs.iterrows():
            p = eval_equation(e["equation"], X)
            if not np.isfinite(p).all():
                raise SystemExit(f"{rid} c{e['complexity']}: non-finite predictions")
            row = dict(run_id=rid, descriptor_set=dset, complexity=int(e["complexity"]), formula=e["equation"],
                       n_val=len(y), uses_excluded_feature=any(f in e["equation"] for f in EXCLUDED_FEATURES))
            row.update(all_metrics(y, p, const_mae, svr_mae))
            key = (rid, int(e["complexity"]), str(e["equation"]))
            if key in led:
                row["ledger_mae_match"] = bool(min(abs(row["mae"] - v) for v in led[key]) < 1e-4)
                mismatches += not row["ledger_mae_match"]
            else:
                row["ledger_mae_match"] = None  # run never appended to the ledger
            rows.append(row)
    return rows, mismatches


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", nargs="+", default=[])
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if not args.run and not args.all:
        ap.error("give --run <id> ... or --all")

    tr, va = load_data()
    y = va.hv_chen.astype(float).values
    base = get_baselines(tr, va)
    print("baseline refit check:")
    refit_ok = check_against_recorded(base, va)
    const_mae, svr_mae = mae(y, base[CONST]), mae(y, base[PRIMARY_SVR])
    print(f"constant (train median {np.median(tr.hv_chen):.4f}) val MAE {const_mae:.4f}; primary SVR {svr_mae:.4f}")

    runs = args.run if not args.all else sorted(p.stem for p in (ROOT / "ledger/runs").glob("*.json"))
    rows, mismatches = score_runs(runs, va, const_mae, svr_mae)

    brows = []
    for name in base.columns:
        if name.endswith(("_B", "_G")):
            continue  # moduli predictions, not hv; used by the literature comparison only
        r = dict(run_id="baseline", descriptor_set=name, complexity=np.nan, formula="", n_val=len(y),
                 uses_excluded_feature=False, ledger_mae_match=None)
        r.update(all_metrics(y, base[name].values, const_mae, svr_mae))
        brows.append(r)

    new = pd.DataFrame(brows + rows)
    if OUT.exists():
        old = pd.read_csv(OUT)
        old = old[~old.run_id.isin(set(new.run_id))]
        new = pd.concat([old, new], ignore_index=True)
    new.to_csv(OUT, index=False, float_format="%.6g")
    print(f"scored {len(rows)} equations from {len(set(r['run_id'] for r in rows))} runs; ledger mismatches: {mismatches}; "
          f"baseline refit {'reproduces recorded MAEs' if refit_ok else 'DOES NOT reproduce recorded MAEs'}")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
