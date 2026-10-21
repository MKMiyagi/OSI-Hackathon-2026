# Overnight 3 summary (branch agent/overnight-1, 2026-10-20/21)

Scripted plan completed: Phases 1-5, all 8 queue cycles (012-019, numbered in queue order a-h; cycle 013 was scored last because of a crash retry). 46 PySR fits (10 d_008 ablation, 4 extra reference, 1 retry, 2 long, 24 queue + 1 retry), no STOP file, finished ~02:50 local (limit 06:00). Test set untouched. Target still hv_chen (Chen on DFT B,G, provisional); all val numbers are exploratory (val was used to choose descriptors/equations).
Search settings as in overnight 2 (niter 22000, maxsize 15, procs 4, 900 s, MeltingT/SpaceGroup hidden) except Phase 3 (niter 120000, 3600 s). `deterministic=False`, so seeds are labels, not reproducible streams.
Failures: Julia segfaults on 2 fits (v008_wo_s2, c013_s1; logs kept as `*.attempt1_segfault.log`), each re-run once with identical settings and succeeded. Not logged as BLOCKED (recovered). The "3 non-improving" stop rule was suspended as instructed; the 0.05 improvement flag is not used below.

## Per-phase findings
**Phase 1 — d_008 paired ablation (5 seeds; wiki/D008_VALIDATION.md).** With d_008: best c<=9 mean 4.0959 +- 0.090; without: 4.1947 +- 0.0001; mean difference -0.099 (unpaired Welch 95% CI [-0.21, +0.01]). c<=12: +0.030 (CI [-0.06, +0.12]); c<=15: -0.028 (CI [-0.07, +0.02]). d_008 selected in 3/5 seeds, always at c8, always the same equation `NUnfilled + 381.7/exp(Row + d_008)` (val 4.0300). Verdict: recurrent compact candidate, no established improvement; the benefit exists only at c<=9 and vanishes by c12. Reviewer asked to drop the "paired" framing (seeds not matched) and soften claims; done.
**Phase 2 — is the c<=9 metric broken? Yes (wiki/DECISIONS.md "Metric").** 9 no-descriptor seeds: c<=9 best val_mae 4.1946-4.1949 (sd 0.0001); 9/9 are the same function `k*MendeleevNumber/(NValence*GSvolume_pa) + NUnfilled` (k~8.48), always c9. Saturated. c<=12 is not (3.911/3.977/4.052, mean 3.980, sd 0.061). Replacement proposed (>=5-seed same-settings no-descriptor arm, report c<=9/12/15, use c<=12 as headline, require selection in a majority of seeds); CLAUDE.md untouched.
**Phase 3 — longer search (niter 120000, one seed per arm).** Both fits ran to ~100% iterations (3604 s / 3483 s). With d_008: c<=9 4.0300 (same c8 equation, not selected earlier), c<=12 4.0300, c<=15 3.8923. Without: 4.1946 / 3.9771 / 3.8923. Search depth changed nothing: the 22k search was already converged for seed 0; d_008's effect is a stable optimum, not a shortfall. n=1 per arm.
**Phase 4 — EN-family queue (3 seeds/cycle).** See table. Summary: nothing improved c<=12 on average (all cycle means 3.91-4.03 vs reference 3.980 +- 0.061/sqrt(9)); only cycles containing d_008 (015, 017) or a d_008-derived form (019) moved c<=9, and by no more than d_008 alone.

