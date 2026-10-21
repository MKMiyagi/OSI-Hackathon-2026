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

## Train-median constant comparator (2026-10-21)
`eval/score.py` has no median path (only a one-time train-mean `baseline_mean` row, 5.2589 val MAE) and may not be edited, so no ledger row was added. Documented here instead, computed directly (scripts/data_audit.py): train median target = 5.7499 GPa; **val MAE of that constant = 5.0442 GPa** (train-mean constant 7.2280 -> 5.2589). Comparator for all development-set claims: best SR equations (3.77-4.19) improve on it by roughly 0.85-1.27 GPa. Development-set (val, reused) numbers.

## Secondary metrics (pre-registered Wed 15:30)
Written and committed **before** any of these metrics was computed (eval/metrics_extra.py did not exist at commit time). Exactly these, no others will be added after seeing results. All are computed on data/splits/val.csv (a reused development set; see wiki/RESEARCH_REVIEW_3_VERDICT.md), for every Pareto equation of a run, plus the Tehrani-style SVR baseline (eval/tehrani_baseline.py) and the train-median constant (5.7499 GPa). Target = `hv_chen`. Nothing here replaces or re-ranks the headline; score.py and the splits are untouched.

1. **MAE (GPa) — frozen headline.** Mean |y - yhat| in GPa, as computed by eval/score.py; the only metric used for "improvement" in CLAUDE.md. Rationale: already adopted; in the target's own units; every other metric below is reported next to it, not instead of it.
2. **MASE vs train-median constant.** val MAE of the model / val MAE of the train-median constant (5.0442 GPa). Rationale: scale-free; says whether the model beats the trivial predictor (<1 beats it), which is the right floor for a target with a skewed spread.
3. **MASE vs the SVR baseline (skill score).** val MAE of the model / val MAE of the SVR baseline; 1.0 = same as the black box, <1 better, >1 worse. Rationale: the comparison the project is actually about, formula vs composition-only black box, without reference to units. The "fraction of the constant-to-black-box gap closed", (MAE_const - MAE_model)/(MAE_const - MAE_SVR), is a deterministic rewriting of metrics 1-3, not an additional metric.
4. **MAE of log(Hv+3).** Mean |log(y+3) - log(yhat+3)|. Chen's form Hv = 2(k^2 G)^0.585 - 3 is bounded below by -3, so y+3 > 0 by construction. Predictions yhat <= -3 are counted as **failures**: the failure count is reported beside the metric and the log-MAE is taken over the non-failure rows only; any equation with failures is flagged. Rationale: relative error on the quantity Chen's form actually makes positive, so errors on soft materials are not drowned out by errors on superhard ones.
5. **Stratified MAE** in bins of the *true* value: <5 / 5-15 / 15-25 / >25 GPa (intervals [lo, hi), the top bin is >=25), with per-bin n. Rationale: a single MAE can hide a model that is good on the bulk and fails in the superhard tail, which is the region of scientific interest.
6. **Spearman rho and precision-at-top-10%.** rho = Spearman rank correlation of yhat with y; precision-at-top-10% = fraction of the ceil(0.1 n) rows with the highest yhat that are also in the true top ceil(0.1 n). Rationale: a screening use only needs the right ranking and the right top decile, which MAE does not measure. Ties in yhat (constants) give rho = NaN and are reported as such, not coerced to 0.

**Considered and rejected: MAPE and MRAE.** Both divide by the target (MAPE) or by a baseline's absolute error (MRAE); hv_chen has negative and near-zero values, so the denominators vanish or flip sign and the metrics are unstable or undefined. MASE (scaled by a fixed aggregate MAE) and log(Hv+3) are used instead.
