# OSI-Hackathon-2026 — hardness-law

OSI Hackathon 2026. Goal: a compact, composition-only emulator of the DFT-derived Chen (2011) hardness proxy (`hv_chen`, Chen applied to DFT B,G), searched with symbolic regression and compared against the Tehrani-style composition -> B,G -> Chen pipeline. The labels are Chen's own outputs, so this is not a measured-hardness model and does not "beat Chen"; no formula here is established as a physical law. Symbolic regression (PySR) over physically motivated descriptors, with an overnight agent loop (ARIS + Claude Code, Codex as cross-model reviewer).

## Status (Thu morning)
The d_023 (cohesive-energy density) gain recurs under nested grouped CV: it is selected and beats Magpie-only in 5/5 outer folds, with fold-mean outer-fold MAE (pooled train+val; not the quarantined test set) at c<=12 of 3.61 GPa vs 3.79 Magpie-only and 2.81 for the SVR, which descriptively corresponds to 62% of the constant-to-SVR gap vs 53%, with the screening-history caveat: d_023 was screened on train labels and scored once on val before adoption, so this is recurrence under repartition of reused development data and not independent validation. None of the tested additions established a consistent incremental gain over d_023 (metal fraction, B/C/N fraction, their combination with d_027, and L1 loss all stay within search scatter of d_023 alone; L1 has no L1 reference arm), and the shear-proxy line is blocked because elemental shear moduli were unavailable in pymatgen and the handbook tables we cited for B, C, N, O, Si, P, S and other nonmetals, which blocks the specified full-data comparison. Residuals show the formula fails on oxides (overpredicts, mean signed error +2.6 GPa, worse than the constant) and does not separate covalent from ionic phases that share a composition fraction (ZrB2 is underpredicted by 19 GPa while BaC2 is overpredicted by 15). The test-set one-shot and the Zhang measured-Hv check are run today by T1 under [`wiki/THURSDAY_PLAN.md`](wiki/THURSDAY_PLAN.md); TODO(Thursday): test-set MAE per frozen candidate and the baselines; TODO(Thursday): Zhang measured-Hv MAE per candidate. All other numbers are exploratory, on reused development data, and the target is still the proxy `hv_chen` (Chen on DFT B,G).
Details: [overnight 5 summary](wiki/OVERNIGHT_5_SUMMARY.md), [nested CV of d_023](wiki/NESTED_CV_D023.md), [d_023 residuals](wiki/RESIDUALS_D023.md), [storyline](wiki/STORYLINE.md), [candidate formulas](wiki/CANDIDATE_FORMULAS.md); earlier: [overnight 1](wiki/OVERNIGHT_1_SUMMARY.md), [2](wiki/OVERNIGHT_2_SUMMARY.md), [3](wiki/OVERNIGHT_3_SUMMARY.md), [4](wiki/OVERNIGHT_4_SUMMARY.md).

## Results

<!-- DRAFT for T2 (prepared Wed 2026-10-21). Numbers are copied from wiki/PROGRESS_EVAL.md, wiki/T1_ROUTES.md, wiki/BASELINES.md (branch m/baseline) and wiki/RESEARCH_REVIEW_3_VERDICT.md. Edit freely; check each number against its source before submitting. -->

The problem is to find a short formula that predicts, from chemical composition alone, the hardness proxy `hv_chen`: Chen's (2011) formula applied to DFT bulk and shear moduli from the Brgoch dataset. Because the labels are Chen's own outputs, this is an emulation task and not a measured-hardness model, and "beating Chen" is not a coherent claim on this target (see `wiki/RESEARCH_REVIEW_3_VERDICT.md`). The honest comparator is a composition-only pipeline in the style of Tehrani (2018) that predicts B and G from composition and passes them through Chen. Symbolic regression (PySR) searches over Magpie composition features plus a small set of hand-written physical descriptors, one hypothesis per cycle, and every formula is scored by MAE in GPa on the validation split. That split is a reused development set, so each number reported here is descriptive and none is an unbiased estimate of generalization.

The protocol was frozen before the headline comparisons. Train, val and test are split 70/15/15 with seed 42, grouped by element set so that no chemical system appears on both sides, and the test file lives outside the repository with only its hash committed (`wiki/SPLIT_FREEZE.md`). The metric and scorer are not edited. Each descriptor cycle runs at least three seeds and is compared with a stored nine-seed reference arm with no descriptors, using the mean of the best val MAE at complexity 12 or below as the headline. A descriptor counts as an improvement only if that headline drops by at least 0.08 GPa, about one reference standard deviation, and the descriptor appears in a Pareto equation in a majority of seeds.

