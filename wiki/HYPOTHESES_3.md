# Hypothesis queue — overnight 3, Phase 4 (cycles 012+, seeds 0-2, run in order)

Cycle score = mean best val_mae at c<=9 AND at c<=12 over 3 seeds (sr/cycle_summary3.py), also reported as a
paired difference vs the no-descriptor runs v008_wo_s0..s2 (same seeds, same search settings). The overnight-2
"3 consecutive non-improving" stop rule is suspended; a queue item is skipped only if the reviewer finds leakage.
All descriptors use only df["comp"] (+ fixed literature constants); none is tuned on val.

| cycle | descriptor(s) | idea | sign |
|---|---|---|---|
| 012 | d_014 | sum_i x_i (chi_max - chi_i): composition-averaged EN deviation from the most electronegative element | - |
| 013 | d_015 | Pauling ionic character 1 - exp(-(chi_max-chi_min)^2/4) (saturating transform of d_008) | - |
| 014 | d_016 | EN range on the Allen scale (scale-sensitivity test of d_008; hard-coded literature table) | - |
| 015 | d_008 + d_007 | EN range plus B/C/N fraction: does covalent light-element content interact with EN spread? | -, + |
| 016 | d_013 | O-corrected valence electron density, alone | + |
| 017 | d_008 + d_013 | EN range plus d_013 jointly | -, + |
| 018 | d_017 | sum_{chi>2.5} x_i chi_i: EN-weighted anion-like content | + |
| 019 | d_018 | (chi_max-chi_min)^2: a nonlinearity in d_008 that is costly to build in PySR | - |
