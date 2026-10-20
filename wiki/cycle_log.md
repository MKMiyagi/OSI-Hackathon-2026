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
