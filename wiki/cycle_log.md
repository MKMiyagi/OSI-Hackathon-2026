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
