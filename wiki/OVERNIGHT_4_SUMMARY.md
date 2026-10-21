# Overnight 4 summary (branch agent/overnight-2, 2026-10-21 15:00-18:15 local)

Queue run: cycles 020-025 and 027 (7 of 8 queue items; 18 completed fits + 1 re-run, 1 crashed attempt). Cycle 026 skipped by rule (neither bond-count descriptor was selected in any seed). Stopped on the 3-consecutive-non-improving rule (023, 024, 025), at ~18:15, well before 06:00; no STOP file. Test set and ~/quarantine never touched; `eval/score.py` was not run on B/G/pugh_k runs. All numbers are exploratory: val is a reused development set, target is the DFT-derived Chen proxy `hv_chen`. Search settings: defaults (L2, niter 22000, maxsize 15, procs 4, 900 s, MeltingT/SpaceGroup hidden), `deterministic=False` (seeds are labels). Two fits at a time.
Failures: Julia segfault on c021_s2 attempt 1 (log `ledger/logs/c021_s2.attempt1_segfault.log`), re-run once with identical settings, succeeded. Not logged as BLOCKED.
Missing inputs: wiki/NESTED_CV_D023.md named in the brief does not exist on any branch; wiki/HYPOTHESES_4.md existed only on `m/nested-cv-d023` (copied in). d_019/d_020 were implemented tonight (descriptors/d_019.py, d_020.py, _bondcount.py) per HYPOTHESES_4 H4.1/H4.2 with the declared conventions.

## Per-cycle table (mean over 3 seeds; reference 9-seed means c<=9 4.1947, c<=12 3.9802 (sd 0.0609), c<=15 3.9273)
| cycle | descriptors | mean c<=9 | mean c<=12 | mean c<=15 | c<=12 vs ref | selected | rule flag | verdict |
|---|---|---|---|---|---|---|---|---|
| 020 | d_023 | 3.6939 | 3.6838 | 3.6514 | -0.296 (~4.9 sd) | 3/3, every Pareto point from c2 | improvement | **the lead holds under the adopted protocol** |
| 021 | d_023 + d_027 | 3.6939 | 3.6225 | 3.6169 | -0.358 | d_027 3/3, only at c>=10 | improvement (vs ref) | gain over d_023 alone -0.061, paired bootstrap 95% CI [-0.208, +0.085] includes 0: not established |
| 022 | d_023 + d_008 | 3.6939 | 3.6939 | 3.6734 | -0.286 | d_008 3/3 from c9 | improvement (vs ref) | no added value: +0.010 (c12) / +0.022 (c15) vs d_023 alone; d_008 c9 form loses to the d_008-free c8 |
| 023 | d_023 + d_025 | 3.6939 | 3.6839 | 3.6453 | -0.296 | 0/3 | no | size mismatch adds nothing |
| 024 | d_019 anion/cation (alone) | 4.1947 | 4.0170 | 3.8731 | +0.037 | 0/3 | no | unsupported (see flaw below) |
| 025 | d_020 bonds/atom (alone) | 4.1946 | 4.0271 | 3.9436 | +0.047 | 0/3 | no | unsupported |
| 026 | d_023 + best bond-count | - | - | - | - | - | - | skipped by rule |
| 027 | d_023, `--units --dimensionless-constants` | 3.6972 | 3.6972 | 3.6263 | not comparable | 3/3 | separate | c9 form is d_023 x dimensionless; costs +0.003/+0.013 at c<=9/12, -0.025 at c<=15 vs cycle 020 |
Per-seed numbers, equations and Codex verdicts: wiki/cycle_log.md. Scores: ledger/cycle_scores3.csv (cycles 020-025; 027 deliberately not added), ledger/results.csv (027 rows noted "units-constrained").

## Findings
- **d_023 (cohesive-energy density) is the first descriptor to move the reference materially.** It lowers c<=9 by 0.50 GPa (the saturated no-descriptor c9 equation is displaced in all 3 seeds), c<=12 by 0.30 and c<=15 by 0.28, with seed-to-seed spread ~0.00-0.01 at c<=12. Seeds converge to the same fronts, so this shows search stability, not 3 independent confirmations. Best compact form (c8): `d_023/(m_NdValence + sqrt(m_Column)) + m_NpUnfilled`, val 3.6939; the one-feature c5 `d_023/(m_NdValence + 2.46)` (3.9077) already beats the c<=12 reference.
- **Caveats on d_023 (reviewer + record):** (i) not val-blind: T1 screened it on train and scored a 2-parameter fit on val before tonight; (ii) the c8 winner adds a count to a GPa quantity (implicit 1-GPa coefficient); (iii) `sqrt(m_Column)` is arbitrary; (iv) everything is a fit to Chen's output from DFT B,G, not measured hardness; (v) composition means cannot separate polymorphs. The unit-constrained arm (027) shows the gain survives dimensional consistency (c9 3.6972, `d_023/1.367/(chi + NdValence/NsValence)`). Constraint is a soft penalty, and m_GSbandgap/m_GSvolume_pa also has pressure dimensions, so "d_023 is the only source of GPa" is not guaranteed.
- **Interactions (021-023): none established.** d_027 gives 3.6225 at c11 but the gain over d_023 alone (-0.061, <1 ref sd) has a bootstrap CI over val families containing zero; d_008 and d_025 add nothing. d_008's earlier c8 effect is subsumed by d_023.
- **Bond-count family (024-025): negative screens.** Neither d_019 nor d_020 selected in any seed, c<=12 worse than reference by 0.04-0.05. d_019 flaw: the declared chi>=2.0 anion cut puts Mo (2.16), W (2.36) and late TMs in the anion set (Mo2C -> 10, BN/B4C/B -> 10), opposite to the HYPOTHESES_4 rationale; followed as declared, not retuned. d_020 correlates only 0.45 with m_NValence, so non-selection is not explained by redundancy. Both ran on reused val, contrary to the nested-CV-only plan in HYPOTHESES_4; negative exploratory screens, not refutations.
- Rule bookkeeping: 021 and 022 are formal "improvements" vs the no-descriptor reference but their gain is d_023's; counting them as such, the non-improving streak at the end is exactly 3 (023-025) either way.

## Recommended next steps
1. Freeze the candidate list before the one-shot test run (eval/test_once.py, rehearsed on val): at minimum #1 (c8), #4 (c9 unit-consistent) and #8 (c5) from CANDIDATE_FORMULAS "Overnight 4 additions"; do not add d_027 forms on the strength of the 0.06 gain.
2. Test d_023 in the nested grouped-CV protocol (eval/nested_cv.py) as a fixed extra arm, since val is not independent of the T1 screen; also compare d_023 vs d_023 with `m_NpUnfilled` dropped, to price the unit-inconsistent term.
3. Try L1 loss / longer search only for d_023 arms if anything; the fronts here are already converged across seeds.
4. If bond-count ideas are revisited, fix the anion rule first (e.g. a metal list or Pauling cut ~2.5) as a new pre-registered descriptor, not a retune of d_019.
5. Create wiki/NESTED_CV_D023.md or correct the reference to it.
Files: wiki/cycle_log.md, wiki/CANDIDATE_FORMULAS.md, wiki/HYPOTHESES_4.md, ledger/results.csv, ledger/cycle_scores3.csv, ledger/logs/c02*_s*.out, descriptors/d_019.py, d_020.py, _bondcount.py.
