# Cycle 020 (run on T1's laptop): d_023 cohesive-energy density — IMPROVEMENT under the adopted rule

Runs `t1_c020_s0..s2`, 2026-10-21 14:57-15:40. Scored with `scripts/t1_cycle_score.py`, which applies
`sr/cycle_summary3.py`'s own functions to rows scored in memory exactly as `eval/score.py` would. Not appended to
`ledger/results.csv` (agent-owned); the score row is in `ledger/t1_cycle_scores.csv`.

## Settings: the standard CLAUDE.md cycle, one change
Defaults: L2 loss, no units, niterations 22000, maxsize 15, procs 4, MeltingT/SpaceGroupNumber hidden, 3 seeds in
parallel. **Change:** the timeout was raised from 900 to 6000 s so all 22k iterations complete on this slower machine
(the stored reference runs completed 22k on the agent machine). Fits took 2556-2587 s and stopped on iterations,
not the timeout (last progress lines 21954-21986/22000). d_023 has no NaN rows (val 0/374, train 0/1746).

## Result (official headline: best val MAE within each complexity window, mean over 3 seeds)
| window | cycle 020 per seed | mean | stored 9-seed reference | difference |
|---|---|---|---|---|
| c<=9 | 3.6939 / 3.6939 / 3.6939 | **3.6939** | 4.1947 (sd 0.0001) | **-0.501** |
| c<=12 (headline) | 3.6838 / 3.6939 / 3.6939 | **3.6905** | 3.9802 (sd 0.0609) | **-0.290** (~4.8 sd) |
| c<=15 | 3.6482 / 3.6482 / 3.6577 | **3.6514** | 3.9273 (sd 0.0382) | **-0.276** |
Selected in 3/3 seeds (first use at complexity 2). **Improvement = True: the first descriptor in the project to pass
the adopted rule** (>= 0.08 GPa drop and majority selection). It reproduces the afternoon's L1/`--units` experiment
under the frozen protocol (wiki/T1_ROUTES.md).

## The formulas (identical in all 3 seeds up to rounding of constants)
| c | val MAE | formula |
|---|---|---|
| 2 | 4.568 | `sqrt(d_023)` |
| 3 | 4.174 | `d_023 / m_NValence` |
| 5 | 3.908 | `d_023 / (m_NdValence + 2.461)` |
| 7 | 3.841 | `d_023 / (m_NdValence + 2.962) + m_NpUnfilled` |
| **8** | **3.694** | **`d_023 / (m_NdValence + sqrt(m_Column)) + m_NpUnfilled`**: no fitted constants |
| 13 | 3.648 | `d_023 / (m_NdValence + log(m_Row) + m_Electronegativity) + m_NpUnfilled * sqrt(m_NdUnfilled)` |
**Reading of the c8 law:**
- The first term is the energy density softened by d electrons and by group number: metallic, non-directional
  bonding dilutes the cohesive energy that resists shear.
- `m_NpUnfilled` adds hardness for unfilled p states (directional covalent bonding, B/C/N/Si chemistry).
- **Caveat:** adding a count to a GPa term carries an implicit 1 GPa coefficient, so this is not strictly
  unit-consistent. The c5 law has no such term.

## Caveats
- These are development-set numbers: the window-best convention picks equations on val, and val was reused.
  Thursday's test set gives the unselected number.
- Run on a different machine from the reference. The settings and iteration count match, but PySR here runs with
  `deterministic=False`.
- The known failure mode stands: these laws encode stiffness and overpredict simple metals (wiki/T1_ROUTES.md).
- Still about 0.8 GPa above the black-box SVR (2.82-2.91).
