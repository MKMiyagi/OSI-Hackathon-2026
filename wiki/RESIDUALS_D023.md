# Residuals of the d_023 c8 and c5 formulas on val, by chemical family (overnight 5, step 0)

Script: `eval/residuals_d023.py` (val only; never the test file). Tables: `ledger/residuals_d023.csv`, per-row predictions `ledger/residuals_d023_rows.csv`.
Target is the DFT-derived Chen proxy `hv_chen`; val is a reused development set. Signed error = prediction - hv_chen (positive = formula too hard).
Formulas: c8 `(d_023/(m_NdValence + sqrt(m_Column))) + m_NpUnfilled` (val 3.6939 reproduced); c5 `d_023/(m_NdValence + 2.4609854)` (3.9077). SVR = primary Magpie B,G -> Chen (2.839).
Families (fixed rules, first match wins): binary_CNB = two elements, one of B/C/N, the other not B/C/N/O; oxide = contains O; pnictide_chalcogenide = contains P/As/Sb/S/Se/Te, no O; intermetallic = all elements in the d_031 METALS list; other = the rest (37 Si/Ge compounds, 24 halides, 24 ternary B/C/N or misc).

## Per-family MAE and mean signed error (GPa)
| family | n | mean hv | MAE const | MAE SVR | MAE c8 | bias c8 | MAE c5 | bias c5 | c8 - SVR | Spearman c8 (SVR) |
|---|---|---|---|---|---|---|---|---|---|---|
| binary carbide/nitride/boride | 14 | 17.36 | 13.52 | 6.01 | 7.40 | +0.63 | 7.20 | +1.08 | +1.39 | 0.74 (0.83) |
| oxide | 36 | 4.88 | 3.94 | 2.23 | 4.19 | **+2.63** | 4.87 | +2.97 | **+1.96** | 0.55 (0.77) |
| pnictide/chalcogenide | 97 | 6.60 | 4.44 | 2.48 | 3.28 | -1.55 | 3.46 | -2.38 | +0.80 | 0.66 (0.81) |
| intermetallic | 142 | 6.73 | 4.41 | 2.87 | 3.41 | +0.34 | 3.62 | -0.81 | +0.54 | 0.43 (0.68) |
| other | 85 | 7.03 | 5.86 | 2.92 | 3.82 | -0.01 | 3.96 | -0.65 | +0.90 | 0.79 (0.82) |
| all | 374 | 6.98 | 5.04 | 2.84 | 3.69 | 0.00 | 3.91 | -0.75 | +0.85 | |

## Reading
- **Oxides are the one family where d_023 is worse than the constant** (MAE 4.19 vs 3.94; c5 4.87), with a systematic +2.6 GPa overprediction (VO2 13.3 vs 3.1, MgWO4, FeWO4 in the c5 worst list). Oxides have high cohesive-energy density (O is strongly bound, small volume) but low Chen hardness: B is high, G/B is low. That is a shear/ductility signature that d_023 cannot see.
- **Hard covalent compounds are underpredicted and soft ionic ones overpredicted inside the same family.** binary_CNB bias is +0.63 only by cancellation: ZrB2 (-18.7) and TaN (-14.6) underpredicted, BaC2 (+15.2) and CoN (+10.2) overpredicted. MAE 7.40 is 1.39 above the SVR; the formula is not discriminating hard from soft at similar d_023. Among the 12 val rows >= 20 GPa outside the oxide family, the signed error is -8 to -14 GPa (binary_CNB -7.9, other -9.6, pnictide -14.0, n = 6/5/1).
- **Intermetallics** (n = 142, 38% of val) have bias near zero but the worst ranking (Spearman 0.43 vs 0.68): 70 of them are below 5 GPa, bias there +3.0, and the hard ones (Be12W, Be22Re, MoIr3, Ir3W) are underpredicted. Ordering within the metals is the weakest part.
- **Pnictides/chalcogenides** are systematically too soft (-1.55; c5 -2.38).
- Worst rows (both formulas): ZrB2, BaC2, Mg(BeN)2, VSi2, TaN, VP2, Ca(CoP)2, LiZnN, VO2, Ti2GaC, P2Ir. Full 20-row lists per formula below.
- Every family trails the SVR; the gap is largest for oxides (+1.96) and binary_CNB (+1.39), smallest for intermetallics (+0.54). Total excess MAE over the SVR (n x gap): oxide 71, pnictide 78, intermetallic 77, other 77, binary_CNB 19 GPa-rows, i.e. four families contribute similarly and the CNB family is small (n = 14).

