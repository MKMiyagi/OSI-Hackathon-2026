# Overnight 1 cycle log
Knee metric = best val_mae among Pareto points (maxsize 12, niter 40). Reference before night: 4.2583 (smoke_001), train-mean baseline 5.2589.

## cycle 002 — d_002 valence electron density (m_NValence/m_GSvolume_pa), run c002
best val_mae 3.9996 (complexity 7, Magpie-only: MeltingT/Row^2). d_002 NOT selected by PySR. Improved vs 4.2583.
Reviewer (codex, medium): plausible, units OK (e/A^3), no leakage. Notes: ratio of means, PySR can already build it from existing features; nonselection doesn't refute physics; the MAE gain is not attributable to d_002. Caveat: target is Chen-derived.

## cycle 003 — d_003 light-element (B,C,N,O) atomic fraction, run c003
best val_mae 3.9709 (complexity 7, Magpie-only: MeltingT/Number + NpUnfilled). d_003 NOT selected. Improved vs 3.9996 (tiny; search noise, not attributable to d_003).
Reviewer (codex, medium): coarse but plausible; including O weakens rationale (ionic oxides) — test B/C/N separately; units fine; no leakage. No demonstrated incremental benefit.

## cycle 004 — d_004 d-block transition-metal fraction (metallicity proxy), run c004
best val_mae 4.0376 (complexity 9). d_004 NOT selected. NO improvement vs 3.9709 (non-improving streak 1/3).
Reviewer (codex, medium): weak metallicity proxy; hard TM carbides/nitrides/borides make negative sign non-universal; units fine; no leakage; docstring element-range wording misleading (fixed). Sign is a hypothesis, not a constraint.

## cycle 005 — d_005 Gao ionicity penalty exp(-1.191 f_i), run c005
best val_mae 3.9753 (complexity 10; USES d_005: sqrt(MeltingT)/(Row-(d_005+0.1786)) - 4.755). NO improvement vs 3.9709 (streak 2/3). First descriptor PySR actually selected.
Reviewer (codex, medium): plausible Gao-style covalency proxy, ignores stoichiometry/bond density; dimensionless; fitted equation not dimensionally explicit (sqrt(K) mixed with dimensionless; sqrt(MeltingT) has no unit-consistent meaning); possible unstable denominator (Row - d_005 - 0.18); no leakage. No demonstrated incremental benefit.

## cycle 006 — d_006 n_e^(2/3)·exp(-1.191 f_i) (Gao composite), run c006
best val_mae 4.0475 (complexity 12). d_006 NOT selected. NO improvement vs 3.9709 (streak 3/3 -> STOP condition).
Reviewer (codex, medium): heuristic, not faithful Gao (averaged elemental volumes, range-only ionicity); output units (e/A^3)^(2/3) not GPa; no leakage; note added descriptors can change the joint finite-row filter; recommends pausing this family.

# Overnight 2 (hardened search: niter 22000, maxsize 15, seeds 0/1, m_MeltingT & m_SpaceGroupNumber excluded; ~11 min/fit)
Cycle score = mean over 2 seeds of best val_mae at complexity <= 9. Improvement needs >= 0.05 drop vs best previous. Reference = d_003 under this search (t003b_s0/s1): 4.1946 / 4.1946, mean 4.1946. (Calibration note: at niter 300 a fit took 6-10 s, not minutes; niter was raised to 22000 to hit the 8-12 min target. t003_s0/s1 at niter 300 are kept in the ledger, c<=9 best 4.111 / 4.134, not used as reference.)

## cycle 007 — d_007 B/C/N fraction, O excluded, runs c007_s0 / c007_s1
Per-seed best c<=9: 4.1947 / 4.1946, mean 4.1946; NO improvement (streak 1/3). d_007 NOT selected at c<=9 in either seed. Seed 0 used it at c11, c13-15 (e.g. exp(d_007)*m_NUnfilled, c15 val 3.8898 vs reference 3.8923 at c15: indistinguishable); seed 1 never.
Both seeds (and the reference) converge to the same c<=9 equation (MendeleevNumber/(GSvolume*NValence)+NUnfilled), so c<=9 scores are nearly deterministic: the metric cannot move unless a descriptor displaces that equation.
Reviewer (codex, regular): composition-only, dimensionless, no leakage; physically plausible but non-specific (cannot distinguish allotropes; excluding O may drop relevant compounds); no c<=9 evidence either way on whether O drove d_003 (the d_003 signal is not shown to be real or fake).

