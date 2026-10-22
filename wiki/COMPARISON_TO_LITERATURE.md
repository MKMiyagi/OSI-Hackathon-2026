# Comparison to the literature: composition -> B, G

Scope: how well do *our* composition-only models predict the bulk and shear moduli, next to what Tehrani et al. (2018) report on the same database? Numbers on our side come from `scripts/bg_errors.py` (output `ledger/bg_errors.csv`), on val only, reused development set. Numbers on the paper's side are quoted from the paper and each carries a source in the verification table at the end (citation audit: `wiki/CITATION_AUDIT_COMPARISON.md`).

**What this file does not do.** Our Hv numbers (`hv_chen`, MAE 2.84 GPa for the SVR, 3.6-4.2 GPa for formulas) are errors against the **Chen (2011) proxy computed from DFT B and G**, not against measured hardness. They cannot be compared to any published measured-Hv MAE, and no such comparison is made here. That comparison waits for Thursday's Zhang external check (wiki/TARGET_RECOMMENDATION.md, option c).

## 1. Same database?
Yes, the training database is Tehrani et al.'s own. The matminer record `brgoch_superhard_training` is described as "2574 materials used for training regressors that predict shear and bulk modulus", with VRH moduli and Materials Project IDs, and it references Mansouri Tehrani et al., J. Am. Chem. Soc. 140, 9844 (2018). The paper states that 3248 elastic moduli were extracted from the Materials Project, reduced to **2572** after filtering. The matminer snapshot has 2574 (a 2-row difference we cannot explain from the paper's text). Our pipeline drops the 80 rows flagged `suspect_value` (2494 remain), then splits 1746 train / 374 val / test (quarantined), grouped by element set so train and val share no element set and no reduced formula (wiki/SPLIT_FREEZE.md).

## 2. Our errors next to the published ones
Tehrani report **RMSE** and **r^2** from **10-fold cross-validation** on all 2572 moduli. We report **MAE** in the frozen metric, so the table gives RMSE and R^2 on val too, with 95% cluster-bootstrap intervals (resampling element-set groups, 2000 draws; SVR rows only).

| model | features | B RMSE (GPa) | B R^2 | G RMSE (GPa) | G R^2 | B MAE | G MAE |
|---|---|---|---|---|---|---|---|
| **Tehrani 2018, as published (10-fold CV, n = 2572)** | 150 (34 compositional variables x expressions + 14 structural); GA variable selection also run | **17.2** | **0.94** | **16.5** | **0.84** | not reported | not reported |
| our SVR, tehrani150 (val, n = 374) | the 150 shipped features, incl. 18 structure-derived | 16.3 [14.1, 18.7] | 0.951 [0.933, 0.965] | 17.5 [14.9, 20.0] | 0.831 [0.788, 0.865] | 10.5 | 11.5 |
| our SVR, tehrani_comp (val) | 132 composition-only | 21.5 [18.1, 25.2] | 0.915 [0.879, 0.940] | 20.9 [17.8, 24.1] | 0.759 [0.685, 0.812] | 13.8 | 13.5 |
| our SVR, Magpie (val), **the Hv baseline's B,G** | 132 Magpie, composition-only | 21.7 [17.6, 26.2] | 0.913 [0.868, 0.944] | 18.8 [16.5, 21.2] | 0.806 [0.751, 0.845] | 14.0 | 12.8 |
| symbolic B = 3.365 * d_023 (c3, T1, 3 seeds identical) | composition, one descriptor | 31.9 | 0.812 | n/a | n/a | 23.5 | n/a |
| symbolic B, Magpie only (T1, best of front within c<=15, mean of 3 seeds) | Magpie means | 40.9 | 0.692 | n/a | n/a | 31.2 | n/a |

