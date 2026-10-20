---
name: descriptor-cycle
description: Run one hypothesis-driven descriptor cycle for the hardness-law project — propose a physically motivated composition descriptor, run PySR, score on val, get a Codex review, commit to agent/overnight-1. Use when asked to run a cycle, test a descriptor idea, or continue the overnight loop.
---

# Descriptor cycle (skeleton — refine Wed afternoon after 2–3 manual cycles)

One hypothesis per cycle. Never touch eval/score.py, data/splits/, data/test.csv, or ~/quarantine/.

1. Read wiki/ and ledger/results.csv. Do not repeat a failed descriptor family.
2. Write descriptors/d_###.py: docstring = physical rationale + expected sign; `def compute(df) -> pd.Series`.
3. Run: `uv run python sr/run_pysr.py --descriptors d_### ...` (writes Pareto CSV to ledger/runs/)
4. Run: `uv run python eval/score.py --run <id>` (appends one row per Pareto point to ledger/results.csv)
5. Ask the Codex reviewer: physical plausibility, unit consistency, leakage risk. Log the verdict in wiki/.
6. `git add -A && git commit -m "cycle ###: <descriptor> val_mae=<x>" && git push origin agent/overnight-1`

Stop: 12 cycles/night, 3 consecutive non-improving cycles at the knee, or 06:00 local. On an unfixable error write wiki/BLOCKED.md and stop.
