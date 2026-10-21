# Data audit: duplicate compositions, negatives, tail (train + val only)

Reproduce: `uv run python scripts/data_audit.py`. Duplicates are defined by pymatgen `reduced_formula` (so Ti2O4 and TiO2 collapse; polymorphs and different cell sizes of one composition are indistinguishable by composition). Test data was not touched. `data/splits` has only `formula, bulk_modulus, shear_modulus, hv_chen`, so no structure ID or energy is available here.

Note on the constant comparator: the train **median** target is 5.7499 GPa; the number 5.0442 quoted in the verdict is the **val MAE** of predicting that constant (train-mean constant 7.228 gives 5.2589). 

## Findings (script output, verbatim)
rows 1746 374 | median train 5.749891403166224 | val MAE median-const 5.044224055568322 | val MAE mean-const 5.25893873676617

## train: 1746 rows, 1624 distinct reduced formulas
- compositions with >1 row: 108 (230 rows = 13.2% of rows)
- max rows per composition: 7
- target spread (max-min) over those: median 1.41, mean 2.94, p90 7.27, max 49.90 GPa; 20 compositions with spread >5 GPa, 4 with >10
- within-split irreducible MAE floor (group-median predictor, all rows of train): 0.1903 GPa; restricted to duplicated rows: 1.4444
- widest groups: BN (2 rows, 14.11..64.01); Si2W (2 rows, 20.13..33.15); TiO2 (7 rows, 0.68..11.69); LiAlO2 (2 rows, 7.34..18.07); Y(SiIr)2 (2 rows, 3.55..13.30); Si2Mo (2 rows, 22.34..31.44)

## val: 374 rows, 350 distinct reduced formulas
- compositions with >1 row: 17 (41 rows = 11.0% of rows)
- max rows per composition: 3
- target spread (max-min) over those: median 0.88, mean 3.24, p90 8.76, max 13.39 GPa; 5 compositions with spread >5 GPa, 1 with >10
- within-split irreducible MAE floor (group-median predictor, all rows of val): 0.1474 GPa; restricted to duplicated rows: 1.3442
- widest groups: V5Si3 (2 rows, 2.38..15.76); YAl3 (3 rows, 5.61..14.86); KNbO3 (2 rows, 2.91..11.35); CaSiPt (3 rows, -0.81..5.03); V3Au (2 rows, 0.05..5.17); SiRh (3 rows, 5.47..9.39)

## Negative targets / tail
- train negative: 128/1746; val negative: 39/374 (min val -1.87)
- val >=20 GPa: 17 rows; train >=20: 86; val max 41.98
- val >=20 tail share of total absolute deviation from train median: 20.3%
- val rows whose composition also occurs in train (cross-split leakage by reduced formula): 0

## Pooled train+val duplicate floor
- group-median predictor MAE over all 2120 rows: 0.1827 GPa
- leave-one-out within-composition (rows with >=1 sibling), train: 2.778 over 230 rows; val: 2.513 over 41 rows

## Reading
- 13.2% of train rows (108 compositions) and 11.0% of val rows (17 compositions, 41 rows) are polymorphs/duplicates. No val composition occurs in train (grouped split works at the reduced-formula level).
- Spread is heavy-tailed: median 1.4 / 0.9 GPa, but a few pairs differ by 10-50 GPa (BN 14.11 vs 64.01 in train; V5Si3 2.38 vs 15.76 in val).
- 39/374 val and 128/1746 train targets are negative (Chen proxy goes below 0 when G/B is small); 17 val rows are >= 20 GPa and carry ~20% of the val absolute deviation from the train median.

## Irreducible floor from duplicate spread alone
For any predictor that maps composition to one number, the best it can do on a set of rows sharing a composition is the group median. The resulting MAE over all rows is **0.147 GPa on val** (0.190 on train, 0.183 pooled), i.e. about 4% of the current ~3.8-4.0 GPa errors. Restricted to the 41 duplicated val rows it is 1.34 GPa. So duplicates cap how low a composition-only MAE can go (no formula can beat ~0.15 on val as defined), but they are **not** what limits the current results; they matter for individual rows (V5Si3, YAl3, CaSiPt) and for evaluation noise, not for the aggregate gap. Caveat: this floor is in-sample for the group (a predictor would need to know each group's median), so it is a lower bound; the leave-one-out sibling error is 2.5 GPa on val duplicates (2.8 train), a more realistic cost of an unseen polymorph.

## Proposed handling rule (NOT applied; splits and score.py are frozen)
1. Keep the split files unchanged for the frozen metric. Report, alongside the headline MAE, the MAE on a de-duplicated view of val.
2. De-duplication rule for any new analysis or any future re-split: one row per reduced formula. If the source data carries a structure/energy field (re-pull from the matminer dataset with its ID/formation-energy columns), keep the minimum-energy structure; else take the mean target of the group (or the median, which is the MAE-optimal constant and robust to the BN-type outliers). Record the group size and spread as a column so noisy compositions can be flagged or down-weighted.
3. Any future grouped CV should group by reduced formula (already true for element-set grouping) so siblings never straddle folds.
4. Treat negative targets as valid Chen outputs but report MAE with and without rows < 0 (and the >= 20 GPa tail separately); do not clip silently.