Reading, with the caveats that matter:
1. **Our 150-feature SVR lands where the paper's figures do**: the published RMSEs (17.2, 16.5) sit inside our intervals and the r^2 values differ by at most 0.011. This is a consistency check on our baseline, not an independent replication.
2. **The two protocols are not the same, so the match is not evidence of equal difficulty.** The paper describes 10-fold CV with no mention of grouping, and polymorphs are separate entries labelled "composition, space group number", so same-composition entries can fall in different folds unless the folds were grouped (the text does not say). Our val is grouped by element set, which is stricter for new chemistries. Other differences: we drop 80 suspect rows; we fit log-moduli with a grid-searched RBF-SVR in scikit-learn, they used PLS_Toolbox in MATLAB with genetic-algorithm descriptor selection; our val has 374 rows (one large-modulus outlier moves RMSE visibly, hence the intervals).
3. **Composition-only costs accuracy.** Dropping the structural features moves B RMSE from 16.3 to 21.5-21.7 and G R^2 from 0.83 to 0.76-0.81 on val. The published model is not composition-only either (it uses 14 structural descriptors), a point already made in wiki/TARGET_RECOMMENDATION.md.
4. **Formulas for B are far behind the SVR**: the one-descriptor energy-density law `B = 3.365 d_023` has R^2 0.81 (RMSE 32 GPa) against 0.91-0.95; Magpie-only symbolic B never gets below 31 GPa MAE. There are **no symbolic G runs** and no B/G runs in this branch's `ledger/runs/`; the B runs above are T1's (`t1_B_s0-2`, `t1_Bd23_s0-2`, read from `origin/t1/wed` with `git show`, not merged). MAEs at c3 are not selected on val (one candidate); the c<=15 row takes the lowest-val-MAE equation within the budget and is optimistic.
5. Hv inherits both modulus errors through Chen's form (`Hv = 2 (k^2 G)^0.585 - 3`, k = G/B, Chen 2011, Eq. 11 of the arXiv preprint). Tehrani did not apply Chen's formula (no citation of it in the text); they screened on predicted B and G as the hardness proxy and discuss Pugh's ratio G/B only as a ductility indicator. (wiki/TARGET_RECOMMENDATION.md says they used G/B as a hardness proxy as well; the paper text does not support that part, see the audit.) The Hv error of the Magpie SVR route (2.84 GPa) therefore reflects *our* composition of the two, not a published number.

## 3. Verification table (every number quoted from a paper)
| # | quantity | value used here | source | status |
|---|---|---|---|---|
| 1 | moduli extracted from Materials Project | 3248 | Tehrani 2018, Experimental Methods, "Data Extraction and Machine-Learning Training Model" | verified (audit) |
| 2 | final training set | 2572 | same paragraph | verified (audit) |
| 3 | descriptors | 150 = 34 compositional variables (with expressions) + 14 structural | same section | verified (audit) |
| 4 | cross-validation | 10-fold (SVR training); 20-fold random split only for descriptor selection; grouping of folds not described | same section | verified (audit); absence of grouping = not found in the text, actual folds unknown |
| 5 | B: RMSECV, r^2 | 17.2 GPa, 0.94 | Results, discussion of Figure 1a | verified (audit) |
| 6 | G: RMSECV, r^2 | 16.5 GPa, 0.84 | Results, discussion of Figure 2a | verified (audit) |
| 7 | Chen hardness formula | Hv = 2 (k^2 G)^0.585 - 3, k = G/B | Chen, Niu, Li, Li 2011, Eq. (11) (arXiv:1102.4063v1, titled "Intrinsic Correlation between Hardness and Elasticity in Polycrystalline Materials and Bulk Metallic Glasses"; published as "Modeling hardness of polycrystalline materials and bulk metallic glasses", Intermetallics 19, 1275-1281) | verified for the preprint; published equation numbering unverified |
| 8 | matminer dataset size and reference | 2574 materials; cites Tehrani 2018 | matminer dataset metadata (`get_all_dataset_info("brgoch_superhard_training")`) | verified (audit); 2574 (matminer) vs 2572 (paper) difference unexplained |
| 9 | Mazhnik-Oganov hardness model: E = 9BG/(3B+G), nu = (3B-2G)/(2(3B+G)) (exact inversions of Eq. 7), H = 0.096 chi(nu) E, chi = (1 - 8.5 nu + 19.5 nu^2)/(1 - 7.5 nu + 12.2 nu^2 + 19.6 nu^3) | gamma_0 = 0.096, coefficients 8.5, 19.5, 7.5, 12.2, 19.6 | Mazhnik & Oganov, J. Appl. Phys. 126, 125109 (2019), doi 10.1063/1.5113622, Eqs. (7), (10), (11), pp. 125109-7/8 (author-hosted AIP-formatted PDF) | verified (audit 2026-10-22, see CITATION_AUDIT_COMPARISON.md); publisher-hosted copy not compared |
| 10 | Tian hardness model H = 0.92 k^1.137 G^0.708, k = G/B | 0.92, 1.137, 0.708 | Tian, Xu, Zhao, Int. J. Refract. Met. Hard Mater. 33, 93-106 (2012) | **NOT verified at source** (original not retrievable; only a later paper attributes the formula to Tian). Not used in any figure: the Tian oracle line is omitted. wiki/BASELINES.md still lists Tian 1.14 as our computation with unverified coefficients |
| 11 | Chen's RMSE on Mazhnik-Oganov's dataset | 4.4 GPa | Mazhnik & Oganov 2019, Table I, p. 125109-4 | verified (audit 2026-10-22); not used in any figure |

Every Tehrani figure above was read from the NSF-PAR copy (par.nsf.gov/servlets/purl/10094086; it carries the journal's page numbers, but whether its body is identical to the published version is unverified). The published ACS article (doi 10.1021/jacs.8b02717) was verified for metadata only, so a number could differ there.

## Reproduce
`uv run python eval/metrics_extra.py --all` (writes `ledger/baseline_val_preds.csv`), then `uv run python scripts/bg_errors.py --git-ref origin/t1/wed`.
