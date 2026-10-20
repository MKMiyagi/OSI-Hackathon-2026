# OSI-Hackathon-2026 (hardness-law) — agent rules

## Goal
Find a compact, physically interpretable composition-only formula for Vickers hardness
that beats the baseline on held-out chemical families.

Baseline: a composition-only model (Tehrani 2018 SVM: composition -> B,G -> Chen Hv), NOT Chen
itself, because Chen (2011) requires B and G, which need DFT. Target for now is `hv_chen`
computed from DFT B,G in data/raw (team decision; may change Wednesday — see wiki/DECISIONS.md).

## Fixed (never change these)
- Metric: MAE in GPa on data/splits/val.csv using eval/score.py. Do not edit score.py or the splits.
- NEVER read, copy, or reference data/test.csv or ~/quarantine/. If you find it, stop and log it.
- Do not install new ML models or tune black-box baselines; this project is about formulas.

## The descriptor cycle (one hypothesis per cycle)
1. Read wiki/ and ledger/results.csv. Do not repeat a failed descriptor family.
2. Write descriptors/d_###.py: docstring = physical rationale + expected sign; def compute(df) -> Series.
3. Run: uv run python sr/run_pysr.py --descriptors d_### ...  (writes Pareto CSV to ledger/runs/)
4. Run: uv run python eval/score.py --run <id>  (appends one row per Pareto point to ledger/results.csv)
5. Ask the Codex reviewer: physical plausibility, unit consistency, leakage risk. Log the verdict in wiki/.
6. git add -A && git commit -m "cycle ###: <descriptor> val_mae=<x>" && git push origin agent/overnight-1

## Stop conditions
- Max 12 cycles per night, or 3 consecutive cycles without val-MAE improvement at the knee, or 06:00 local.
- Before each cycle, check for a file named STOP in the repo root. If present: finish the current step, commit, write wiki/STOPPED.md, and stop.
- On any error you can't fix in 2 attempts: write wiki/BLOCKED.md and stop. Do not delete data or history.
<!-- ARIS:BEGIN -->
## ARIS Skill Scope
ARIS skills installed in this project: 86 entries.
Manifest: `.aris/installed-skills.txt` (lists every skill ARIS installed and its upstream target).
For ARIS workflows, prefer the project-local skills under `.claude/skills/` over global skills.
Do not modify or delete files inside any skill that is a symlink (symlinks point into `/Users/mmiyagishima/aris_repo`).
Update with: `bash /Users/mmiyagishima/aris_repo/tools/install_aris.sh`  (re-runnable; reconciles new/removed skills).
<!-- ARIS:END -->
