# Pitch outline (6 slides) — DRAFT for T2

All MAEs are development-set (val, reused) numbers unless a slide says otherwise. Target is `hv_chen`, not measured hardness.

1. **Problem:** Hardness needs DFT moduli, so can a short composition-only formula emulate the DFT-derived Chen proxy, and how close does it get to a black box?
2. **Protocol:** Element-set-grouped 70/15/15 split frozen first, test file quarantined outside the repo with a committed hash, fixed metric, 3 seeds per cycle against a stored 9-seed reference.
3. **What formulas reach vs the black box:** A 9-node formula gets val MAE ~4.0 GPa against 5.04 for a constant and 2.82 for the Magpie-SVR (B,G) -> Chen pipeline, about half the gap, still ~1 GPa short.
4. **The reviewer loop:** A second model (Codex) reviews every cycle; it caught that the c<=9 score was saturated (9 seeds, same equation, sd 0.0001), so we switched to a c<=12 multi-seed headline.
5. **The d_023 formula:** `d_023 / (NdValence + 2.376)` with d_023 = cohesive-energy density scores 3.90 at c5 and reads as stiffness (energy per volume) divided by a metallicity term, but it overpredicts Al, W, Cu and NaCl and is still a lead pending the formal cycle.
6. **Limits and next:** Labels are Chen's own output, val is reused, and the tail (>= 20 GPa) is poorly fit, so next we run the one-shot test (TODO Thursday) and the Zhang measured-Hv check (TODO Thursday), then nested CV and a metallicity descriptor.
