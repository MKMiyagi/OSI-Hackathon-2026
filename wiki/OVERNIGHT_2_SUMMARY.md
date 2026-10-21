# Overnight 2 summary (branch agent/overnight-1, 2026-10-20)

Stop condition hit: 3 consecutive non-improving cycles (009, 010, 011). 5 cycles run (007-011) of max 10; queue item f (d_013) not run; no STOP file. Target is still hv_chen (Chen applied to DFT B,G), provisional (wiki/DECISIONS.md). Test set untouched.

## Search setup (hardened)
PySR niterations 22000, maxsize 15, procs 4, 900 s timeout, nested unary ops disallowed, m_MeltingT and m_SpaceGroupNumber excluded, seeds 0 and 1 (`deterministic=False`, so seeds do not make runs bit-reproducible). ~11 min per fit (678 s / 670 s for the d_003 pair, two fits in parallel).
Calibration note: your spec assumed niterations 300 would be slow. It was not: 300 iterations took 6-10 s per fit (the "40-second" overnight-1 fits were mostly Julia startup). I therefore raised the default to 22000 to hit the 8-12 min target (linear scaling ~25 ms/iteration). t003_s0/s1 (niter 300) remain in the ledger, not used as reference.
Cycle score = mean over 2 seeds of best val_mae at complexity <= 9; improvement needs >= 0.05 drop vs best so far. Reference (d_003, t003b_s0/s1): 4.1946 / 4.1946, mean 4.1946. Train-mean baseline 5.2589.

## Per-cycle results
| cycle | descriptor | seed0 best c<=9 | seed1 best c<=9 | mean | improved | selected by PySR? (Pareto pts using it, s0 / s1; lowest complexity) |
|---|---|---|---|---|---|---|
| ref | d_003 B/C/N/O fraction | 4.1946 | 4.1946 | 4.1946 | - | n/a |
| 007 | d_007 B/C/N fraction, no O | 4.1947 | 4.1946 | 4.1946 | no (1) | 4/13 (c11) / 0/13 |
| 008 | d_008 EN range max-min | 4.1946 | 4.0300 | **4.1123** | **yes (-0.082)** | 6/13 (c10) / 1/14 (c8) |
| 009 | d_009 min valence e- x fraction | 4.1947 | 4.1947 | 4.1947 | no (1) | 0 / 0 |
| 010 | d_010+d_011 harmonic covalent radius, r^-2.5 | 4.1946 | 4.1946 | 4.1946 | no (2) | 0 / 0 |
| 011 | d_012 Pugh proxy (Mendeleev spread) | 4.1946 | 4.2489 | 4.2218 | no (3) | 0 / 7/13 (c9) |

Best overall val_mae per run (any complexity <= 15) sits at 3.89-3.98 in every cycle including the reference; those are not in the cycle score.

## Honest read
- Only one cycle improved: 008 (EN range). The improvement comes from ONE seed: seed 1 found `m_NUnfilled + exp((5.9447 - m_Row) - d_008)` (c8, val 4.0300). Seed 0 at c<=9 returned to the same 4.1946 Magpie equation, although it also selected d_008 at c10+ (c10 val 3.9671 inside a different expression). So d_008 is the only descriptor with a plausible signal, supported by 2 seeds in selection but 1 seed in the score. A single improving seed at a 0.05 threshold is not strong evidence; it needs more seeds and a paired with/without ablation.
- The c<=9 metric is nearly degenerate: in 4 of 5 cycles both seeds converge to the identical equation `MendeleevNumber/(GSvolume*NValence)+NUnfilled` (4.1946). The score only moves if a descriptor displaces that equation, so non-improvement mostly means "not selected below complexity 10", not "worse".
- Differences at c10-15 (3.89-3.98 across all cycles, including the d_003 reference) are search noise; d_007's best 3.8898 does not beat the reference's 3.8923 meaningfully.
- Excluding m_MeltingT/m_SpaceGroupNumber raised the reference from ~3.97 (overnight 1) to 4.19; the earlier "gain" leaned on non-physical MeltingT features.
- Target remains Chen-derived from DFT B,G; formulas are fits to Chen's output. Fitted forms (e.g. exp(-d_008) combined with Row and NUnfilled) are dimensionless-in-form with implicit GPa calibration, not dimensionally derived laws. Repeated selection against val risks val-overfit; the d_012 scale constant (10) was fixed a priori, not tuned.
- Descriptor d_007 control: d_003's signal is neither confirmed nor refuted (O removal changed nothing at c<=9).

## Descriptor families
- Electronegativity spread: d_008 (range) is the only live lead; d_001/d_005 earlier.
- B/C/N light-element fraction (d_003/d_007): no evidence at c<=9.
- Min valence-electron count (d_009): never selected. Note tie-handling flaw (first minimum wins).
- Harmonic covalent radius (d_010/d_011): never selected; reviewer says retire (needs structure-derived bond lengths). FAILED.
- Pugh proxy (d_012): selected by one seed but worse than Magpie-only at c<=9; heuristic scale constant. Weak.
- Not run: d_013 (O-corrected valence electron density; closest to the d_002 family not selected in overnight 1).

## Reviewer notes (codex, regular tier, one per cycle)
No direct leakage found in any cycle. Recurrent: coarse composition proxies ignore structure/stoichiometry; fitted equations have implicit GPa calibration; repeated val selection can overfit; with/without comparisons are across different searches, not controlled ablations.

## Recommended next
1. Validate d_008 properly: >= 5 seeds, paired with/without-d_008 searches, and report c<=9 mean+-sd before believing it.
2. Replace the c<=9 knee metric or add a complexity-matched ablation, since it saturates at one Magpie equation.
3. Revisit the target (experimental Hv) Wednesday; Chen-derived labels limit what any composition-only formula can claim.
