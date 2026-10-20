# Overnight 1 summary (branch agent/overnight-1, 2026-10-20)

Stop condition hit: 3 consecutive cycles (004-006) without val-MAE improvement. 5 cycles run (002-006) of max 6; no STOP file; target = hv_chen (Chen applied to DFT B,G), provisional (wiki/DECISIONS.md).

Train-mean baseline val MAE: **5.2589 GPa**. Pre-night manual reference (smoke_001, d_001 unused): 4.2583.

## Best val_mae per cycle (PySR maxsize 12, niter 40; one seed, single run each)
| cycle | descriptor | selected by PySR? | best val_mae (complexity) | best at c<=6 | best at c<=9 |
|---|---|---|---|---|---|
| 001 (manual) | d_001 EN mean abs deviation | no | 4.2583 (11) | 4.353 | 4.327 |
| 002 | d_002 valence e-density NValence/GSvolume | no | 3.9996 (7) | 4.377 | 4.000 |
| 003 | d_003 B/C/N/O atomic fraction | no | **3.9709 (7)** | **3.981** | **3.971** |
| 004 | d_004 d-block TM fraction | no | 4.0376 (9) | 4.373 | 4.038 |
| 005 | d_005 Gao ionicity penalty | yes (c10) | 3.9753 (10) | 4.402 | 4.055 |
| 006 | d_006 n_e^(2/3)·exp(-1.191 f_i) | no | 4.0475 (12) | 4.402 | 4.075 |

Knee: best compact equation is c003 complexity 5, `m_MeltingT / (m_Number / 0.125)` val MAE 3.981 (-24% vs baseline), Magpie-only. Simple features carry nearly everything: `sqrt(m_MeltingT/m_Number)` (c4, 4.40) recurs across runs.

## Honest read
- The gains over the baseline come from Magpie-mean features (MeltingT, Number, Row), **not** from my descriptors: only d_005 was ever selected, at complexity 10, with no MAE gain. Differences between cycles (~0.03-0.08 GPa) are within PySR search noise (single seed) and are not evidence for or against any descriptor.
- Target is Chen applied to DFT B,G, so fitting it is circular w.r.t. "beating Chen"; reviewers flagged this repeatedly. Formulas contain sqrt(MeltingT)-type terms that are not dimensionally meaningful.
- Repeated selection against val risks val-overfit; test (quarantined) untouched.

## Descriptor families tried
1. Covalency/electronegativity spread (d_001, d_005): d_005 only one selected, no gain.
2. Bonding electron density (d_002, d_006): not selected; redundant with Magpie means.
3. Light-element fraction (d_003): not selected; O inclusion questioned.
4. Metallicity via TM fraction (d_004): not selected; sign non-universal (WC, TiN).

## Reviewer objections (codex, medium tier, one per cycle)
Descriptors are coarse composition proxies; ratios of means are reconstructible by PySR (no incremental benefit); O in d_003 weakens rationale; TM sign non-monotonic; d_005 fit not dimensionally consistent and denominator Row-(d_005+0.18) may be unstable; d_006 output not in GPa; no direct leakage found in any cycle; recommended pausing the Gao-composite family.

## Recommended next hypotheses
1. **Fix the search before more descriptors:** multiple seeds / niterations>=200 per descriptor set, report mean±sd; otherwise cycle comparisons are noise. Consider a unit-aware or restricted feature set (drop MeltingT/SpaceGroupNumber, which are non-physical for hardness).
2. B/C/N fraction separate from O (reviewer suggestion); per-element nonlinear features PySR cannot build from means: max/min of electronegativity, weighted harmonic mean of covalent radii (bond length), fraction-weighted min valence-electron count.
3. Pugh-like proxies from composition (predict G/B via Mendeleev-number spread) before Chen, i.e. mimic Tehrani's two-stage structure with a compact formula.
4. Revisit target on Wednesday (experimental Hv rather than Chen-derived) — likely changes which descriptors matter.
