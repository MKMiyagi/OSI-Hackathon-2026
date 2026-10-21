# Decisions

## Target and baseline (2026-10-20) — PROVISIONAL, may change Wednesday
- Baseline is composition-only (Tehrani 2018 SVM: composition -> B,G -> Chen Hv), not Chen, since Chen needs DFT B,G.
- Target = `hv_chen` = Chen(2011) applied to DFT B,G from data/raw/brgoch_superhard_training.csv.
- Caveat (see codex_review_run_pysr.md): labels are Chen-derived, so any formula is fit to Chen's output, not measured hardness. Revisit Wednesday.
- Splits: 70/15/15, seed 42, grouped by sorted element set. Test lives in ~/quarantine/test.csv (sha256 in data/test.sha256), never read by agents.

## Metric (overnight 3, 2026-10-21) — ADOPTED Wed morning (2026-10-21), see CLAUDE.md
Adopted rule: each cycle = >=3 seeds vs the stored 9-seed no-descriptor reference; headline = mean best val_mae at c<=12 (c<=9 and c<=15 reported); improvement = headline mean drops >=0.08 GPa AND descriptor selected in a majority of seeds. Branch overnight-2. The proposal text below is kept as the original rationale.
Finding: the c<=9 knee score is saturated. Across 9 no-descriptor reference seeds (v008_wo_s0..s4, ref_s5..s8) the best c<=9 val_mae is 4.1946-4.1949 (mean 4.1947, sd 0.0001) and ALL 9 (not just >=7) are the same function up to the fitted constant: `k * m_MendeleevNumber / (m_NValence * m_GSvolume_pa) + m_NUnfilled`, k ~ 8.49, always at complexity 9 (algebraically equivalent forms). The c<=9 score therefore only moves when a descriptor displaces this single equation, so "non-improving" mostly means "not selected below c10". At c<=12 the reference is no longer saturated (mean 3.980, sd 0.061, values 3.911/3.977/4.052).
Proposal (not adopted): (1) score a descriptor by the paired difference vs a same-settings no-descriptor arm over >=5 seeds, at c<=12 and c<=15 as well as c<=9; (2) use best c<=12 (or the mean of c<=9/12/15) as the headline since c<=12 has seed variance to discriminate on; (3) require the descriptor to appear in a Pareto equation in a majority of seeds. Rough detection limit: with sd ~0.06-0.09 at c<=12, 5 paired seeds resolve only ~0.1 GPa effects.

## Wording and framing corrections (round-3 review, 2026-10-21)
- "Magpie ceiling" is replaced everywhere by "best observed under this search configuration" (README, summaries); it was never a bound.
- Framing: compact composition-only emulator of the DFT-derived Chen proxy, compared against the Tehrani-style composition -> B,G -> Chen pipeline; "beats Chen" is incoherent because labels are Chen's output.
- All val MAEs are development-set (val, reused) numbers. Per-cycle scoring uses sr/cycle_summary3.py (9 reference runs, c<=9/12/15, headline c<=12, >=0.08 drop AND majority selection); output file ledger/cycle_scores4.csv.
