---
name: descriptor-cycle
description: Run one hypothesis-driven descriptor cycle for the hardness-law project — propose a physically motivated composition descriptor, run PySR with two seeds, score on val, get one Codex review, commit to agent/overnight-1. Use when asked to run a cycle, test a descriptor idea, or continue the overnight loop.
---

# Descriptor cycle

One hypothesis per cycle. Never touch eval/score.py, data/splits/, data/test.csv, or ~/quarantine/.

1. Read wiki/ (incl. HYPOTHESES.md) and ledger/results.csv. Do not repeat a failed descriptor family. Check for a STOP file in the repo root first.
2. Write descriptors/d_###.py: docstring = physical rationale + expected sign; `def compute(df) -> pd.Series`.
3. Run TWO seeds (may run in parallel):
   `uv run python sr/run_pysr.py --descriptors d_### --run-id c###_s0 --seed 0` and `... c###_s1 --seed 1`.
   Defaults: niterations 22000 (~8-12 min/fit), maxsize 15, procs 4, 900 s timeout, nested unary ops disallowed, m_MeltingT and m_SpaceGroupNumber excluded (seed/exclusions recorded in the run .json).
4. `uv run python eval/score.py --run c###_s0` and `--run c###_s1` (appends to ledger/results.csv).
5. `uv run python sr/cycle_summary.py --cycle ### --descriptor "<name>" --runs c###_s0 c###_s1`.
   Cycle score = mean of the two best val_mae at complexity <= 9. Improvement = mean drops >= 0.05 GPa vs the best previous cycle (reference: d_003 under this search, t003b_s0/s1).
6. One regular-tier Codex review call (not deep-audit): physical plausibility, unit consistency, leakage risk. Log the verdict in wiki/cycle_log.md with per-seed numbers and whether PySR selected the descriptor.
7. `git add -A && git commit -m "cycle ###: <descriptor> val_mae=<mean>" && git push origin agent/overnight-1`

Stop: 3 consecutive non-improving cycles, 10 cycles, 06:00 local, or a STOP file (write wiki/STOPPED.md). On an unfixable error (2 attempts) write wiki/BLOCKED.md and stop. Do not delete data or history.
