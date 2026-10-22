# Nested grouped CV with d_023 (overnight 5, cycle 033; not scored against the 9-seed reference)

Generated from `ledger/nested_cv/ncv_d023.csv` by `eval/nested_cv.py --report-d023 ncv_d023` (tables) plus hand-written analysis. Protocol is the frozen one in `eval/nested_cv.py` / wiki/NESTED_CV.md: train+val pooled (2120 rows, 1406 element-set groups, test file never read), 5 element-set-grouped outer folds (seed 42), per-fold grouped 80/20 inner split, ONE PySR fit per (fold, arm) with the default search (niterations 22000, maxsize 15, procs 4, 900 s, seed 0, L2, MeltingT/SpaceGroup hidden), equation chosen per window (c<=9/12/15) by inner-validation MAE only, scored once on the outer-test fold. Wall time: two fit processes, 15 PySR fits of 700-790 s each (about 1h15), SVR assembly 81 s.
Arms (declared in wiki/cycle_log.md before any fit): `median_const`; `svr_baseline` = eval/tehrani_baseline.py's Magpie-132 SVR (log B, log G, grouped-5-fold-CV grid over C/gamma/epsilon, then Chen) fitted on ALL outer-training rows of each fold; `svr_fitidx` = the same fitted on the inner-train rows only (the 80% the PySR arms fit on; extra arm to price that difference, 0.14 GPa); `magpie` (22 Magpie means); `magpie+d_023`; `magpie+d_023+d_031` (d_031 = metal-atom fraction, the only new overnight-5 descriptor selected in a majority of seeds). d_028-d_030 not available (coverage), d_007 never selected.
All numbers are outer-fold test MAE in GPa on the DFT-derived Chen proxy `hv_chen`; sd across folds is fold heterogeneity, not optimizer or selection uncertainty. A single search seed per fit: PySR is not deterministic, so each cell is one draw.

## Summary (mean over the 5 outer folds)
| arm | c<=9 | c<=12 | c<=15 | gap closed at c<=12 | MASE vs SVR at c<=12 | pooled tail (>=20 GPa, n=103) at c<=12 |
|---|---|---|---|---|---|---|
| median_const | 4.889 | 4.889 | 4.889 | 0% | - | 21.97 |
| svr_baseline (all outer-train rows) | 2.810 | 2.810 | 2.810 | 100% | 1.00 | 8.74 |
| svr_fitidx (inner-train rows only) | 2.952 | 2.952 | 2.952 | 93% | - | 9.06 |
| magpie | 4.039 | 3.787 | 3.767 | 53% | 1.355 | 12.84 |
| magpie+d_023 | 3.618 | 3.608 | 3.493 | 62% | 1.291 | 10.07 |
| magpie+d_023+d_031 | 3.618 | 3.601 | 3.518 | 62% | 1.289 | 10.05 |
Gap closed = (const - arm)/(const - svr_baseline) on the fold-mean MAEs; MASE = mean over folds of arm MAE / SVR MAE.

Paired per-fold differences (arm minus magpie, GPa; folds 0-4): d_023, c<=9: -0.276, -0.543, -0.432, -0.430, -0.424 (mean -0.421); c<=12: -0.242, -0.070, -0.193, -0.222, -0.165 (mean -0.178, sd 0.067); c<=15: -0.352, -0.286, -0.262, -0.156, -0.315 (mean -0.274). d_023 is better than Magpie-only in 5/5 folds in every window. Adding d_031 on top of d_023: c<=9 -0.001, c<=12 -0.007 (per fold 0, -0.023, -0.040, +0.028, 0), c<=15 +0.025 (0, +0.140, +0.032, -0.045, 0): no effect.
d_023 selection: in 5/5 folds at every window, complexity c<=9: 8, 9, 8, 8, 8 (the same c8 form `d_023/(sqrt(Column) + NdValence) + NpUnfilled` in 4 of 5 folds); c<=12: 11, 9, 12, 12, 8; c<=15: 15, 13, 14, 12, 13. d_031 (in the d_023+d_031 arm) was selected in 3/5 folds at c<=12 and c<=15 (folds 1-3; 1/5 at c<=9), with a worse c<=15 mean than the d_023-only arm.
Tail (hv_chen >= 20 GPa, 103 of 2120 pooled rows; per-fold n 20, 26, 22, 9, 26): the formulas underpredict the tail badly, 10.07 vs the SVR's 8.74 and Magpie-only 12.84, i.e. d_023 recovers 68% of the Magpie-to-SVR tail gap at c<=12 ((12.84-10.07)/(12.84-8.74)), though it still misses the SVR by 1.33 GPa and the constant-to-SVR tail gap by far more than the headline MAE does.

