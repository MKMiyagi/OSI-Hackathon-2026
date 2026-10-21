# Nested CV pilot notes (run ncv_pilot_n5000_s0)

- Config: niterations 5000, procs 4, maxsize 15, timeout 900 s, seed 0, 3 arms x 5 outer folds (+ median constant). 2120 rows, all finite.
- Wall-clock: 1088 s total (about 18 min); 65-80 s per fit (15 fits), no timeouts, no non-finite selected equations.
- Extrapolation to niterations 22000 (linear in niterations): about 4.4 x 72 s = 320 s per fit, so about 80 min per seed (15 fits),
  about 4 h for 3 seeds run back-to-back. If the "8-12 min per fit at 22000" calibration in CLAUDE.md applies to these smaller
  inner-train sets (about 1360 rows vs 1746) the range is up to about 2.5 h per seed (about 7 h for 3). Per-fit 900 s timeout
  could then bind and truncate fits. Running seeds in parallel (2 x procs 4 on this 10-core machine) would be the way to cut it;
  not yet tested for slowdown.
- Pilot results (one seed, niter 5000, NOT evidence of anything): c<=12 mean MAE magpie 3.772, +d_008 3.898, +d_008+d_018 3.883,
  median constant 4.889. d_008 did not beat Magpie-only here; selected in 2-3 of 5 folds. Single seed, optimizer variance
  at this niter is unmeasured; do not interpret.
- Design choices to confirm: selected equation is evaluated with constants as fitted on inner-train (no refit on the full
  outer-train); the median constant uses the outer-train median; tail = hv_chen >= 20 GPa, pooled across folds (103 rows).
