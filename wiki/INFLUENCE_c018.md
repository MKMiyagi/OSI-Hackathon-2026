# Influence analysis: c018_s0 c12 vs Magpie c12 (development-set, val reused)

Script: `scripts/influence_c018.py`. Equations are taken verbatim from ledger/results.csv (c018_s0 c12; c012_s1 c12, the recurring Magpie-only c12 equation). All MAEs are development-set (val, reused), n=374.

- c018_s0 c12: `(1070.5477/((exp(d_017)+(NdValence+3.0097768))-GSbandgap))/GSvolume_pa`, val MAE 3.7722
- Magpie c12: `642.6664/GSvolume_pa/(NValence-NfValence)+NpUnfilled*sqrt(NdUnfilled)`, val MAE 3.9114

## 1. Per-row jackknife of the MAE gap
Gap = MAE(Magpie) - MAE(c018_s0) = 0.1393 GPa; jackknife SE 0.0961 (row-level, ignores duplicate-composition correlation and selection; descriptive only). Gap is positive in 179 rows, negative in 195.

Top-10 influential rows (by |per-row contribution|; contribution = (|err_mag|-|err_c018|)/n; gap without the row in last column):

| rank | formula | target | pred c018 | pred Magpie | contribution to gap | gap without row |
|---|---|---|---|---|---|---|
| 1 | Be3P2 | 15.53 | 23.15 | 14.59 | -0.0179 | 0.1576 |
| 2 | Fe(SiP)4 | 17.99 | 14.60 | 8.55 | +0.0162 | 0.1234 |
| 3 | Mg(BeN)2 | 32.10 | 20.61 | 14.72 | +0.0157 | 0.1239 |
| 4 | ReO3 | 12.70 | 5.84 | 11.48 | -0.0151 | 0.1547 |
| 5 | ReO3 | 12.59 | 5.84 | 11.48 | -0.0151 | 0.1547 |
| 6 | ReO3 | 12.71 | 5.84 | 11.48 | -0.0151 | 0.1547 |
| 7 | VO2 | 3.13 | 7.39 | 12.93 | +0.0148 | 0.1248 |
| 8 | Mg(AlC)2 | 14.75 | 20.01 | 14.96 | -0.0135 | 0.1532 |
| 9 | V3O5 | 7.74 | 7.96 | 12.83 | +0.0130 | 0.1266 |
| 10 | MnWO4 | 4.72 | 7.08 | 11.74 | +0.0125 | 0.1271 |

- Top-10 by |contribution|: net -0.0043 of the 0.1393 gap (-3.1%); gap on the remaining 364 rows = 0.1475.
- Top-10 by positive contribution only: +0.1319 (94.7% of the gap); gap on the other 364 rows = 0.0075.
- Dropping the top-10 compositions (group-level, 10 compositions): gap = 0.1078.

## 2. Per-family MAE
Families (assigned in this order): oxides = contains O; binary C/N/B = exactly two elements, one of B/C/N, no O; intermetallics = every element a metal or Si/Ge/Sb; other = the rest. 

| family | n | MAE c018_s0 | MAE Magpie c12 | gap (Magpie - c018) | share of total gap | mean target | MAE const (train median) |
|---|---|---|---|---|---|---|---|
| binary carbides/nitrides/borides | 14 | 8.831 | 8.473 | -0.358 | -9.6% | 17.36 | 13.517 |
| oxides | 36 | 3.975 | 4.540 | +0.565 | 39.1% | 4.88 | 3.945 |
| intermetallics | 189 | 3.582 | 3.612 | +0.030 | 10.9% | 6.79 | 4.295 |
| other | 135 | 3.460 | 3.690 | +0.230 | 59.7% | 6.74 | 5.508 |
| all | 374 | 3.772 | 3.911 | +0.139 | 100% | 6.98 | 5.044 |

## 3. GSbandgap ablation
Same functional form with the `- m_GSbandgap` term deleted: `C1/((exp(d_017)+NdValence+C2)*GSvolume_pa)`. Constants (C1, C2) re-fit three ways, each also done for the full form (control) so the comparison is like for like. Nelder-Mead from several starts; best of starts reported. 'train' fits never see val. 'val (oracle)' fits constants on val itself and is optimistic.

| fit | form | C1 | C2 | train MAE | val MAE |
|---|---|---|---|---|---|
| as published (PySR constants) | with GSbandgap | 1070.5 | 3.010 | 3.7309 | 3.7722 |
| train, MSE | with GSbandgap | 1070.0 | 3.008 | 3.7308 | 3.7719 |
| train, MSE | without GSbandgap | 1108.7 | 2.726 | 3.8253 | 3.9113 |
| train, MAE | with GSbandgap | 933.6 | 2.455 | 3.7141 | 3.7333 |
| train, MAE | without GSbandgap | 928.5 | 2.075 | 3.7924 | 3.8581 |
| val, MAE (oracle) | with GSbandgap | 871.8 | 1.939 | 3.7274 | 3.7185 |
| val, MAE (oracle) | without GSbandgap | 868.9 | 1.861 | 3.7979 | 3.8514 |

GSbandgap in val: mean 0.417 eV, max 3.22; in train mean 0.376.

## Summary (descriptive; no selection-corrected inference)
- The 0.139 GPa gap reproduces the reviewer's concentration: the ten rows that favour c018_s0 most (VO2, V3O5, MnWO4, Mg(BeN)2, Fe(SiP)4, ... ) contribute 94.7% of it; on the other 364 rows the gap is 0.0075. The rows that favour Magpie most (Be3P2, ReO3 x3, Mg(AlC)2) offset them, so by |contribution| the top 10 are net -3%. The gap is the small difference of two large opposing sets of rows (positive in 179 rows, negative in 195); jackknife SE 0.096 is about 70% of the gap itself. ReO3 appears three times (near-duplicate targets 12.6-12.7), so row-level jackknife overstates independence; dropping the top 10 compositions leaves 0.108.
- By family the gain sits in oxides (+0.565) and "other" (+0.230); intermetallics are a tie (+0.030) and the 14 binary carbides/nitrides/borides, the only family with high hardness, are worse (-0.358, MAE ~8.5-8.8 against a 17.4 GPa mean). Neither equation is a hard-materials predictor.
- GSbandgap ablation: removing the `- GSbandgap` term and re-fitting C1, C2 on train raises val MAE from 3.772 to 3.911 (MSE fit) or 3.733 to 3.858 (MAE fit), i.e. back to the Magpie c12 value (3.9114) or within 0.05 of it. So essentially all of c018_s0's advantage over Magpie comes from the band-gap term (an elemental-mean eV value subtracted from dimensionless counts), not from d_017. This is consistent with the verdict that d_017 adds no c12 improvement. Re-fitting constants on train for the full form changes val MAE by only 0.0003 (MSE) so the published constants are near their train optimum; an MAE fit on train gives 3.733, i.e. the published constants are not even val-optimal, which argues against the gap being an artefact of constant tuning on val.