## Cycle ordering (028-031) and the reason
Pattern: the signed errors split by bond character at fixed d_023 (ionic/soft overpredicted, covalent/hard underpredicted), which is the G/B (Pugh) signature the hypothesis names. The ordering from the brief (028 d_030, 029 d_028, 030 d_007, 031 d_031) is kept in numbering, but **cycles 028 and 029 cannot be run under the pre-registered fallback rules (coverage table below)**. The runnable order is therefore:
1. **031 d_023 + d_031 (metal fraction) first.** Full coverage (0 NaN), and it addresses the largest-bias family (oxides, metal fraction 1/3-1/2 with a non-metal anion that makes them ionic) and the 142 intermetallics (fraction 1) at once; a metal/non-metal split is the cheapest available proxy for the bond character that separates the over- and underpredicted rows.
2. **030 d_023 + d_007 (B/C/N fraction).** Full coverage, targets only the 14 binary_CNB rows plus a few "other"; smaller upside on the headline metric (the family is 4% of val) but cheap and never tested jointly.
3. 028 and 029: blocked by coverage, see below.
Decision sequence uses only the residual table, not any new-descriptor result.

## Coverage table (before any cycle; per-split row counts, fallback = NaN with row drop, never a fit)
Elements in train+val: 62. pymatgen `Element.rigidity_modulus` (G) / `bulk_modulus` (B) are None for:
- **G missing (20):** As, B, Br, C, Cl, Cs, F, Ga, Ge, Hg, I, In, Mn, N, O, P, Rb, S, Si, Tc. (Present only for 42 elements.)
- **B missing (10):** F, Ga, Ge, In, N, O, Os, Sr, Tc, Zr. (Pymatgen's B for C = 33 GPa is graphite-like, not diamond.)
- Cited fallback search: the Wikipedia data page "Elastic properties of the elements" (WebElements / CRC Handbook 84th ed. / Kaye & Laby) also has **no shear modulus for B, C, Si, P, S, As, Ge, Ga, In, Br, I, N, O, F, Cl** and no bulk modulus for N, O, F, In, Tc, Sr. A handful of B values exist (Ge 75.8, Os 462, Ga 56) but none of the missing G values that matter. So no cited published fallback exists for the elements that dominate the hard and the oxide rows; imputing or fitting one is forbidden by the brief.

| descriptor | split | rows | finite | dropped (%) | rows >= 20 GPa dropped | mean hv of dropped rows |
|---|---|---|---|---|---|---|
| d_028 (G) | train | 1746 | 721 | 1025 (58.7%) | 63 / 86 | 8.26 |
| d_028 (G) | val | 374 | 139 | 235 (62.8%) | 12 / 17 | 7.38 |
| d_029 (B) | train | 1746 | 1209 | 537 (30.8%) | 12 / 86 | 7.05 |
| d_029 (B) | val | 374 | 242 | 132 (35.3%) | 5 / 17 | 6.30 |
| d_030 (G/B) | train | 1746 | 653 | 1093 (62.6%) | 63 / 86 | 8.06 |
| d_030 (G/B) | val | 374 | 119 | 255 (68.2%) | 13 / 17 | 7.30 |
| d_031 (metal fraction) | train | 1746 | 1746 | 0 | 0 | - |
| d_031 (metal fraction) | val | 374 | 374 | 0 | 0 | - |

**Consequence for cycles 028 and 029:** (i) `eval/score.py` raises SystemExit on any non-finite val feature and may not be edited, so a descriptor with NaN on 63-68% of val rows cannot be scored on val at all; (ii) training on the finite rows alone (653-721 of 1746) is a different training set from the 9-seed reference, so the headline would not be comparable; (iii) the dropped rows contain the oxides, borides, carbides, nitrides and silicides, i.e. exactly where the residuals are; the 119-139 surviving val rows are almost all intermetallics and heavier compounds. Cycles 028 and 029 were therefore **not run** (not counted toward the stop rule: no fit was done). The honest options for the team: (a) drop them; (b) a covered-subset paired comparison (d_023 vs d_023 + d_030, both trained and scored on the same finite rows, own scorer, reference equations re-evaluated on the same rows), a different and much weaker question; (c) supply a defensible G for B, C, N, O, Si, ... from a DFT/handbook source, which needs a team decision on provenance. Not done tonight.

## 20 worst val rows (|error|, GPa)
c8: ZrB2, BaC2, Mg(BeN)2, VSi2, TaN, VP2, Ca(CoP)2, MoIr3, LiZnN, Mg23Al30, CoN, VO2, P2Ir, Al3Ir, Cr3PtN, V5Si3, Ir3W, MoIr, Ti2GaC, Ti2FeS4. c5: ZrB2, BaC2, Mg(BeN)2, VSi2, Be12W, Be22Re, VP2, TaN, VO2, Ca(CoP)2, ZrGa3, MgWO4, FeWO4, LiZnN, Ti2GaC, As2Ir, TaSb2, P2Ir, As3Ir, Sc3SnB. Values (hv_chen, c8/c5 prediction, SVR) in `ledger/residuals_d023_rows.csv`; script prints both top-20 tables.
Six rows appear in both formulas' list with a sign error against the SVR (BaC2: truth -1.3, c8 +13.9, SVR -0.8; VO2: truth 3.1, c8 13.3, SVR 6.8; Mg23Al30; Al3Ir; V5Si3; CoN): soft/ionic or metal-rich-cohesive rows that the SVR, which sees G, places correctly. These are the rows a shear proxy should fix.