## cycle 008 — d_008 Pauling electronegativity range (max-min), runs c008_s0 / c008_s1
Per-seed best c<=9: 4.1946 / 4.0300, mean 4.1123; IMPROVED by 0.082 vs 4.1946 (streak reset to 0). The gain is ONE seed: seed 1 found c8 `m_NUnfilled + exp((5.9447 - m_Row) - d_008)` (val 4.0300), selecting d_008. Seed 0 at c<=9 reverted to the usual Magpie equation (4.1946, d_008 unused) but selected d_008 at c10-15 (c10 val 3.9671, `162.18/((m_NdValence*exp(d_008)) + m_GSvolume_pa - m_NUnfilled)`), outside the c<=9 scoring window. So d_008 was selected in both seeds, but the cycle score rests on one seed.
Reviewer (codex, regular): composition-only, no leakage; plausible polarity proxy, docstring overclaims (extreme elements need not bond), stoichiometry ignored; exp(-d_008) dimensionally valid (dimensionless Pauling units, implicit 1-unit decay scale) but fitted formula needs implicit GPa calibration; the with/without comparison is across different searches, not a controlled ablation; seed-sensitive association, not established ionicity physics; repeated val selection can overfit.

## cycle 009 — d_009 min valence-electron count x its atomic fraction, runs c009_s0 / c009_s1
Per-seed best c<=9: 4.1947 / 4.1947, mean 4.1947; NO improvement vs best 4.1123 (streak 1/3). d_009 NOT selected: it appears in no Pareto equation of either seed.
Reviewer (codex, regular): composition-only, no leakage; units OK (electrons/atom). Flagged: ties in NValence pick the first constituent (order-dependent when tied elements have different fractions) — known minor flaw, not fixed (descriptor failed anyway); trace constituents can switch the selected minimum abruptly; low NValence does not establish weakest bonding. min_i(x_i N_i) or sum_i x_i N_i are alternative readings. Non-selection shows no utility in this search, not physical invalidity.

## cycle 010 — d_010 (harmonic-mean covalent radius, A) + d_011 (r_h^-2.5), runs c010_s0 / c010_s1
Per-seed best c<=9: 4.1946 / 4.1946, mean 4.1946; NO improvement vs best 4.1123 (streak 2/3). Neither d_010 nor d_011 selected in any Pareto equation of either seed.
Reviewer (codex, regular): composition-only, no leakage; units correct (A; A^-2.5, not GPa); harmonic radius is a weak bond-length proxy (ignores pairwise radius sums, connectivity, coordination; Gao also needs electron density/covalency). Recommends RETIRING this family unless structure-derived bond lengths become available. Marked failed.

## cycle 011 — d_012 Pugh proxy k=1/(1+10*MAD(MendeleevNumber)/103), runs c011_s0 / c011_s1
Per-seed best c<=9: 4.1946 / 4.2489, mean 4.2218; NO improvement vs 4.1123 (streak 3/3 -> STOP). Seed 0 never used d_012. Seed 1 used it at c9-15 (7/13 Pareto points), but its c<=9 best (4.2489) is WORSE than the Magpie-only 4.1946; its c14 reached 3.9587 (outside the window).
Reviewer (codex, regular): heuristic, not an established G/B estimator; dimensionless; no direct leakage; the scale 10 (and 103) is an undocumented hyperparameter, i.e. an implicit fit if tuned on val (it was fixed a priori here, not tuned); c<=9 evidence negative.

STOP: 3 consecutive non-improving cycles (009, 010, 011). Queue item f (d_013, O-corrected valence electron density) not run. No STOP file; time ~22:30 local, before 06:00.

