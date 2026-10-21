# Research Review Request — Round 3: are the candidate formulas physical laws, and is val reuse fatal?

Repo root: /Users/mmiyagishima/OSI-Hackathon-2026. Decision input for the Wednesday noon target decision (wiki/DECISIONS.md, GitHub issue #2).
Do NOT read data/test.csv or ~/quarantine/ (quarantined; never needed).

## Questions
1. **Law or fit?** Is any formula in wiki/CANDIDATE_FORMULAS.md defensible as a physical law (or even as a physically interpretable compact model) rather than a curve fit? Consider: fitted prefactors (381.7, 951.27, 872.77, ...) with no derivation; dimensional consistency (dimensionless chi/Row/counts mixed with eV and A^3 via implicit coefficients); whether the "physical reading" column is post-hoc; sign check (d_017 came out opposite to the pre-registered sign); whether recurrence across seeds (d_008 form in 9 runs) is evidence of physics or of a stable optimum of the search over a fixed variable set.
2. **Val reuse.** val (data/splits/val.csv) was used to pick descriptors, choose equations from Pareto fronts, and tune the metric itself. Roughly 60 runs, ~755 scored Pareto rows, 19 descriptor families. Is this fatal to any claim? What claims survive (e.g. "ceiling of Magpie-only SR on val", "d_008 recurs") and which do not (e.g. "beats baseline on held-out families")? How large is the plausible selection optimism relative to the observed gains (0.1-0.2 GPa vs reference sd 0.06)? Does the 9-seed reference (v008_wo_s0-4, ref_s5-8) address it at all (it controls seed noise, not selection on val)?
3. **Target circularity.** Target hv_chen = Chen(2011) on DFT B,G, not measured hardness (wiki/DECISIONS.md, wiki/codex_review_run_pysr.md). Given 1-2, which option is defensible for the noon decision: (a) keep hv_chen, (b) predict B and G from composition then apply Chen/Tian/Mazhnik-Oganov, (c) find a measured-Hv dataset? State what each option allows us to claim and what the minimum viable claim is for the hackathon.
4. What is the minimum additional evidence (no test set) that would make any formula claim honest? E.g. nested/grouped CV on train+val with the whole descriptor-selection pipeline inside the loop; leave-family-out; a fresh untouched split.

## Primary artifacts (verify, do not trust this summary)
- wiki/CANDIDATE_FORMULAS.md, wiki/OVERNIGHT_3_SUMMARY.md, wiki/OVERNIGHT_2_SUMMARY.md, wiki/OVERNIGHT_1_SUMMARY.md, wiki/D008_VALIDATION.md, wiki/DECISIONS.md, wiki/cycle_log.md, wiki/HYPOTHESES.md, wiki/HYPOTHESES_3.md
- ledger/results.csv (column `search`; rows from 'smoke' used niter 40), ledger/results_uncalibrated.csv, ledger/cycle_scores*.csv, ledger/runs/*.json
- descriptors/d_*.py (d_008, d_017, d_018, d_016 especially), sr/run_pysr.py, eval/score.py, data/splits/ (train.csv, val.csv only), scripts/smoke_pysr.py (Chen formula and label construction), data/raw/brgoch_superhard_training.csv
- CLAUDE.md (current metric rule)

## Known facts to check
- No-descriptor Magpie c<=9 winner is the same function in 9/9 seeds (val 4.1946); c<=12 mean 3.9802 sd 0.0609; c<=15 3.9273 sd 0.0382.
- d_008 alone: c<=9 mean 4.0959 vs 4.1947 (Welch CI [-0.21, +0.01]); no gain at c<=12/15.
- Best single results (c018_s0 3.7722 at c12) rely on ~10 val rows.
- Train-mean baseline val MAE 5.2589.

Be adversarial and specific. Say plainly what holds up. Give a verdict I can paste into wiki/ and a recommendation for the noon decision.
