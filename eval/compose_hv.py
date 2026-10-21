"""Score the B / Pugh-ratio route: Hv = Chen(G, B) from separately fitted formulas, on data/splits/val.csv.

Usage:
  uv run python eval/compose_hv.py --direct t1_hv_s0 t1_hv_s1 --B t1_B_s0 t1_B_s1 --k t1_k_s0 t1_k_s1 [--G ...]

Per seed i, the i-th B run is paired with the i-th k run (or G run). Every (B equation, k equation) pair on the two
Pareto fronts is evaluated; Hv = 2 (k^2 G)^0.585 - 3 with G = k B (Chen 2011). Guards, applied identically to every
route: B >= 1 GPa, 1e-3 <= k <= max train k.

Reported per complexity budget T (direct: equation complexity <= T; composed: c_B + c_k <= T, the fixed Chen layer
not counted):
  train-selected  the candidate with the lowest TRAIN Hv MAE within the budget, then its val MAE (no val selection)
  val-best        the lowest val MAE within the budget (the ledger's convention; optimistic, and more so for the
                  composed route, which has many more candidates per budget)
Uses eval/score.py's eval_equation and sr/run_pysr.py's featurize, so the metric is the frozen one. Never reads the
test file. Writes ledger/t1_compose.csv.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from eval.score import eval_equation  # noqa: E402
from scripts.make_splits import chen_hardness  # noqa: E402
from sr.run_pysr import DERIVED_TARGETS, featurize  # noqa: E402

BUDGETS = (9, 12, 15, 18, 24, 30)
B_MIN, K_MIN = 1.0, 1e-3


def meta(run):
    return json.loads((ROOT / f"ledger/runs/{run}.json").read_text())


def front(run, X):
    """Pareto equations of a run evaluated on X: {complexity: prediction array}."""
    eqs = pd.read_csv(ROOT / f"ledger/runs/{run}.csv")
    out = {}
    for _, r in eqs.iterrows():
        pred = eval_equation(r["equation"], X)
        if np.isfinite(pred).all():
            out[int(r["complexity"])] = pred
    return out


def target(df, name):
    return (DERIVED_TARGETS[name](df) if name in DERIVED_TARGETS else df[name]).astype(float).values


def mae(a, b):
    return float(np.mean(np.abs(a - b)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--direct", nargs="*", default=[], help="runs fitted directly on hv_chen")
    ap.add_argument("--B", nargs="*", default=[], help="runs fitted on bulk_modulus")
    ap.add_argument("--k", nargs="*", default=[], help="runs fitted on pugh_k (G/B)")
    ap.add_argument("--G", nargs="*", default=[], help="runs fitted on shear_modulus (alternative to --k)")
    args = ap.parse_args()
    partner, pname = (args.k, "k") if args.k else (args.G, "G")
    if args.B and len(args.B) != len(partner):
        raise SystemExit("--B and --k/--G need the same number of runs (paired by position)")

    runs = args.direct + args.B + partner
    descs = sorted({d for r in runs for d in meta(r)["descriptors"]})
    data = {s: pd.read_csv(ROOT / f"data/splits/{s}.csv") for s in ("train", "val")}
    X = {s: featurize(df, descs)[1] for s, df in data.items()}
    hv = {s: data[s].hv_chen.values for s in data}
    k_max = float(DERIVED_TARGETS["pugh_k"](data["train"]).max())

    rows = []
    print("single-target val MAE by complexity")
    for run in runs:
        tgt = meta(run)["target"]
        f = front(run, X["val"])
        y = target(data["val"], tgt)
        print(f"  {run:12s} {tgt:13s} " + "  ".join(f"c{c}:{mae(y, p):.3f}" for c, p in sorted(f.items())))

    def report(route, seed, cands):
        """cands: list of (complexity, train_pred, val_pred) for Hv."""
        for T in BUDGETS:
            inb = [c for c in cands if c[0] <= T]
            if not inb:
                continue
            tr_sel = min(inb, key=lambda c: mae(hv["train"], c[1]))
            va_best = min(inb, key=lambda c: mae(hv["val"], c[2]))
            rows.append(dict(route=route, seed=seed, budget=T, n_candidates=len(inb),
                             trainsel_c=tr_sel[0], trainsel_val_mae=mae(hv["val"], tr_sel[2]),
                             valbest_c=va_best[0], valbest_val_mae=mae(hv["val"], va_best[2])))

    for i, run in enumerate(args.direct):
        ft, fv = front(run, X["train"]), front(run, X["val"])
        report("direct", i, [(c, ft[c], fv[c]) for c in fv if c in ft])

    for i, (brun, prun) in enumerate(zip(args.B, partner)):
        fb = {s: front(brun, X[s]) for s in X}
        fp = {s: front(prun, X[s]) for s in X}
        cands = []
        for cb in fb["val"]:
            for cp in fp["val"]:
                preds = []
                for s in ("train", "val"):
                    B = np.clip(fb[s][cb], B_MIN, None)
                    k = np.clip(fp[s][cp], K_MIN, k_max) if pname == "k" else np.clip(fp[s][cp] / B, K_MIN, k_max)
                    preds.append(chen_hardness(k * B, B))
                cands.append((cb + cp, *preds, cb, cp))
        report(f"B+{pname}", i, [c[:3] for c in cands])
        best = min(cands, key=lambda c: mae(hv["val"], c[2]))
        print(f"  seed {i}: best composed pair on val c_B={best[3]} c_{pname}={best[4]} -> {mae(hv['val'], best[2]):.3f}")

    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "ledger/t1_compose.csv", index=False, float_format="%.4f")
    summary = out.groupby(["route", "budget"]).agg(
        seeds=("seed", "nunique"), trainsel_mean=("trainsel_val_mae", "mean"), trainsel_sd=("trainsel_val_mae", "std"),
        valbest_mean=("valbest_val_mae", "mean"))
    print("\nHv val MAE (mean over seeds)\n" + summary.round(3).to_string())


if __name__ == "__main__":
    main()
