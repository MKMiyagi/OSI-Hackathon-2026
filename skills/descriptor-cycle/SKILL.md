---
name: descriptor-cycle
description: Run one hypothesis-driven descriptor cycle for the hardness-law project — propose a physically motivated composition descriptor, run PySR with >=3 seeds, score on val against the stored 9-seed reference, get one Codex review, commit to agent/overnight-2. Use when asked to run a cycle, test a descriptor idea, or continue the overnight loop.
---

# Descriptor cycle

One hypothesis per cycle. Never touch eval/score.py, data/splits/, data/test.csv, or ~/quarantine/.

1. Read wiki/ (incl. HYPOTHESES.md) and ledger/results.csv. Do not repeat a failed descriptor family. Check for a STOP file in the repo root first.
2. Write descriptors/d_###.py: docstring = physical rationale + expected sign; `def compute(df) -> pd.Series`.
3. Run >=3 seeds with the descriptor (may run in parallel):
   `uv run python sr/run_pysr.py --descriptors d_### --run-id c###_s0 --seed 0`, then `c###_s1 --seed 1`, `c###_s2 --seed 2`, ...
   Defaults: niterations 22000 (~8-12 min/fit), maxsize 15, procs 4, 900 s timeout, nested unary ops disallowed, m_MeltingT and m_SpaceGroupNumber excluded (seed/exclusions recorded in the run .json).
4. `uv run python eval/score.py --run c###_sK` for every seed (appends to ledger/results.csv).
5. `uv run python sr/cycle_summary3.py --cycle ### --descriptor "<name>" --runs c###_s0 c###_s1 c###_s2 --uses d_###`.
   Reference = stored 9-seed no-descriptor arm (v008_wo_s0-4, ref_s5-8, same settings); do not re-run it. Reference means (sd): c<=9 4.1947 (0.0001), c<=12 3.9802 (0.0609), c<=15 3.9273 (0.0382).
   Headline score = mean over seeds of best val_mae at c<=12; also report c<=9 and c<=15. Improvement = headline mean drops >= 0.08 GPa (~1 reference sd) vs the reference mean AND the descriptor appears in a Pareto equation in a majority of seeds.
6. One regular-tier Codex review call (not deep-audit): physical plausibility, unit consistency, leakage risk. Log the verdict in wiki/cycle_log.md with per-seed numbers (c<=9/12/15) and in how many seeds PySR selected the descriptor.
7. `git add -A && git commit -m "cycle ###: <descriptor> c12=<headline mean>" && git push origin agent/overnight-2`

Stop: 3 consecutive non-improving cycles, 10 cycles, 06:00 local, or a STOP file (write wiki/STOPPED.md). On an unfixable error (2 attempts) write wiki/BLOCKED.md and stop. Do not delete data or history.
