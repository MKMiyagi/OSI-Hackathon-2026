# OSI-Hackathon-2026 — hardness-law

OSI Hackathon 2026. A search for compact, interpretable composition-only emulators of the DFT-derived Chen hardness proxy on held-out chemical families. Symbolic regression (PySR) over physically motivated descriptors, with an overnight agent loop (ARIS + Claude Code, Codex as cross-model reviewer).

## Status (Wed morning)
Three overnight runs found the best observed Magpie-only symbolic-regression val MAE under this search configuration to be 4.19 / 3.91 / 3.89 GPa at complexity <=9 / 12 / 15. The compact formula from descriptor d_008 (`NUnfilled + 381.7/exp(Row + d_008)`, val 4.03 at c8) is a recurrent candidate without an established predictive advantage. The old c<=9 cycle metric was found to be saturated, so it was replaced (>=3 seeds vs a stored 9-seed no-descriptor reference, headline c<=12; see `CLAUDE.md` and `wiki/DECISIONS.md`). All val numbers are exploratory and the target is still the provisional `hv_chen` (Chen on DFT B,G).
Details: [overnight 1](wiki/OVERNIGHT_1_SUMMARY.md), [overnight 2](wiki/OVERNIGHT_2_SUMMARY.md), [overnight 3](wiki/OVERNIGHT_3_SUMMARY.md), [candidate formulas](wiki/CANDIDATE_FORMULAS.md).

## Quick start (teammates)

```bash
git clone https://github.com/MKMiyagi/OSI-Hackathon-2026 && cd OSI-Hackathon-2026
brew install uv gh
uv sync
uv run python scripts/get_data.py
uv run python scripts/smoke_pysr.py     # first run ~10 min: Julia download + precompile
```

Install Claude Code (`curl -fsSL https://claude.ai/install.sh | bash`), run `claude` once inside the repo to log in, read `CLAUDE.md`. ARIS/Codex are only needed on the overnight machine. The ARIS skills under `.claude/skills/` are symlinks into `~/aris_repo` that exist on the agent machine only; on your clone they are dangling and can be ignored (the project's own skill, `descriptor-cycle`, is a real file).

## Reproduce the declared baseline

With the committed train/val splits and locked dependencies:

```bash
uv sync --frozen
uv run python eval/baselines.py --run-id baseline_v1
```

This selects two RBF SVRs over the full 132 Magpie features using five-fold
element-set-grouped CV on train only, then applies Chen to predicted B,G.
It also reports train constants and explicitly labelled true-DFT oracle comparisons,
including MAE for targets >=20 GPa. Each invocation appends six rows to the ledger
and writes [the results and exact protocol](wiki/BASELINES.md). Oracles using true
DFT moduli are privileged-input comparisons; Chen reproduces the target by construction.

## Layout

| path | what | owner |
|---|---|---|
| `data/raw/` | matminer downloads (gitignored) | — |
| `data/splits/` | `train.csv`, `val.csv` (committed), `test.sha256` | T1 (frozen Wed hour 2) |
| `descriptors/` | `d_###.py`, one physical hypothesis each | agent / anyone |
| `sr/` | PySR runner | T1 |
| `eval/score.py` | the metric (MAE, GPa, on val) | T1 (frozen Wed hour 2) |
| `eval/baselines.py` | composition → Magpie → SVR(B,G) → Chen; constants and true-DFT oracle comparisons | T2 |
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
