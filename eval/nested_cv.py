"""Frozen nested grouped CV: predictive comparison of Magpie-only SR vs +d_008 vs +d_008+d_018.

Protocol (wiki/RESEARCH_REVIEW_3_VERDICT.md, "Minimum extra evidence"):
  * pool data/splits/train.csv + val.csv (never test); group key = sorted element set, as in
    scripts/make_splits.py; 5 outer folds, group-shuffled with seed 42, filled by cumulative rows.
  * per outer fold: grouped 80/20 inner split of the outer-training rows (seed 42 + fold, same for
    every arm), fit PySR on the inner-train rows with ONE fixed config, and for each complexity
    window (<=9/12/15) pick the equation with the lowest inner-validation MAE. Constants stay as
    fitted on inner-train (no refit). The pick is scored once on the outer test fold.
  * nothing is chosen using outer-test rows. Arms share folds, inner splits and PySR seed.
  * arms: magpie, magpie+d_008, magpie+d_008+d_018, and the outer-train median constant.
  * a selected equation that is non-finite on some outer-test rows gets the outer-train median for
    those rows (pre-declared fallback, counted in n_nonfinite). Equations that are non-finite on
    any inner-val row are ineligible.

Overnight-5 additions (arms are now configurable, protocol unchanged):
  --arms NAME...   any of median_const, svr_baseline, svr_fitidx, magpie, magpie+d_0XX[+d_0YY...]. Default = the
                   original three-arm set. svr_baseline = eval/tehrani_baseline.py's Magpie SVR (log B, log G -> Chen,
                   grid tuned by grouped 5-fold CV) fitted on ALL outer-training rows inside each outer fold;
                   svr_fitidx = the same fitted on the inner-train rows only (the rows the PySR arms see).
  --folds 0 1 ..   restrict to these outer folds;  --fit-only --shard i/n  fit and cache only every n-th PySR task
                   (two processes can share one run id's fit cache; a final non-sharded call assembles the CSV).
  --report-d023 RUN...   write wiki/NESTED_CV_D023.md from the given run ids.

Usage: uv run python eval/nested_cv.py --run-id ncv_pilot --niterations 5000 --seed 0
       uv run python eval/nested_cv.py --report            # rebuild wiki/NESTED_CV.md from ledger/nested_cv/*.csv
Resumable: per-fit Pareto fronts are cached in ledger/nested_cv/<run-id>_fits/.
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from pymatgen.core import Composition

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from eval.score import eval_equation  # noqa: E402
from sr.run_pysr import DEFAULT_EXCLUDE, featurize  # noqa: E402

OUT = ROOT / "ledger/nested_cv"
SEED = 42
N_OUTER = 5
WINDOWS = (9, 12, 15)
TAIL = 20.0
ARMS = {
    "magpie": [],
    "magpie+d_008": ["d_008"],
    "magpie+d_008+d_018": ["d_008", "d_018"],
}
CONST = "median_const"
SVR_ARMS = ("svr_baseline", "svr_fitidx")
DESC_RE = re.compile(r"\bd_\d{3}\b")


def parse_arms(names):
    """Arm name -> list of descriptors ([] for plain magpie); SVR/const arms are handled separately."""
    arms = {}
    for n in names:
        if n == CONST or n in SVR_ARMS:
            continue
        parts = n.split("+")
        if parts[0] != "magpie" or not all(re.fullmatch(r"d_\d{3}", d) for d in parts[1:]):
            raise SystemExit(f"unknown arm {n!r}")
        arms[n] = parts[1:]
    return arms


def group_key(formula):
    return "-".join(sorted(el.symbol for el in Composition(formula).elements))


def split_groups(groups, fracs, seed):
    """Shuffle unique groups, fill parts in order by cumulative row count (make_splits style)."""
    uniq = np.array(sorted(set(groups)))
    sizes = pd.Series(groups).value_counts()
    rng = np.random.default_rng(seed)
    rng.shuffle(uniq)
    targets = np.cumsum(fracs) * len(groups)
    assign, cum, k = {}, 0, 0
    for g in uniq:
        if cum >= targets[k] and k < len(fracs) - 1:
            k += 1
        assign[g] = k
        cum += sizes[g]
    return pd.Series(groups).map(assign).values


def make_model(niterations, maxsize, procs, timeout, seed):
    """Same search config as sr/run_pysr.py."""
    from pysr import PySRRegressor

    return PySRRegressor(
        niterations=niterations,
        maxsize=maxsize,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["sqrt", "log", "exp"],
        nested_constraints={op: {"sqrt": 0, "log": 0, "exp": 0} for op in ("sqrt", "log", "exp")},
        procs=procs,
        timeout_in_seconds=timeout,
        random_state=seed,
        deterministic=False,
        progress=False,
        temp_equation_file=True,
    )


def predict(eq, X, fallback):
    """Return (pred, n_nonfinite) with non-finite entries replaced by fallback."""
    try:
        pred = eval_equation(eq, X)
    except Exception:
        return np.full(len(X), fallback), len(X)
    bad = ~np.isfinite(pred)
    pred[bad] = fallback
    return pred, int(bad.sum())


def svr_predict(data, fit_rows, test_rows, groups, cache):
    """Tehrani-protocol SVR (log B, log G, grouped-CV grid; then Chen) fitted on fit_rows, predicting test_rows. Cached."""
    if cache.exists():
        return np.array(json.loads(cache.read_text())["pred"])
    from eval.chen import chen_hardness
    from eval.tehrani_baseline import tuned_svr

    F = data["F"]
    Xf, Xt = F.iloc[fit_rows], F.iloc[test_rows]
    fits = {}
    for name in ("B", "G"):
        gs = tuned_svr(Xf, np.log(data[name][fit_rows]), groups[fit_rows], quick=False)
        fits[name] = (np.exp(gs.predict(Xt.values)), str(gs.best_params_))
    pred = chen_hardness(fits["G"][0], fits["B"][0])
    cache.write_text(json.dumps(dict(pred=[float(v) for v in pred], params_B=fits["B"][1], params_G=fits["G"][1])))
    return pred


def mae(y, p):
    return float(np.mean(np.abs(y - p))) if len(y) else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id")
    ap.add_argument("--niterations", type=int, default=22000)
    ap.add_argument("--maxsize", type=int, default=15)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--arms", nargs="*", default=None)
    ap.add_argument("--folds", nargs="*", type=int, default=None)
    ap.add_argument("--fit-only", action="store_true")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--report-d023", nargs="*", default=None)
    args = ap.parse_args()
    if args.report:
        write_report()
        return
    if args.report_d023:
        write_report_d023(args.report_d023)
        return
    arm_names = args.arms if args.arms is not None else [CONST] + list(ARMS)
    arms = parse_arms(arm_names)
    shard_i, shard_n = (int(v) for v in args.shard.split("/"))
    folds_to_run = args.folds if args.folds is not None else list(range(N_OUTER))
    if not args.run_id:
        raise SystemExit("--run-id required")

    OUT.mkdir(parents=True, exist_ok=True)
    fits = OUT / f"{args.run_id}_fits"
    fits.mkdir(exist_ok=True)

    df = pd.concat(
        [pd.read_csv(ROOT / f"data/splits/{s}.csv") for s in ("train", "val")], ignore_index=True
    )
    df["group"] = [group_key(f) for f in df.formula]
    all_descs = sorted({d for ds in arms.values() for d in ds})
    df, X = featurize(df, all_descs)
    exclude = [c for c in DEFAULT_EXCLUDE.split(",") if c]
    X = X.astype(float)
    y = df["hv_chen"].astype(float).values
    keep = np.isfinite(y) & np.isfinite(X.values).all(axis=1)
    print(f"rows kept: {keep.sum()}/{len(keep)}")
    df, X, y = df[keep].reset_index(drop=True), X[keep].reset_index(drop=True), y[keep]
    groups = df["group"].values
    outer = split_groups(groups, [1 / N_OUTER] * N_OUTER, SEED)
    meta = dict(vars(args), outer_seed=SEED, n_rows=int(len(y)), n_groups=int(len(set(groups))))
    meta["arms"] = arm_names
    if not args.fit_only:
        (OUT / f"{args.run_id}.json").write_text(json.dumps(meta))
    svr_data = None
    if any(a in SVR_ARMS for a in arm_names):
        from eval.tehrani_baseline import magpie_all
        svr_data = dict(F=magpie_all(df[["formula"]]), B=df["bulk_modulus"].astype(float).values, G=df["shear_modulus"].astype(float).values)

    rows = []
    task_i = -1
    t_start = time.time()
    for fold in folds_to_run:
        tr_idx = np.where(outer != fold)[0]
        te_idx = np.where(outer == fold)[0]
        inner = split_groups(groups[tr_idx], [0.8, 0.2], SEED + fold)
        fit_idx, val_idx = tr_idx[inner == 0], tr_idx[inner == 1]
        med = float(np.median(y[tr_idx]))
        yte, tail = y[te_idx], y[te_idx] >= TAIL
        common = dict(run_id=args.run_id, seed=args.seed, fold=fold, n_test=len(te_idx), n_tail=int(tail.sum()))

        p = np.full(len(te_idx), med)
        for w in WINDOWS if (CONST in arm_names and not args.fit_only) else ():
            rows.append(dict(common, arm=CONST, window=w, complexity=0, inner_val_mae=mae(y[val_idx], np.full(len(val_idx), med)),
                             test_mae=mae(yte, p), tail_mae=mae(yte[tail], p[tail]), n_nonfinite=0, uses_desc="", equation=f"{med:.6f}"))

        if not args.fit_only:
            for arm in (a for a in arm_names if a in SVR_ARMS):
                fi = tr_idx if arm == "svr_baseline" else fit_idx
                pt = svr_predict(svr_data, fi, te_idx, groups, fits / f"{arm}_f{fold}.json")
                for w in WINDOWS:
                    rows.append(dict(common, arm=arm, window=w, complexity=0, inner_val_mae=float("nan"), test_mae=mae(yte, pt),
                                     tail_mae=mae(yte[tail], pt[tail]), n_nonfinite=int((~np.isfinite(pt)).sum()), uses_desc="",
                                     equation="svr"))

        for arm, descs in arms.items():
            cols = [c for c in X.columns if c not in exclude and (c.startswith("m_") or c in descs)]
            cache = fits / f"{arm}_f{fold}.csv"
            task_i += 1
            if cache.exists():
                eqs = pd.read_csv(cache)
            else:
                if task_i % shard_n != shard_i and args.fit_only:
                    continue
                if (ROOT / "STOP").exists():
                    raise SystemExit("STOP file present; fits so far are cached, rerun to resume")
                t0 = time.time()
                model = make_model(args.niterations, args.maxsize, args.procs, args.timeout, args.seed)
                model.fit(X.loc[fit_idx, cols].values, y[fit_idx], variable_names=cols)
                eqs = model.equations_[["complexity", "loss", "equation"]]
                eqs.to_csv(cache, index=False)
                print(f"fold {fold} {arm}: fit {time.time() - t0:.0f}s (elapsed {time.time() - t_start:.0f}s)", flush=True)
            if args.fit_only:
                continue
            inner_mae = []
            for eq in eqs.equation:
                pv, nb = predict(eq, X.loc[val_idx], med)
                inner_mae.append(mae(y[val_idx], pv) if nb == 0 else np.inf)
            eqs = eqs.assign(inner=inner_mae)
            for w in WINDOWS:
                cand = eqs[(eqs.complexity <= w) & np.isfinite(eqs.inner)]
                if cand.empty:
                    raise SystemExit(f"fold {fold} {arm} c<={w}: no eligible equation")
                best = cand.loc[cand.inner.idxmin()]
                pt, nb = predict(best.equation, X.loc[te_idx], med)
                used = sorted(set(DESC_RE.findall(best.equation)))
                rows.append(dict(common, arm=arm, window=w, complexity=int(best.complexity), inner_val_mae=float(best.inner),
                                 test_mae=mae(yte, pt), tail_mae=mae(yte[tail], pt[tail]), n_nonfinite=nb,
                                 uses_desc="+".join(used), equation=best.equation))
        if not args.fit_only:
            pd.DataFrame(rows).to_csv(OUT / f"{args.run_id}.csv", index=False)  # checkpoint after each fold

    if args.fit_only:
        print("fit-only done")
        return
    total = time.time() - t_start
    meta["total_seconds"] = round(total, 1)
    (OUT / f"{args.run_id}.json").write_text(json.dumps(meta))
    print(f"done in {total:.0f}s")
    if not args.run_id.startswith("ncv_d023"):
        write_report()


def fmt(v):
    return f"{np.nanmean(v):.3f} ± {np.nanstd(v, ddof=1) if len(v) > 1 else float('nan'):.3f}"


def write_report_d023(run_ids):
    """wiki/NESTED_CV_D023.md: tables only (numbers); the interpretive paragraph is added by hand after the review."""
    d = pd.concat([pd.read_csv(OUT / f"{r}.csv") for r in run_ids], ignore_index=True)
    meta = json.loads((OUT / f"{run_ids[0]}.json").read_text())
    folds = sorted(d.fold.unique())
    arms = [CONST] + [a for a in d.arm.unique() if a != CONST]
    L = [f"## Per-fold test MAE (GPa), mean ± sd over {len(folds)} outer folds", "",
         f"Runs {', '.join(run_ids)}; niterations={meta.get('niterations')}, seed={meta.get('seed')}, procs={meta.get('procs')}, "
         f"maxsize={meta.get('maxsize')}, timeout={meta.get('timeout')}s, rows={meta.get('n_rows')}, groups={meta.get('n_groups')}.", "",
         "| arm | window | " + " | ".join(f"f{k}" for k in folds) + " | mean ± sd | pooled tail MAE (>=20) | n_tail | folds with d_023 | nonfinite |",
         "|---|---|" + "---|" * (len(folds) + 5)]
    for arm in arms:
        for w in WINDOWS:
            s = d[(d.arm == arm) & (d.window == w)].sort_values("fold")
            if s.empty:
                continue
            tl = (s.tail_mae * s.n_tail).sum() / s.n_tail.sum() if s.n_tail.sum() else float("nan")
            n23 = int(s.uses_desc.fillna("").str.contains("d_023").sum())
            L.append(f"| {arm} | c<={w} | " + " | ".join(f"{v:.3f}" for v in s.test_mae) + f" | {fmt(s.test_mae.values)} | {tl:.2f} | "
                     f"{int(s.n_tail.sum())} | {n23}/{len(s)} | {int(s.n_nonfinite.sum())} |")
    L += ["", "## Selected equation per fold and window (complexity, inner-val MAE, outer-test MAE)", ""]
    for arm in arms:
        if arm == CONST or arm in SVR_ARMS:
            continue
        for w in WINDOWS:
            for _, r in d[(d.arm == arm) & (d.window == w)].sort_values("fold").iterrows():
                L.append(f"- {arm} c<={w} f{r.fold} (c{r.complexity}, inner {r.inner_val_mae:.3f}, test {r.test_mae:.3f}, uses {r.uses_desc if isinstance(r.uses_desc, str) and r.uses_desc else '-'}): `{r.equation}`")
    (ROOT / "ledger/nested_cv/ncv_d023_tables.md").write_text("\n".join(L))
    print("wrote ledger/nested_cv/ncv_d023_tables.md")


def write_report():
    runs = sorted(p for p in OUT.glob("*.csv") if not p.stem.startswith("ncv_d023"))
    if not runs:
        raise SystemExit("no ledger/nested_cv/*.csv")
    L = ["# Nested grouped CV (frozen predictive comparison)", "",
         "Generated by `eval/nested_cv.py --report`. Protocol is in that file's docstring. All numbers are outer-fold test MAE in GPa; "
         "equation choice used inner-validation rows only. Folds are 5 element-set-grouped folds over train+val (seed 42); "
         "mean ± sd are over the 5 outer folds (sd across folds is fold heterogeneity, not optimizer or selection uncertainty). "
         "Tail = outer-test rows with hv_chen >= 20 GPa (pooled over folds; per-fold in the CSV; fold tail counts are small and uneven).", ""]
    for f in runs:
        d = pd.read_csv(f)
        meta = json.loads(f.with_suffix(".json").read_text()) if f.with_suffix(".json").exists() else {}
        L += [f"## {f.stem}", "",
              f"niterations={meta.get('niterations')}, seed={meta.get('seed')}, procs={meta.get('procs')}, "
              f"maxsize={meta.get('maxsize')}, timeout={meta.get('timeout')}s, rows={meta.get('n_rows')}, "
              f"wall={meta.get('total_seconds', 'incomplete')}s", ""]
        L += ["| arm | window | " + " | ".join(f"f{k}" for k in sorted(d.fold.unique())) + " | mean ± sd | pooled tail MAE | n_tail | picked desc (folds) | nonfinite rows |",
              "|---|---|" + "---|" * (d.fold.nunique() + 5)]
        for arm in [CONST] + [a for a in d.arm.unique() if a != CONST]:
            for w in WINDOWS:
                s = d[(d.arm == arm) & (d.window == w)].sort_values("fold")
                if s.empty:
                    continue
                tl = (s.tail_mae * s.n_tail).sum() / s.n_tail.sum() if s.n_tail.sum() else float("nan")
                picked = int((s.uses_desc.fillna("") != "").sum())
                L.append(f"| {arm} | c<={w} | " + " | ".join(f"{v:.3f}" for v in s.test_mae) +
                         f" | {fmt(s.test_mae.values)} | {tl:.2f} | {int(s.n_tail.sum())} | {picked}/{len(s)} | {int(s.n_nonfinite.sum())} |")
        L += ["", "Selected equations (c<=12):", ""]
        for _, r in d[(d.window == 12) & (d.arm != CONST)].sort_values(["arm", "fold"]).iterrows():
            L.append(f"- {r.arm} f{r.fold} (c{r.complexity}, inner {r.inner_val_mae:.3f}, test {r.test_mae:.3f}): `{r.equation}`")
        L.append("")
    (ROOT / "wiki/NESTED_CV.md").write_text("\n".join(L))
    print("wrote wiki/NESTED_CV.md")


if __name__ == "__main__":
    main()
