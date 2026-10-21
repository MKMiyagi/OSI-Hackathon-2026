"""THE one-time test-set evaluation (T1, by hand, Thursday). Agents must never run this against the test file.

Usage:
  uv run python eval/test_once.py --rehearse-on-val <predictors>                          # rehearsal, writes nothing
  uv run python eval/test_once.py --test ~/quarantine/test.csv <predictors> --confirm-one-shot   # the one shot

Predictors (fix the list BEFORE running; it is recorded in the output with the git commit):
  --formula NAME=EXPR           direct Hv formula (ledger variable names: m_* Magpie means, d_### descriptors)
  --compose NAME=B_EXPR|K_EXPR  Hv = Chen(k*B, B) with the guards of eval/compose_hv.py
  --svr                         Magpie SVR straight on hv_chen, refit on train (eval/tehrani_baseline.py, full grid)
  the train-median constant is always included.
Metrics per predictor: MAE vs hv_chen (GPa) on all rows, on rows with hv_chen >= 20 GPa, and the number of rows where
the prediction is undefined (non-finite; reported, never imputed). Features come from sr/run_pysr.py:featurize and
expressions from eval/score.py:eval_equation, exactly as for val.
Safeguards: the test file must match data/test.sha256; --confirm-one-shot is required; it refuses to run if any
ledger/test_once_*.csv exists. Rehearsal runs the identical pipeline on data/splits/val.csv and writes no file.
"""
import argparse
import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from eval.external_zhang import (  # noqa: E402
    build_features, expressions, parse_specs, predict_spec, svr_magpie, used_symbols)
from sr.run_pysr import DERIVED_TARGETS  # noqa: E402

TAIL = 20.0


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--test", help="path to the quarantined test.csv")
    src.add_argument("--rehearse-on-val", action="store_true")
    ap.add_argument("--formula", action="append", default=[])
    ap.add_argument("--compose", action="append", default=[])
    ap.add_argument("--svr", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--confirm-one-shot", action="store_true")
    args = ap.parse_args()

    if args.test:
        if not args.confirm_one_shot:
            raise SystemExit("this is the one-shot test evaluation; add --confirm-one-shot (or use --rehearse-on-val)")
        prev = sorted((ROOT / "ledger").glob("test_once_*.csv"))
        if prev:
            raise SystemExit(f"refusing: the test set was already evaluated ({prev[0].relative_to(ROOT)})")
        path = Path(args.test).expanduser()
        if hashlib.sha256(path.read_bytes()).hexdigest() != (ROOT / "data/test.sha256").read_text().strip():
            raise SystemExit("test file does not match data/test.sha256")
    else:
        path = ROOT / "data/splits/val.csv"
    df = pd.read_csv(path)
    y = df["hv_chen"].astype(float).values
    tail = y >= TAIL

    specs = parse_specs(args.formula, "formula") + parse_specs(args.compose, "compose")
    from sr.run_pysr import featurize  # noqa: E402  (for the column list)
    base_cols = featurize(pd.DataFrame({"formula": ["TiC"]}), [])[1].columns
    descs = sorted({s for sp in specs for e in expressions(sp) for s in used_symbols(e, list(base_cols) + [
        f"d_{i:03d}" for i in range(1000)]) if s.startswith("d_")})
    X, failures = build_features(list(df.formula), descs)
    tr = pd.read_csv(ROOT / "data/splits/train.csv")
    k_max = float(DERIVED_TARGETS["pugh_k"](tr).max())

    preds = {"train_median_constant": np.full(len(df), tr.hv_chen.median())}
    kinds = {"train_median_constant": "constant"}
    for sp in specs:
        preds[sp[0]] = np.asarray(predict_spec(sp, X, k_max), dtype=float)
        kinds[sp[0]] = " | ".join(expressions(sp))
    if args.svr:
        preds["svr_magpie"], kinds["svr_magpie"] = svr_magpie(list(df.formula), False, args.jobs)

    rows = []
    for name, p in preds.items():
        ok = np.isfinite(p)
        rows.append(dict(predictor=name, n=int(ok.sum()), n_undefined=int((~ok).sum()),
                         mae=float(np.mean(np.abs(p[ok] - y[ok]))) if ok.any() else np.nan,
                         n_tail=int((ok & tail).sum()),
                         mae_tail=float(np.mean(np.abs(p[ok & tail] - y[ok & tail]))) if (ok & tail).any() else np.nan,
                         expression=kinds[name]))
    res = pd.DataFrame(rows)
    label = "TEST (one shot)" if args.test else "REHEARSAL on val (development set; nothing written)"
    print(f"\n{label}: {len(df)} rows, {int(tail.sum())} with hv_chen >= {TAIL:g} GPa")
    if failures:
        print(f"descriptor failures on {len(failures)} compositions (predictions undefined there)")
    print(res.drop(columns="expression").round(3).to_string(index=False))
    if args.test:
        ts = datetime.now(timezone.utc)
        res.insert(0, "commit", git("rev-parse", "HEAD"))
        res.insert(0, "timestamp", ts.isoformat(timespec="seconds"))
        out = ROOT / f"ledger/test_once_{ts.strftime('%Y%m%dT%H%M%SZ')}.csv"
        res.to_csv(out, index=False, float_format="%.4f")
        print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
