"""Score a cycle run off the agent machine under the exact CLAUDE.md rule, without touching ledger/results.csv.

Usage: uv run python scripts/t1_cycle_score.py --cycle 020 --descriptor "d_023 cohesive-energy density" \
           --runs t1_c020_s0 t1_c020_s1 t1_c020_s2 --uses d_023

ledger/results.csv is appended only on the agent machine. This builds the rows eval/score.py would append (val MAE
per Pareto equation, same featurize and eval_equation) in memory, adds them to the stored ledger (which holds the
9-seed reference), and applies sr/cycle_summary3.py's own functions. Also reports iterations actually completed
(from ledger/logs) and descriptor NaN coverage. Writes ledger/t1_cycle_scores.csv.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from eval.score import eval_equation  # noqa: E402
from sr.cycle_summary3 import HEADLINE, WINDOWS, best, is_improvement, reference_stats, selection  # noqa: E402
from sr.run_pysr import featurize  # noqa: E402

OUT = ROOT / "ledger/t1_cycle_scores.csv"


def scored_rows(run, val):
    meta = json.loads((ROOT / f"ledger/runs/{run}.json").read_text())
    df, X = featurize(val, meta["descriptors"])
    y = df[meta["target"]].astype(float).values
    nan = {d: int(X[d].isna().sum()) for d in meta["descriptors"]}
    rows = []
    for _, r in pd.read_csv(ROOT / f"ledger/runs/{run}.csv").iterrows():
        pred = eval_equation(r["equation"], X)
        if not np.isfinite(pred).all():
            raise SystemExit(f"{run}: non-finite val predictions at complexity {r['complexity']} (score.py would abort)")
        rows.append(dict(run_id=run, complexity=int(r["complexity"]), val_mae=float(np.mean(np.abs(y - pred))),
                         formula=r["equation"], descriptor_set="+".join(meta["descriptors"]) or "magpie_only"))
    log = ROOT / f"ledger/logs/{run}.log"
    hits = re.findall(r"Progress: (\d+) / (\d+)", log.read_text()) if log.exists() else []
    return rows, meta, nan, (f"{hits[-1][0]}/{hits[-1][1]}" if hits else "?")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", required=True)
    ap.add_argument("--descriptor", default="")
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--uses", nargs="*", default=[])
    a = ap.parse_args()
    if len(a.runs) < 3:
        raise SystemExit("need >=3 seeds")

    val = pd.read_csv(ROOT / "data/splits/val.csv")
    new = []
    for run in a.runs:
        rows, meta, nan, iters = scored_rows(run, val)
        new += rows
        settings = {k: meta.get(k) for k in ("niterations", "timeout_in_seconds", "loss", "units", "fit_seconds")}
        print(f"{run}: iterations {iters}, NaN rows in val {nan}, {settings}")
    res = pd.concat([pd.read_csv(ROOT / "ledger/results.csv"), pd.DataFrame(new)], ignore_index=True)

    ref = reference_stats(res)
    per = {w: [best(res, r, w) for r in a.runs] for w in WINDOWS}
    mean = {w: float(np.mean(per[w])) for w in WINDOWS}
    sel, minc = selection(res, a.runs, a.uses)
    imp = is_improvement(mean[HEADLINE], ref[HEADLINE][0], sum(sel), len(sel))
    out = {"cycle": a.cycle, "descriptor": a.descriptor, "runs": "+".join(a.runs)}
    for w in WINDOWS:
        out[f"best_c{w}_per_seed"] = "/".join(f"{x:.4f}" for x in per[w])
        out[f"mean_c{w}"] = round(mean[w], 4)
        out[f"ref_mean_c{w}"] = round(ref[w][0], 4)
        out[f"ref_sd_c{w}"] = round(ref[w][1], 4)
        out[f"diff_c{w}_vs_ref"] = round(mean[w] - ref[w][0], 4)
    out.update(selected=f"{sum(sel)}/{len(sel)}", min_complexity_used="/".join(map(str, minc)), improvement=imp)
    row = pd.DataFrame([out])
    row.to_csv(OUT, mode="a", header=not OUT.exists(), index=False)
    for k, v in out.items():
        print(f"  {k}: {v}")
    print(f"\nheadline c<={HEADLINE}: {mean[HEADLINE]:.4f} vs reference {ref[HEADLINE][0]:.4f} "
          f"(sd {ref[HEADLINE][1]:.4f}); improvement = {imp}")


if __name__ == "__main__":
    main()