## Per-fold test MAE (GPa), mean ± sd over 5 outer folds

Runs ncv_d023; niterations=22000, seed=0, procs=4, maxsize=15, timeout=900s, rows=2120, groups=1406.

| arm | window | f0 | f1 | f2 | f3 | f4 | mean ± sd | pooled tail MAE (>=20) | n_tail | folds with d_023 | nonfinite |
|---|---|---|---|---|---|---|---|---|---|---|---|
| median_const | c<=9 | 4.777 | 4.649 | 5.064 | 4.466 | 5.490 | 4.889 ± 0.400 | 21.97 | 103 | 0/5 | 0 |
| median_const | c<=12 | 4.777 | 4.649 | 5.064 | 4.466 | 5.490 | 4.889 ± 0.400 | 21.97 | 103 | 0/5 | 0 |
| median_const | c<=15 | 4.777 | 4.649 | 5.064 | 4.466 | 5.490 | 4.889 ± 0.400 | 21.97 | 103 | 0/5 | 0 |
| svr_baseline | c<=9 | 2.956 | 2.782 | 3.145 | 2.412 | 2.757 | 2.810 ± 0.272 | 8.74 | 103 | 0/5 | 0 |
| svr_baseline | c<=12 | 2.956 | 2.782 | 3.145 | 2.412 | 2.757 | 2.810 ± 0.272 | 8.74 | 103 | 0/5 | 0 |
| svr_baseline | c<=15 | 2.956 | 2.782 | 3.145 | 2.412 | 2.757 | 2.810 ± 0.272 | 8.74 | 103 | 0/5 | 0 |
| svr_fitidx | c<=9 | 3.054 | 2.953 | 3.260 | 2.568 | 2.928 | 2.952 ± 0.252 | 9.06 | 103 | 0/5 | 0 |
| svr_fitidx | c<=12 | 3.054 | 2.953 | 3.260 | 2.568 | 2.928 | 2.952 ± 0.252 | 9.06 | 103 | 0/5 | 0 |
| svr_fitidx | c<=15 | 3.054 | 2.953 | 3.260 | 2.568 | 2.928 | 2.952 ± 0.252 | 9.06 | 103 | 0/5 | 0 |
| magpie | c<=9 | 3.918 | 4.212 | 4.058 | 3.813 | 4.196 | 4.039 ± 0.174 | 14.97 | 103 | 0/5 | 0 |
| magpie | c<=12 | 3.859 | 3.739 | 3.850 | 3.547 | 3.937 | 3.787 ± 0.151 | 12.84 | 103 | 0/5 | 0 |
| magpie | c<=15 | 3.859 | 3.792 | 3.765 | 3.481 | 3.937 | 3.767 ± 0.173 | 12.70 | 103 | 0/5 | 0 |
| magpie+d_023 | c<=9 | 3.642 | 3.669 | 3.626 | 3.383 | 3.772 | 3.618 ± 0.144 | 9.95 | 103 | 5/5 | 0 |
| magpie+d_023 | c<=12 | 3.617 | 3.669 | 3.658 | 3.326 | 3.772 | 3.608 ± 0.168 | 10.07 | 103 | 5/5 | 0 |
| magpie+d_023 | c<=15 | 3.507 | 3.506 | 3.504 | 3.326 | 3.622 | 3.493 ± 0.106 | 10.05 | 103 | 5/5 | 0 |
| magpie+d_023+d_031 | c<=9 | 3.642 | 3.667 | 3.626 | 3.383 | 3.772 | 3.618 ± 0.143 | 9.90 | 103 | 5/5 | 0 |
| magpie+d_023+d_031 | c<=12 | 3.617 | 3.646 | 3.618 | 3.353 | 3.772 | 3.601 ± 0.153 | 10.05 | 103 | 5/5 | 0 |
| magpie+d_023+d_031 | c<=15 | 3.507 | 3.646 | 3.535 | 3.281 | 3.622 | 3.518 ± 0.145 | 9.76 | 103 | 5/5 | 0 |

## Selected equation per fold and window (complexity, inner-val MAE, outer-test MAE)

