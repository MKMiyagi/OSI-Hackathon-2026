# Round 2 — response and targeted follow-ups

## Accepted (no pushback)
- Fix 1 (target circularity), 2 (composition ambiguity, BN mp-2653 vs mp-984), 3 (negative / flagged
  labels), 4 (group split by element set → "held-out chemical systems"), 5 (three-tier baseline
  table), 6 (missing runner/scorer), 7 (predeclared selection rule), 8 (retire full-data smoke path).
- Correction acknowledged: my `cat`-bypass hypothesis was wrong per current permissions docs.
- Cleanup: drop matbench_glass, unify wiki path, move descriptor-cycle skill under .claude/skills/.

## The decision the team must make (not yet made)
Track A — **proxy surrogate**: composition-only formula approximating Chen(DFT B,G) on brgoch,
grouped by chemical system; deployable baseline = composition→(B,G) regressors→Chen.
Track B — **measured Hv**: train/eval on measured Vickers hardness (Hickey–Brgoch load data if the
workbook is usable, else Dovale-Farelo 143), baseline = Chen with that dataset's moduli + composition
→predicted-moduli→Chen. Possibly Track A for training/descriptor search + Track B as independent
external evaluation only.

## Requests
1. Give a results-to-claims matrix for each track (and the A-train/B-evaluate hybrid): for outcomes
   {formula beats deployable Chen baseline clearly / ties / loses}, what may be claimed?
2. For the hybrid, is evaluating on ~100–300 measured points with grouped resampling enough to say
   anything, given the measured polymorph conflicts you found? What is the minimal honest report?
3. Concretely define "the knee" selection rule you'd accept (one sentence).
4. Which track would you pick for a 2-day laptop hackathon, and why? One paragraph.