The largest single improvement in the project came from the search budget and not from any descriptor. Under the smoke-test settings the best formula at complexity 12 or below scored 4.26 GPa. After calibrating the iteration count so that one fit takes about ten minutes, the same Magpie-only search reached 3.91 GPa and then stayed there for roughly five and a half hours and about 45 runs. At complexity 7 and below every one of 52 runs finds the same equations, so the front is converged at the low end and seed scatter appears only from complexity 9 upward. Of fourteen descriptor sets tested under the adopted rule, none qualified as an improvement.

The one descriptor effect that recurs is d_008, the Pauling electronegativity range. It yields the compact formula `NUnfilled + 381.7 exp(-(Row + chi_range))` at complexity 8 with val MAE 4.03, found in nine runs, against 4.19 for the best Magpie-only equation at complexity 9. In a five-seed ablation the benefit is real at complexity 9 or below (4.096 against 4.195) and disappears by complexity 12 (+0.030 GPa, with an interval that spans zero), so d_008 is a stable, readable candidate and not an improvement under the adopted rule. Its physical reading, that hardness falls with ionic character and with period row, is post hoc.

The gap to a black box is the main caveat. A Magpie-feature SVR that predicts B and G and applies Chen reaches 2.82 GPa in T1's implementation and 2.905 GPa under the frozen baseline protocol in `wiki/BASELINES.md`, while a constant at the train median scores 5.04. The best formulas at 3.77 to 4.03 therefore close roughly half of the gap between the constant and the black box, and they remain about a gigapascal short of it. Oracle comparators that use the true DFT moduli (Tian 1.14, Mazhnik–Oganov 3.13 against Chen-made labels) are privileged-input reference points and cannot rank the formulas physically. Errors are also large where hardness matters, with a mean error of 10 to 15 GPa on the 17 validation rows at or above 20 GPa, so we do not claim a superhard-screening use.

The current lead is d_023, a composition-only proxy for cohesive-energy density: the composition-weighted elemental cohesive energy from a fixed external table (matminer, 90 elements) divided by the weighted elemental ground-state volume. In T1's route experiment, adding d_023 to the direct search lowered the whole Pareto front, from 3.92 to 3.79 GPa at complexity 12 or below and from 3.88 to 3.64 at complexity 15 or below, with d_023 selected in every seed. The complexity-5 formula `d_023 / (NdValence + 2.376)` scores 3.90 and is dimensionally consistent, reading as hardness proportional to cohesive-energy density divided by a d-electron, metallicity-like term. Its status is a lead and not a result: it rests on two or three seeds, at about a fifth of the standard iteration budget with L1 loss and unit constraints on one laptop, so it does not yet satisfy the adopted cycle protocol (cycle 020 in `wiki/OVERNIGHT_4_PROPOSAL.md` is the decisive test). The formula also encodes stiffness and not plasticity, and it overpredicts soft metals and salts (Al, W, Cu, NaCl), which Chen's G/B term would handle. A cross-model review found no leakage in d_023 itself, provided held-out DFT moduli never enter the prediction (`wiki/REVIEW_PR12.md`).

The test-set plan is deliberately small. T1 freezes the list of candidate formulas before the test file is touched, rehearses `eval/test_once.py` on val, and then evaluates the frozen list once on the quarantined test split. A second one-shot check scores the same formulas on measured Vickers hardness (Zhang), which is the only evidence here that is independent of Chen. Results: TODO(Thursday): test-set MAE per frozen candidate and the baselines; TODO(Thursday): Zhang measured-Hv MAE per candidate. Nothing in this section should be read as a held-out result until those numbers are filled in. A nested grouped cross-validation with descriptor selection inside the loop (`wiki/NESTED_CV.md`, branch `m/nested-cv`) is the planned credible comparison between pipelines.

## How the agent loop worked

