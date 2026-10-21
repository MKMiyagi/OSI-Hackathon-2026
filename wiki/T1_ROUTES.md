# T1 experiment: cohesive-energy density (d_023) and the Chen(B, k) route — 2026-10-21

Final: 3 seeds per arm, 18 fits, no failures.
Development-set (val) numbers. Every formula was picked on **train** within its complexity budget, then scored once on
val (`eval/compose_hv.py`, train-selected), so there is no val selection inside an arm. Figure: `wiki/figures/t1_routes.png`.

## Setup
6 arms x 3 seeds (`scripts/t1_queue.sh`). All arms use the same settings: L1 loss, `--units`, maxsize 15, procs 4,
900 s per fit, 3 fits in parallel on T1's laptop. The timeout binds first, so each fit completes only ~4-5k of the 22k
requested iterations; every arm gets the same wall-clock budget. Arms:
- direct on hv_chen: Magpie only (t1_hv), and + d_023 (t1_hvd23)
- B: Magpie only (t1_B), and + d_023 (t1_Bd23)
- k = G/B: Magpie only (t1_k), and + d_008 (t1_kd08)
- composed: Hv = Chen(k B, B); the budget counts c_B + c_k
**Leakage checks:** d_023 is finite for all 1746 train and 374 val rows (0 NaN). In the Chen route, B and k are
predicted from composition by the fitted equations; true DFT B, G and k are never inputs to an Hv prediction
(wiki/REVIEW_PR12.md, Codex risk 1; see the eval/compose_hv.py docstring).
**Search-depth check:** the Magpie-only direct arm at ~4-5k iterations nearly coincides with the stored 22k-iteration
9-seed reference (figure, gray vs blue). The shorter search is not what makes d_023 look good.

## Result (mean +- sd over 3 seeds, val MAE in GPa)
| route | c<=9 | c<=12 | c<=15 |
|---|---|---|---|
| direct, Magpie only | 4.16 | 3.92 | 3.85 +- 0.09 |
| **direct + d_023** | **3.98** | **3.79** | **3.62 +- 0.04** |
| Chen(B + d_023, k Magpie) | 3.91 | 3.75 +- 0.05 | 3.66 +- 0.02 |
| Chen(B + d_023, k + d_008) | 3.91 | 3.78 | 3.71 +- 0.05 |
| Chen(B Magpie, k Magpie) | 4.49 | 4.12 | 4.12 |

1. **d_023 lowers the whole direct front:** -0.18 GPa at c<=9, -0.14 at c<=12, -0.22 at c<=15. It is selected in
   every seed. Best single fit 3.60 at c15 (t1_hvd23_s2), a new project best (previous 3.79). This
   clears the CLAUDE.md bar (>= 0.08, majority selection) against the same-settings Magpie arm, though not yet under
   the formal protocol (stored 22k L2 reference); that is cycle 020 in wiki/OVERNIGHT_4_PROPOSAL.md.
2. **The front is seed-stable.** All 3 seeds find algebraically equivalent equations at c3, c4, c5, c7, c9 and c10
   (constants agree to 4 digits, e.g. c5 `+ 2.3758 / 2.3757 / 2.3756`), and the same structure at c12. This is a stable
   optimum, not a lucky seed.
3. **Splitting into B and k adds nothing beyond d_023** (and d_008 in the k search does not help k). Chen(B, k) only helps when B gets d_023, and then it roughly
   matches direct + d_023 while using two searches.
4. **B: SR rediscovers B = 3.37 d_023 at c3** (val 23.5 GPa MAE). The hand fit was 3.26 d_023^0.994. Magpie-only B
   never gets below ~31 GPa.

## The formulas (direct + d_023, seed 0; d_023 in GPa)
| c | val MAE | formula |
|---|---|---|
| 3 | 4.17 | `d_023 / m_NValence` |
| 5 | **3.90** | `d_023 / (m_NdValence + 2.376)` |
| 7 | 3.77 | `d_023 / (m_NdValence + m_Electronegativity + 0.416)` |
| 11 | 3.83 | `d_023 / (m_NdValence + 3.157) + 0.638 m_NdUnfilled m_NpUnfilled` |
| 15 | 3.61 | `0.721 m_NpUnfilled m_NdUnfilled + d_023 / (m_NdValence + m_Electronegativity - 0.329 m_NUnfilled)` |
Reading: **hardness ~ cohesive-energy density divided by a d-electron (metallicity) term**, plus at c>=9 the recurring
p-d unfilled-state term from the Magpie-only fronts. The c5 law is dimensionally exact: d_023 carries GPa and the
constant 2.376 is a pure number. On val rows >= 20 GPa its MAE is 8.6 GPa vs 13.9 (Magpie c9) and 15.1 (d_008 c8).

## Where it fails (illustration on textbook materials, not a validation)
c5 gives diamond 88 GPa (~95 measured), SiC 31, TiC 26, WC 28, ReB2 27: right order for hard covalent compounds.
But it gives **Al 14 (~0.3), W 14 (~3.5), Cu 4 (~0.7), NaCl 3 (~0.2)**. The formula encodes stiffness (energy per
volume), not plasticity. Chen handles plasticity through k = G/B. The Chen(B, k) route fixes W and Cu (low predicted
k), but its Magpie k formula still gives Al k ~ 0.75, like Si. Next hypothesis: a metallicity indicator that
separates sp metals (Al) from covalent p-block (Si).