## Per-cycle table (mean over 3 seeds; paired = vs v008_wo s0-2 same seed labels; reference 9-seed means c<=9 4.1947, c<=12 3.9802)
| cycle | descriptor | mean c<=9 | mean c<=12 | paired c<=9 / c<=12 | selected (seeds; min complexity) | verdict |
|---|---|---|---|---|---|---|
| 012 | d_014 sum x(chi_max-chi) | 4.1947 | 3.9320 | -0.000 / -0.048 | 2/3; c8 (val 4.32, worse than baseline) | noise; c12 gain is the Magpie ceiling |
| 013 | d_015 Pauling ionic character | 4.1946 | 4.0331 | -0.000 / +0.053 | 2/3; c8 (val 4.28, worse) | no gain |
| 014 | d_016 Allen-scale EN range | 4.1946 | 3.9114 | -0.000 / -0.069 | 1/3; c10 | does not reproduce d_008; c12 = Magpie ceiling |
| 015 | d_008 + d_007 | 4.0849 | 3.9997 | -0.110 / +0.020 | d_008 2/3 at c8; d_007 only at c11+ (one seed 3.9172) | = d_008 alone; no interaction shown |
| 016 | d_013 alone | 4.1988 | 4.0020 | +0.004 / +0.022 | 0/3 | no signal |
| 017 | d_008 + d_013 | 4.0890 | 3.9905 | -0.106 / +0.010 | d_008 2/3 at c8; d_013 once at c14 (unit-inconsistent) | = d_008 alone |
| 018 | d_017 anion-like EN content | 4.1514 | 3.9790 | -0.043 / -0.001 | 3/3; c9-10; sign NEGATIVE vs pre-registered + | selected but wrong sign; seed-0 c12 3.7722 is fragile |
| 019 | d_018 (EN range)^2 | 4.1128 | 3.9815 | -0.082 / +0.001 | 3/3; c9 | selected; seed 2 c9 4.0025 (best compact so far) but seeds 0,1 4.15/4.18 |
Per-seed numbers and reviewer verdicts: wiki/cycle_log.md; scores: ledger/cycle_scores3.csv.

## Signal vs noise
- Most credible: electronegativity spread lowers Hv in a stable compact form with row number, `NUnfilled + C*exp(-(Row + chi_range))`; recurs in about 12 runs (ablation, long, joint cycles). But it only displaces the Magpie c9 equation; it raises no ceiling at c12-15, and the Allen-scale replacement (d_016), the ionic-character transform (d_015) and the mean-deviation form (d_014) do not reproduce it, so it is sensitive to the exact functional form and scale (the Allen table is hand-entered and unverified in full).
- d_018 (squared range) and d_017 (anion-like EN content) are selected in 3/3 seeds, but their c<=12 means equal the reference; their best single seeds (4.0025 at c9; 3.7722 at c12) are seed-specific, and the 3.7722 is driven by ~10 val rows. Treat as hypotheses needing out-of-val checks, not results. d_017's fitted sign is opposite to the hypothesis.
- Noise: d_007 interaction, d_013 (both alone and with d_008), d_014, d_015, d_016. d_013 and d_007 are now retired for this search design.
- Magpie-only floor: c12 3.911 (38 runs) and c15 3.892 are the real baselines; every c<=12 "gain" below ~0.1 GPa is inside seed sd (0.06-0.09).

## Recommended next steps
1. Adopt the proposed metric (>=5-seed no-descriptor arm, c<=12 headline with c<=9/15 reported, selection in majority of seeds) before further cycles; seeds-with-descriptor n=5 resolves only ~0.1 GPa.
2. Test d_017/d_018 and d_008 on chemistry-grouped resamples within train+val (leave-family-out), not just val; the reviewer asked for GSbandgap ablation and per-row jackknife for the 3.7722 equation.
3. Replace the hand-typed Allen table with a verified source before any claim about scale-sensitivity; retest d_016 only then.
4. Decide Wednesday whether the target stays Chen-derived; every formula here is a fit to Chen's output.
5. Do not run more near-duplicates of d_008 (range transforms); next hypothesis family should add information not buildable from means+extrema of chi (e.g. stoichiometry-aware bond-count features, which the reviewers repeatedly flagged as missing).
Files: wiki/D008_VALIDATION.md, wiki/DECISIONS.md (Metric), wiki/HYPOTHESES_3.md, wiki/CANDIDATE_FORMULAS.md, ledger/cycle_scores3.csv, sr/ablation_report.py, sr/cycle_summary3.py, scripts/run_queue.sh.
