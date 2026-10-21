# Target decision (#2): T1 recommendation, 2026-10-21 11:00

## Update 14:30: the experiment changed the recommendation
Final recommendation: **keep `hv_chen` as the frozen target and search it directly, as now**, framed as a compact
composition-based emulator of the DFT-derived Chen proxy. **Add d_023 (cohesive-energy density) to the search.** Run the
Zhang 2021 measured-Hv external check once on Thursday. Drop the Chen(B, k) search route proposed below: in the
experiment (wiki/T1_ROUTES.md) it added nothing beyond d_023.
Evidence, 3 seeds, same settings in every arm, formula picked on train:
- direct + d_023 vs direct Magpie-only: c<=12 3.79 vs 3.92, c<=15 3.62 vs 3.85. Seed-stable.
- Splitting into B and k only helps once B gets d_023, and then it roughly matches direct + d_023.
The morning text below is kept as the record of the original argument.


**Recommendation: keep `hv_chen` as the frozen *evaluation* target, switch the *search* to B and G (Hv = Chen of the
two formulas), and add Zhang 2021 measured Hv as an external check scored once on Thursday.**
Nothing frozen changes: same splits, same `score.py`, same val MAE vs `hv_chen`, so every ledger row stays comparable.

## Evidence (all val numbers: fit on train, scored once on val; script and output in branch t1/tehrani-baseline)
| predictor (composition-only unless noted) | val MAE vs hv_chen (GPa) |
|---|---|
| train-median constant | 5.04 |
| best direct-SR formula, c8 / c12 / c15 (val reused for selection) | 4.03 / 3.77-3.91 / 3.79-3.89 |
| B, G each from one descriptor, `M = a (E_coh/V)^b`, then Chen | 4.45 |
| Magpie SVR -> log B, log G -> Chen | 2.84 |
| Magpie SVR direct on hv_chen | 2.82 |
| Tehrani's 150 features (18 structure-derived, NOT composition-only) -> B, G -> Chen | 2.75 |

1. **Direct SR on hv_chen loses to the real baseline by ~1 GPa.** Formulas close only about half of the constant-to-SVR gap.
   A 15-node formula has to reproduce both composition -> moduli *and* Chen's G^1.76 B^-1.17 nonlinearity.
2. **B is learnable from composition with a law.** Train-only fit: **B = 3.26 (E_coh/V)^0.994 GPa** (E_coh = composition-
   weighted Kittel cohesive energy, V = Magpie mean volume, E/V in eV/A^3 x 160.2). The exponent is 1 as dimensional
   analysis predicts (modulus ~ energy density). Val R^2 0.81 (development-set figure) from one descriptor; SVR gets 0.91, so there is room for
   corrections. It is the first quantity in the project with the target's units.
3. **The B,G route costs nothing in accuracy:** SVR via log B, log G -> Chen = 2.84 vs 2.82 direct.
4. **What's missing is the Pugh ratio.** With B and G both ~ E_coh/V, k = G/B is constant and Chen gives 4.45. So the
   search splits into a *scale* (E_coh/V, GPa) times a dimensionless *bonding-character* term setting k, which is exactly
   where the electronegativity / d-electron / bond-count descriptors belong. Hv = 2 (k^3 B)^0.585 - 3.
5. **The circularity objection goes away.** We do not "beat Chen"; Chen is the physics layer, and SR learns the two DFT
   observables Chen needs. B and G are DFT outputs, not derived labels.

## Why not the other two options
- **(a) keep hv_chen and keep searching Hv directly:** honest as an emulator (the round-3 reviewer's pick), but the
  headline is then "a formula 1 GPa worse than an SVR at reproducing a proxy". Option (b) keeps (a)'s target and metric.
- **(c) switch to measured Hv:** a full reset with one day left. Zhang et al. 2021 (Adv. Mater. 33, e2005112; data
  github.com/ziyan1996/VickersHardnessPrediction, `hv_comp_load.xlsx`, **no license, cite only**) has 1062 rows,
  529 compositions, load-dependent (0.0015-49 N, mostly 0.49-4.9 N; e.g. Al3BC3 20.7 GPa at 0.25 N vs 11.1 at 10 N).
  The load-handling choice alone would need its own frozen protocol.
- **(c) as an external check instead:** 364/529 Zhang compositions have element sets absent from train+val (76 are
  in train+val). Scored once Thursday, it answers the non-circular question: does Chen(B-formula, G-formula) track
  *measured* hardness, and how does Chen on DFT B,G do on the same rows (Mazhnik & Oganov 2019 report Chen RMSE 4.4 GPa
  on 45 crystals)? Rules: freeze cleaning before looking at predictions (strip whitespace; score per load bin, headline
  ~1 N); never use it for selection. Only metadata has been looked at so far; no predictions compared.

## Correction to CLAUDE.md / README
Tehrani 2018 did **not** apply Chen (or Teter). The accepted manuscript (par.nsf.gov/servlets/purl/10094086) does not
cite Chen 2011. It predicted B and G (Materials Project VRH data, RBF-SVR, C=10, gamma=0.01, eps=0.1; CV r^2 0.94 / 0.84)
and used them plus G/B as hardness proxies. "Composition -> B,G -> Chen" is our construction, and the published model is
not composition-only (14 structural descriptors). Our reproduction (val r^2 0.95 / 0.83) matches.

## What it costs (fits tonight's overnight run)
1. A descriptor for E_coh/V (UNITS Pa); see wiki/HYPOTHESES_T1.md.
2. `eval/compose_hv.py`: pair B and k (or G) Pareto equations, Chen on val, MAE vs hv_chen. Do **not** run
   `score.py` on B/G/k runs: it would work, but `ledger/results.csv` has no target column, so B MAEs (~25 GPa)
   would be read as hv_chen MAEs by every ledger consumer.
3. No-descriptor reference arms for `--target bulk_modulus` and `--target shear_modulus`, 3 seeds each.
4. Thursday: test-set evaluation (T1, by hand) and the Zhang external check (T1, once).

If the team prefers (a), all of this still works as an extra arm; nothing in it touches the frozen files.