# Overnight 3 (see wiki/OVERNIGHT_3_SUMMARY.md when written)
Phase 1 (d_008 ablation, 5 seeds) and Phase 2 (9 reference seeds): see wiki/D008_VALIDATION.md and wiki/DECISIONS.md "Metric". Reviewer (codex regular) on D008_VALIDATION: numbers reproduce; verdict softened, unpaired Welch CIs added, pairing caveat, textual-vs-algebraic structure caveat; no leakage seen.

## cycle 012 — d_014 sum x_i (chi_max - chi_i), runs c012_s0/s1/s2 (3 seeds; scores c<=9 and c<=12)
Best c<=9 per seed 4.1946/4.1947/4.1947, mean 4.1947 (paired vs v008_wo s0-2: -0.0001). Best c<=12 3.9114/3.9114/3.9732, mean 3.9320 (paired -0.048, i.e. the same Magpie-only equations the reference finds; not attributable to d_014). Selected: seeds 1 and 2 (min complexity 8, `m_NUnfilled + 262.79/exp(d_014 + m_Row)`, val 4.3247 — worse than the Magpie c9 4.1946 and than d_008's same-form c8 4.0300); seed 0 never.
Reviewer (codex regular): plausible heuristic, dimensionless, no leakage (composition-only; repeated val selection risk); trace high-chi constituents move chi_max; no demonstrated gain; deprioritize.

## cycle 014 — d_016 Allen-scale EN range, runs c014_s0/s1/s2
Best c<=9 4.1946/4.1947/4.1946, mean 4.1946 (paired vs v008_wo -0.0001); best c<=12 3.9114 x3, mean 3.9114 (paired -0.069; the same Magpie-only c12 equation in all seeds, not attributable to d_016). Selected: seed 0 only, min complexity 10 (`m_NUnfilled + 301.13/exp(m_Row + d_016/m_NsValence)`, val 4.107); seeds 1, 2 never. Scale test: the Allen-scale EN range does NOT reproduce d_008's c8 selection (d_008: 3/5 seeds at c8, val 4.030), so the d_008 effect is scale-sensitive or fragile.
Reviewer (codex regular): plausible, composition-only, no leakage; spot-checked ~10 Allen values (H, C, O, Cl, Ti, Fe, Mo, W, Ag, Au) correct, none found wrong (table typed from memory; not fully verified); weak evidence; favors d_008 provisionally.

## cycle 015 — d_008 + d_007 jointly (EN range + B/C/N fraction), runs c015_s0/s1/s2
Best c<=9 4.0300/4.0300/4.1946, mean 4.0849 (paired vs v008_wo -0.110; identical to the d_008-alone result, 3/5 seeds there); best c<=12 4.0300/3.9172/4.0520, mean 3.9997 (paired +0.020). d_008 selected at c8 in seeds 0 and 1 (same equation `381.7/exp(Row + d_008) + NUnfilled`, val 4.0300); seed 2 never. d_007 appears only at c>=11: seed 1 c11 `((307.79/exp(Row+d_008)) + NUnfilled)*exp(d_007)` val 3.9172 (the best c<=12 of the cycle, one seed), seed 0 c12 `(d_008 - d_007)/NsValence` inside the exponent (val 4.0875, worse than c8). 
Reviewer (codex regular): does not establish an EN x light-element interaction; d_007 contributes nothing at c<=9; the 3.9172 rests on one seed; compatible with search noise; exp(d_007) dimensionless so GPa preserved but coefficients implicit; no leakage; needs fixed-complexity ablation and family-held-out validation.

## cycle 016 — d_013 O-corrected valence electron density (alone), runs c016_s0/s1/s2
Best c<=9 4.2071/4.1947/4.1947, mean 4.1988 (paired vs v008_wo +0.004); best c<=12 3.9770/4.0522/3.9769, mean 4.0020 (paired +0.022). d_013 NOT selected in any Pareto equation of any seed; results equal the no-descriptor reference (seed 0's c9 4.2071 is a different Magpie-only form, noise).
Reviewer (codex regular): units e/A^3 correct, 11.494 A^3 constant correct, composition-only, no leakage; mixing Shannon ionic volume with elemental volumes is a heuristic, not a consistent crystal volume; no demonstrated value; deprioritize (does not show physical invalidity).