- magpie c<=9 f0 (c9, inner 4.122, test 3.918, uses -): `((313.5142 / m_NValence) / (m_GSvolume_pa - 4.9109)) + m_NUnfilled`
- magpie c<=9 f1 (c6, inner 3.727, test 4.212, uses -): `exp((m_NUnfilled + 3.5651524) / m_Row)`
- magpie c<=9 f2 (c7, inner 3.778, test 4.058, uses -): `((500.17487 / m_NValence) / m_GSvolume_pa) + m_NUnfilled`
- magpie c<=9 f3 (c7, inner 3.937, test 3.813, uses -): `m_NUnfilled + ((1614.5458 / m_GSvolume_pa) / m_Number)`
- magpie c<=9 f4 (c9, inner 3.373, test 4.196, uses -): `((56671.316 / (m_CovalentRadius * m_NValence)) / m_GSvolume_pa) + m_NUnfilled`
- magpie c<=12 f0 (c10, inner 3.931, test 3.859, uses -): `m_NUnfilled + (m_MendeleevNumber / (exp(m_Row) / (4.0826006 - m_NpValence)))`
- magpie c<=12 f1 (c12, inner 3.686, test 3.739, uses -): `253.16577 / (((exp(m_NpValence) - m_NUnfilled) + (m_NdValence * m_Row)) + m_GSvolume_pa)`
- magpie c<=12 f2 (c12, inner 3.665, test 3.850, uses -): `(((398.1363 - exp(m_NdUnfilled)) / m_NValence) / (m_GSvolume_pa - m_NUnfilled)) + m_NUnfilled`
- magpie c<=12 f3 (c12, inner 3.693, test 3.547, uses -): `((m_MendeleevNumber * ((m_NsValence * 2.2444355) - m_NpValence)) / exp(m_Row)) + m_NUnfilled`
- magpie c<=12 f4 (c12, inner 3.317, test 3.937, uses -): `m_NUnfilled + ((m_MendeleevNumber * ((m_NsValence / 0.4594579) - m_NpValence)) / exp(m_Row))`
- magpie c<=15 f0 (c10, inner 3.931, test 3.859, uses -): `m_NUnfilled + (m_MendeleevNumber / (exp(m_Row) / (4.0826006 - m_NpValence)))`
- magpie c<=15 f1 (c14, inner 3.620, test 3.792, uses -): `251.85307 / ((m_NdValence * m_Row) + ((exp(m_NpValence) + m_GSvolume_pa) - (m_NpUnfilled * m_NdUnfilled)))`
- magpie c<=15 f2 (c14, inner 3.605, test 3.765, uses -): `m_NUnfilled + (((383.34253 - exp(m_NdUnfilled)) / (m_GSvolume_pa - m_NUnfilled)) / (m_NValence - m_NfValence))`
- magpie c<=15 f3 (c15, inner 3.598, test 3.481, uses -): `m_NUnfilled + ((sqrt(m_GSbandgap) + (m_MendeleevNumber / exp(m_Row))) * ((m_NsValence * 2.0500977) - m_NpValence))`
- magpie c<=15 f4 (c13, inner 3.313, test 3.937, uses -): `(m_MendeleevNumber * ((exp(m_NsValence / 1.3458744) - m_NpValence) / exp(m_Row))) + m_NUnfilled`
- magpie+d_023 c<=9 f0 (c8, inner 3.779, test 3.642, uses d_023): `(d_023 / (sqrt(m_Column) + m_NdValence)) + m_NpUnfilled`
- magpie+d_023 c<=9 f1 (c9, inner 3.264, test 3.669, uses d_023): `(d_023 / (m_Electronegativity + (m_NdValence + 0.88324726))) + m_NpUnfilled`
- magpie+d_023 c<=9 f2 (c8, inner 3.419, test 3.626, uses d_023): `(d_023 / (m_NdValence + sqrt(m_Column))) + m_NpUnfilled`
- magpie+d_023 c<=9 f3 (c8, inner 3.509, test 3.383, uses d_023): `(d_023 / (m_NdValence + sqrt(m_Column))) + m_NpUnfilled`
- magpie+d_023 c<=9 f4 (c8, inner 3.346, test 3.772, uses d_023): `(d_023 / (m_NdValence + sqrt(m_Column))) + m_NpUnfilled`
- magpie+d_023 c<=12 f0 (c11, inner 3.660, test 3.617, uses d_023): `(m_NpUnfilled * sqrt(m_NdUnfilled)) + (d_023 / (m_NdValence + sqrt(m_Column)))`
- magpie+d_023 c<=12 f1 (c9, inner 3.264, test 3.669, uses d_023): `(d_023 / (m_Electronegativity + (m_NdValence + 0.88324726))) + m_NpUnfilled`
- magpie+d_023 c<=12 f2 (c12, inner 3.374, test 3.658, uses d_023): `m_NpUnfilled + (d_023 / (((m_Row + m_NdValence) / sqrt(m_NsValence)) + m_NpValence))`
- magpie+d_023 c<=12 f3 (c12, inner 3.422, test 3.326, uses d_023): `(d_023 / (m_NdValence + sqrt(m_Column))) + ((m_NsValence + -0.6164457) * m_NpUnfilled)`
- magpie+d_023 c<=12 f4 (c8, inner 3.346, test 3.772, uses d_023): `(d_023 / (m_NdValence + sqrt(m_Column))) + m_NpUnfilled`
- magpie+d_023 c<=15 f0 (c15, inner 3.499, test 3.507, uses d_023): `(d_023 / (m_NdValence + sqrt(m_NdUnfilled + m_Column))) + (m_NpUnfilled * (sqrt(m_NdUnfilled) + 0.4351303))`
- magpie+d_023 c<=15 f1 (c13, inner 3.181, test 3.506, uses d_023): `(d_023 / (m_Electronegativity + (m_NdValence + log(m_Row)))) + (m_NpUnfilled * sqrt(m_NdUnfilled))`
- magpie+d_023 c<=15 f2 (c14, inner 3.210, test 3.504, uses d_023): `((d_023 + 11.94037) / ((m_Row + m_NpValence) + m_NdValence)) + (m_NpUnfilled * sqrt(m_NdUnfilled))`
- magpie+d_023 c<=15 f3 (c12, inner 3.422, test 3.326, uses d_023): `(d_023 / (m_NdValence + sqrt(m_Column))) + ((m_NsValence + -0.6164457) * m_NpUnfilled)`
- magpie+d_023 c<=15 f4 (c13, inner 3.289, test 3.622, uses d_023): `(sqrt(m_NdUnfilled) * m_NpUnfilled) + (d_023 / (m_NdValence + sqrt(m_NdUnfilled + m_Column)))`
- magpie+d_023+d_031 c<=9 f0 (c8, inner 3.779, test 3.642, uses d_023): `m_NpUnfilled + (d_023 / (sqrt(m_Column) + m_NdValence))`
- magpie+d_023+d_031 c<=9 f1 (c9, inner 3.284, test 3.667, uses d_023+d_031): `d_023 / ((m_Electronegativity * 1.3700607) + (d_031 * m_NdValence))`
- magpie+d_023+d_031 c<=9 f2 (c8, inner 3.419, test 3.626, uses d_023): `m_NpUnfilled + (d_023 / (sqrt(m_Column) + m_NdValence))`
- magpie+d_023+d_031 c<=9 f3 (c8, inner 3.509, test 3.383, uses d_023): `m_NpUnfilled + (d_023 / (m_NdValence + sqrt(m_Column)))`
- magpie+d_023+d_031 c<=9 f4 (c8, inner 3.346, test 3.772, uses d_023): `(d_023 / (sqrt(m_Column) + m_NdValence)) + m_NpUnfilled`
- magpie+d_023+d_031 c<=12 f0 (c11, inner 3.660, test 3.617, uses d_023): `(d_023 / (sqrt(m_Column) + m_NdValence)) + (sqrt(m_NdUnfilled) * m_NpUnfilled)`
- magpie+d_023+d_031 c<=12 f1 (c10, inner 3.258, test 3.646, uses d_023+d_031): `d_023 / ((m_NdValence * d_031) + exp(m_Electronegativity * 0.49487114))`
- magpie+d_023+d_031 c<=12 f2 (c12, inner 3.284, test 3.618, uses d_023+d_031): `(d_023 / (m_NValence - m_NfValence)) + (exp(m_NsValence - d_031) - m_Electronegativity)`
- magpie+d_023+d_031 c<=12 f3 (c12, inner 3.410, test 3.353, uses d_023+d_031): `(d_023 / (sqrt(m_Column) + m_NdValence)) + (m_NpUnfilled * (m_NsValence - d_031))`
- magpie+d_023+d_031 c<=12 f4 (c8, inner 3.346, test 3.772, uses d_023): `(d_023 / (sqrt(m_Column) + m_NdValence)) + m_NpUnfilled`
- magpie+d_023+d_031 c<=15 f0 (c15, inner 3.499, test 3.507, uses d_023): `(d_023 / (m_NdValence + sqrt(m_NdUnfilled + m_Column))) + (m_NpUnfilled * (sqrt(m_NdUnfilled) - -0.43399423))`
- magpie+d_023+d_031 c<=15 f1 (c10, inner 3.258, test 3.646, uses d_023+d_031): `d_023 / ((m_NdValence * d_031) + exp(m_Electronegativity * 0.49487114))`
- magpie+d_023+d_031 c<=15 f2 (c15, inner 3.277, test 3.535, uses d_023+d_031): `(d_023 / ((sqrt(m_Column) + m_NdValence) + 0.33464015)) + (m_NpUnfilled * (sqrt(m_NUnfilled) - d_031))`
- magpie+d_023+d_031 c<=15 f3 (c13, inner 3.371, test 3.281, uses d_023+d_031): `(m_NpUnfilled * (sqrt(m_NUnfilled) - d_031)) + (d_023 / (m_NdValence + sqrt(m_Column)))`
- magpie+d_023+d_031 c<=15 f4 (c13, inner 3.289, test 3.622, uses d_023): `(d_023 / (sqrt(m_NdUnfilled + m_Column) + m_NdValence)) + (sqrt(m_NdUnfilled) * m_NpUnfilled)`

