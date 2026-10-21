# Round 3 review: are the candidate formulas physical laws, and is val reuse fatal?

Reviewer: Codex (gpt-6-astra, ultra), thread 01a15e9d-39b9-75d3-892a-f877f6abeb90. Brief: wiki/RESEARCH_REVIEW_REQUEST_3.md. Input to the noon target decision (issue #2).
Spot-checked by the executor (reproduced): 128/1746 train and 39/374 val labels negative; BN train targets 64.01 and 14.11; V5Si3 val targets 2.375 and 15.76; train-mean val MAE 5.2589, train-median 5.0442; 17 val rows >= 20 GPa; eval/baselines.py does not exist. Everything else below is the reviewer's claim, not independently re-run (bootstrap intervals, 94.74% concentration, tail MAEs, all-754-rows reproduction).

## Verdict
Recorded scores reproduce (reviewer re-scored all 754 rows). The train/val split has zero shared element-set groups and no direct target leakage was found. **No candidate is established as a physical law.** d_008 genuinely recurs (9 runs), but recurrence measures search stability, not predictive advantage. Val reuse (descriptor, equation and complexity-window choices all made on val) rules out confirmatory superiority claims but not descriptive ones. The best c12 candidate (c018_s0, 3.772) beats the strongest recurring Magpie c12 equation (3.911) by 0.139 GPa, and 94.7% of that comes from ten val rows; removing them leaves 0.008.

## Law or fit
- Fitted prefactors are not disqualifying on their own; the d_008 form can be stated consistently as H/GPa = N_unfilled + 381.7 exp(-(Row + chi_range)). But there is no derivation and the physical readings are post hoc.
- Two "Gao-like electron-density" readings are algebraically wrong: `1494/(Row*NValence*V)` and `642/(V*(NValence-NfValence))` have electron count in the DENOMINATOR. Remove those readings from CANDIDATE_FORMULAS.md.
- m_GSvolume_pa and m_GSbandgap are composition-weighted elemental values, not compound volume or gap, so success does not support the compound-level mechanism. Band gap (eV) and sqrt(eV) are mixed with dimensionless terms.
- d_017 came out with the opposite sign to the pre-registration: a failed hypothesis, not a new mechanism. d_018 is exactly d_008^2 (adds no information; any gain is a representation/complexity-budget effect). d_016 failing to reproduce d_008 does not refute the physics, and the Allen table was not shown to be wrong.
- No singularities or non-finite predictions in the shortlisted formulas on train/val.

## Target problem (independent of val reuse)
- Labels reproduce Chen 2(G^3/B^2)^0.585 - 3 to float precision, so "beats Chen" is incoherent on this target (README line 3 still says it).
- 128 train / 39 val labels are negative: valid Chen-proxy outputs, not physical hardness.
- Same composition, very different target (BN, V5Si3): any composition-only formula must predict one value per pair, so a universal composition-to-hardness law is not identifiable from these inputs.
- Tail: only 17 val targets >= 20 GPa. MAE on those 17: about 15.1 (d_008) and 10.1 (c018_s0) vs 4.03 overall. No superhard-screening story.

## Val reuse
- 9 seeds measure optimizer variation, not uncertainty over new families or selection optimism. Selection optimism cannot be computed from "754 equations" (correlated, adaptive).
- Descriptive post-selection bootstrap over 256 val groups (not corrected CIs): d_008 c8 vs Magpie c9 [-0.395, +0.060]; c018_s0 vs Magpie c12 [-0.392, +0.104].
- Surviving claims: best observed under this search config (not "ceiling"), recurrence of d_008, the saturation of the c<=9 metric. Not surviving: any "beats baseline on held-out families", d_017/d_018 gains (c12 means 3.9790 / 3.9815 vs reference 3.9802).

## Gaps found
1. Declared baseline (composition -> B,G -> Chen) is not implemented; only constant baselines exist. Add the train-median constant (5.0442) as a cheap comparator. (issues #4, #5)
2. `sr/cycle_summary3.py` does not implement the adopted rule: uses first 3 reference runs, reports c<=9/12 only, paired terminology, no selection-majority test. Needs a small fix.
3. Replace "Magpie ceiling" wording with "best observed under this search configuration" (README status, summaries).

## Recommendation for the noon decision
Choose **(a) keep hv_chen**, framed explicitly as a compact composition-based emulator of a DFT-derived Chen proxy. Freeze further descriptor search; spend remaining effort on credible evaluation (grouped nested CV with descriptor selection inside the loop; GSbandgap ablation; per-family errors; influence analysis for c018_s0) and corrected claims. (b) predicting B,G is a useful follow-up but gives no measured-hardness validation, and comparing Chen/Tian/Mazhnik-Oganov against Chen-made labels cannot rank them physically. Choose (c) measured Hv only if discovering a hardness law is a hard requirement; that resets the study and needs curated phases/conditions. The evidence supports a research-workflow demonstration, not a hardness law, superiority on independent families, or a NeurIPS/ICML-level contribution.

## Minimum extra evidence by claim
- Exploratory formula: no more search; fix readings, state units, label all MAEs as development-set.
- Predictive pipeline comparison: frozen protocol, grouped outer folds, all selection inside inner loop, compared with Magpie-only SR and the declared baseline.
- Independent confirmation: genuinely new labeled families (re-partitioning train+val does not make consulted labels fresh).
