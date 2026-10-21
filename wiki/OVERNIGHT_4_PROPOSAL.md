# Overnight 4 proposal (T1, 2026-10-21) — for Matthew to accept, edit or reject

**Dependency:** met. PR #12 was merged 2026-10-21 14:50, so d_023-d_027 and the `run_pysr.py` flags are on main.

## Why
T1's afternoon experiment (wiki/T1_ROUTES.md) found that **d_023 = cohesive-energy density** lowers the whole direct-Hv
Pareto front. It came from 3 seeds at ~4-5k iterations, L1 loss and `--units`, on T1's laptop. That is not the adopted
cycle protocol, so it does not count under the CLAUDE.md rule yet. Tonight's job is to test it under that protocol.

**Update 15:45: cycle 020 PASSED** (wiki/CYCLE_020_T1.md). d_023, default settings, all 22k iterations, 3 seeds on T1's
laptop: headline c<=12 **3.691** vs reference 3.980 (-0.29, ~4.8 sd); c<=9 3.694 (-0.50); c<=15 3.651 (-0.28); selected
3/3. All seeds find the constant-free c8 law `d_023 / (m_NdValence + sqrt(m_Column)) + m_NpUnfilled`. Scored with the
CLAUDE.md rule, not appended to ledger/results.csv. **The agent should start at cycle 021** (rerunning 020 on its own
machine is an optional replication). With d_023 established, the follow-ups below test what adds to it.

## Queue (in priority order; standard CLAUDE.md cycle unless noted)
| cycle | descriptors | settings | purpose |
|---|---|---|---|
| 020 | d_023 | defaults (L2, no units, niter 22k), 3 seeds | **the decisive test** vs the stored 9-seed reference (c<=12 mean 3.980 +- 0.061) |
| 021 | d_023 + d_027 | defaults, 3 seeds | E_coh spread (weakest link): the most novel of H2-H5 |
| 022 | d_023 + d_008 | defaults, 3 seeds | does the recurring EN-range term add to the energy density? |
| 023 | d_023 + d_025 | defaults, 3 seeds | size mismatch (interstitial compounds) |
| 024 | d_023 | `--units --dimensionless-constants`, 3 seeds | physics-constrained search: Hv must be d_023 x f(dimensionless). Not comparable to the reference; report separately |

Not queued: d_024 (rank-identical to d_010) and d_026 (~ m_NValence); see wiki/HYPOTHESES_T1.md. Nor the
Chen(B, k) route: at equal settings it did not beat direct + d_023.

## Rules that change
- Do **not** run `eval/score.py` on B/G/pugh_k runs (ledger has no target column). Hv-target cycles as usual.
- Stop rule unchanged: 3 consecutive non-improving cycles, 10 cycles, or 06:00.
- Cycle 024 uses non-default flags, so log its rows with a note. Its headline is not compared with the reference.

## Thursday (T1)
1. Freeze the candidate list for the test set before running it. Use `eval/test_once.py`, rehearsed on val first.
2. Run the Zhang measured-Hv check once: `eval/external_zhang.py ... --score --confirm-one-shot`.
