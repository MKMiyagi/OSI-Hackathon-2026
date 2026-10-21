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
1. Read wiki/ (incl. wiki/HYPOTHESES.md) and ledger/results.csv. Do not repeat a failed descriptor family.
2. Write descriptors/d_###.py: docstring = physical rationale + expected sign; def compute(df) -> Series.
3. Run >=3 seeds with the descriptor (parallel is fine): uv run python sr/run_pysr.py --descriptors d_### --run-id c###_s0 --seed 0 (then c###_s1 --seed 1, c###_s2 --seed 2, ...).
   Defaults: niterations 22000 (calibrated so one fit is ~8-12 min), maxsize 15, procs 4, 900 s timeout, m_MeltingT and m_SpaceGroupNumber excluded.
4. Run: uv run python eval/score.py --run c###_s0 (and every other seed)  (appends one row per Pareto point to ledger/results.csv)
5. Run: uv run python sr/cycle_summary3.py --cycle ### --descriptor "<name>" --runs c###_s0 c###_s1 c###_s2 --uses d_###
   Reference = the stored 9-seed no-descriptor arm (v008_wo_s0-4, ref_s5-8; same search settings), do NOT re-run it.
   Reference means (sd): c<=9 4.1947 (0.0001, saturated), c<=12 3.9802 (0.0609), c<=15 3.9273 (0.0382).
   Headline score = mean over seeds of best val_mae at complexity <= 12; also report c<=9 and c<=15.
   "Improvement" = headline mean drops >= 0.08 GPa (~1 reference sd) vs the reference mean AND the descriptor appears in a Pareto equation in a majority of seeds.
6. Ask the Codex reviewer ONCE (regular tier, not deep-audit): physical plausibility, unit consistency, leakage risk. Log the verdict in wiki/cycle_log.md, including per-seed numbers (c<=9/12/15) and in how many seeds PySR selected the descriptor.
7. git add -A && git commit -m "cycle ###: <descriptor> c12=<headline mean>" && git push origin agent/overnight-2

## Stop conditions
- Stop after 3 consecutive non-improving cycles (per the rule above), or 10 cycles per night, or 06:00 local.
- Before each cycle, check for a file named STOP in the repo root. If present: finish the current step, commit, write wiki/STOPPED.md, and stop.
- On any error you can't fix in 2 attempts: write wiki/BLOCKED.md and stop. Do not delete data or history.

## ARIS Skill Scope
ARIS skills installed in this project: 86 entries.
Manifest: `.aris/installed-skills.txt` (lists every skill ARIS installed and its upstream target).
For ARIS workflows, prefer the project-local skills under `.claude/skills/` over global skills.
Do not modify or delete files inside any skill that is a symlink (symlinks point into `/Users/mmiyagishima/aris_repo`).
Update with: `bash /Users/mmiyagishima/aris_repo/tools/install_aris.sh`  (re-runnable; reconciles new/removed skills).
<!-- ARIS:END -->