Each descriptor cycle is one hypothesis. The agent reads the wiki and the results ledger so as not to repeat a failed family, writes a descriptor module whose docstring states the physical rationale and the expected sign, runs PySR for at least three seeds, scores every Pareto point on val into the ledger, and summarizes the cycle against the stored nine-seed reference. It then asks a second model, Codex, to review the cycle once at the regular tier for physical plausibility, unit consistency and leakage risk, logs the verdict with per-seed numbers in `wiki/cycle_log.md`, and commits to the agent branch. The loop stops after three non-improving cycles, ten cycles in a night, a STOP file, or 06:00, and an unfixable error writes `wiki/BLOCKED.md` and stops. Because the reviewer is a different model from the one writing descriptors, it catches errors the author tends to repeat, such as algebraically wrong "electron-density" readings, formulas that add eV to dimensionless counts, and wording that overclaims.

The saturated-metric fix is the clearest worked example of the loop correcting itself. The original cycle score was the best val MAE at complexity 9 or below. After the first overnight run, nine no-descriptor reference seeds all returned the same equation, `8.49 MendeleevNumber / (NValence GSvolume) + NUnfilled`, with val MAE between 4.1946 and 4.1949 (standard deviation 0.0001). The score could therefore only move when a descriptor displaced that single function, so "non-improving" mostly meant "not selected below complexity 10", and three such cycles would have stopped the night on a metric that could not discriminate. The remedy, adopted before the later cycles and recorded in `wiki/DECISIONS.md`, was to score at complexity 12 or below, where the reference has a usable spread (mean 3.980, standard deviation 0.061), to require at least three seeds, and to require selection in a majority of seeds. The round-3 review later showed that the new bar still leaves val reuse unresolved, which is why the final claims are descriptive and the test-set plan above exists.

## Quick start (teammates)

```bash
git clone https://github.com/MKMiyagi/OSI-Hackathon-2026 && cd OSI-Hackathon-2026
brew install uv gh
uv sync
uv run python scripts/get_data.py
uv run python scripts/smoke_pysr.py     # first run ~10 min: Julia download + precompile
```

Install Claude Code (`curl -fsSL https://claude.ai/install.sh | bash`), run `claude` once inside the repo to log in, read `CLAUDE.md`. ARIS/Codex are only needed on the overnight machine. The ARIS skills under `.claude/skills/` are symlinks into `~/aris_repo` that exist on the agent machine only; on your clone they are dangling and can be ignored (the project's own skill, `descriptor-cycle`, is a real file).

## Layout

| path | what | owner |
|---|---|---|
| `data/raw/` | matminer downloads (gitignored) | — |
| `data/splits/` | `train.csv`, `val.csv` (committed), `test.sha256` | T1 (frozen Wed hour 2) |
| `descriptors/` | `d_###.py`, one physical hypothesis each | agent / anyone |
| `sr/` | PySR runner | T1 |
| `eval/score.py` | the metric (MAE, GPa, on val) | T1 (frozen Wed hour 2) |
| `eval/baselines.py` | Chen / Tian / Mazhnik–Oganov baselines from B,G | T2 |
| `ledger/results.csv` | one row per Pareto point per run; `search` column = smoke / niter22k / niter120k (rows appended by `score.py` leave it blank) | agent machine only (append) |
| `wiki/` | ARIS research wiki + review verdicts | agent |
| `notebook.py` | marimo notebook | T2 |
| `skills/descriptor-cycle/` | Claude Code skill for the loop (mirrored in `.claude/skills/`, keep identical) | — |
| README results | results tables in this file | T2 |

## Branch and merge conventions

- `main` is always runnable. Nobody commits to it directly; PRs only (0 approvals required), force-push blocked.
- Personal branches: `t1/<topic>`, `t2/<topic>`. Short-lived: PR as soon as it works, self-merge, delete.
- Agent branch: `agent/overnight-2`. ARIS commits and pushes here each cycle; humans don't touch it until Thursday morning, then review and merge via PR.
- `git pull --rebase` before every push (`git config --global pull.rebase true`). Commit small and often.
- File ownership (above) is how we avoid merge conflicts. Tasks live in GitHub Issues, one owner each, labelled by role.

## Test-set quarantine

1. T1 generates the split with a fixed seed → `data/splits/train.csv`, `data/splits/val.csv` (committed) and `test.csv` to `~/quarantine/test.csv` **outside the repo** on T1's laptop.
2. T1 commits `data/test.sha256` (hash of the test file) for provenance.
3. `.gitignore` excludes `data/test.csv`; `.claude/settings.json` denies the agent read access.
4. The test file is evaluated once, Thursday morning, by T1, by hand.