## Does d_023 hold on folds where the equation search never saw the held-out element sets, and how far is it from the SVR under the same folds?
Conditional on the previously selected d_023 feature, the equation search improves on Magpie-only in all five outer folds at every complexity window (mean paired gain 0.42 GPa at c<=9, 0.18 at c<=12, 0.27 at c<=15), selects d_023 in 5/5 folds, and at c<=9 re-derives the c8 form found on the original val split (`d_023/(sqrt(Column)+NdValence) + NpUnfilled`) in four of five folds. The fold-mean at c<=12 is 3.608 against 3.787 for Magpie only; the c<=12 gain (0.18) is smaller than the 0.30 seen on the single val split, and the c<=9 gain is larger than the c<=12 gain but smaller than on val (0.42 against 0.50 GPa). This is exploratory evidence of recurrence across repartitions of reused development data; it does not rule out descriptor-selection optimism and does not independently validate the descriptor. The reason is the selection history: d_023 as a *feature choice* was screened on train labels, and a two-parameter fit was scored once on val in that initial screen, before it was adopted; val was reused afterwards, and train+val is exactly the pooled set here, so every outer-test row had already informed the choice of d_023. The folds hold element sets out of the equation fitting and the inner equation selection, not out of the descriptor choice. Against the SVR run under the same folds, the magpie+d_023 arm at c<=12 is at 3.608 against 2.810 (ratio of fold means 1.284; fold-averaged MAE ratio, MASE, 1.291), closes 62% of the constant-to-SVR gap (53% for Magpie only), and has pooled >= 20 GPa tail MAE 10.07 against 8.74 for the SVR and 12.84 for Magpie only. The fit-row-matched SVR (`svr_fitidx`: fitted on the inner-train rows only; the PySR arms additionally use inner-validation labels for equation selection) is 2.952, so most of the 0.80 GPa deficit (0.66 against the fit-row-matched SVR) is not explained by the SVR seeing more rows. The SVR is a fair predictive benchmark with different resources: it uses 132 Magpie statistics and separate log B / log G supervision tuned by grouped CV on log-modulus MAE before conversion through Chen, whereas symbolic regression uses 22 Magpie means plus d_023 and selects on hv_chen MAE; the remaining deficit therefore does not isolate formula compactness from feature, supervision or tuning differences. The d_023-arm deficit against the SVR ranges from 0.36 GPa (fold 2, c<=15) to 1.02 GPa (fold 4, c<=9 and c<=12). The c<=12 relative-error summaries (MASE about 1.3, 62% of the gap closed) are numerically similar to those on the reused val split (1.30, 62%); that similarity is not independent corroboration. Adding d_031 shows no consistent incremental benefit in these runs (-0.007 at c<=12, +0.025 at c<=15). Limits: one PySR fit per (fold, arm), shared across the complexity windows; any two outer folds share approximately three quarters of their outer-training rows; the sd across folds measures fold heterogeneity, not optimizer or selection uncertainty; the target is the DFT-derived Chen proxy, not measured hardness.
Reviewer (codex regular, one pass): ACCEPT WITH FIXES; fixes applied (corrected the maximum SVR deficit to 1.02 from fold 4, labelled the arm and window explicitly, separated MASE from the ratio of means 1.284, narrowed 'holds' and 'same picture as on val', added the SVR resource difference).
