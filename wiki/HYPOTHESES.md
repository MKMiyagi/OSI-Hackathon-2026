# Hypothesis queue — overnight 2 (follow in order; one cycle each, cycles 007+)

Each cycle: 2 seeds, score = mean of best val_mae at complexity <= 9 (sr/cycle_summary.py).
Improvement = mean drops >= 0.05 GPa vs best previous cycle (reference = d_003 under the hardened search, runs t003b_s0/s1).
Families marked failed in wiki/ (OVERNIGHT_1_SUMMARY, cycle_log) are skipped: the Gao-composite family (d_005, d_006; reviewer recommended pausing) is NOT in this queue. TM-fraction (d_004) is also not repeated.

| cycle | descriptor(s) | idea | expected sign |
|---|---|---|---|
| 007 | d_007 | B/C/N atomic fraction, O excluded. Control for d_003: was its signal real? | + |
| 008 | d_008 | Pauling electronegativity range (max-min). Extremum; not buildable from means | - |
| 009 | d_009 | Min valence-electron count among constituents x its atomic fraction (interpretation of "fraction-weighted minimum") | - (hypothesis) |
| 010 | d_010 + d_011 | Harmonic-mean covalent radius r_h (bond-length proxy) and r_h^-2.5 (Gao/Simunek form) | - for r_h, + for r_h^-2.5 |
| 011 | d_012 | Composition-only Pugh proxy k=G/B from Mendeleev-number spread; PySR builds Chen-like form | + |
| 012 | d_013 | Valence electron density with O volume replaced by Shannon O2- sphere (11.49 A^3). Closest to the d_002 family (not selected in overnight 1, redundant with Magpie means) so lowest priority | + |

Max 10 cycles per night; queue has 6, so the stop rule (3 consecutive non-improving) or queue end ends the run. If the queue is exhausted the run stops; do not invent new families without a new queue entry.
