# OSI-Hackathon-2026 — hardness-law

OSI Hackathon 2026. A compact, physically interpretable, composition-only formula for Vickers hardness that beats Chen (2011) on held-out chemical families. Symbolic regression (PySR) over physically motivated descriptors, with an overnight agent loop (ARIS + Claude Code, Codex as cross-model reviewer).

## Quick start (teammates)

```bash
git clone https://github.com/MKMiyagi/OSI-Hackathon-2026 && cd OSI-Hackathon-2026
brew install uv gh
uv sync
uv run python scripts/get_data.py
uv run python scripts/smoke_pysr.py     # first run ~10 min: Julia download + precompile
```

Install Claude Code (`curl -fsSL https://claude.ai/install.sh | bash`), run `claude` once inside the repo to log in, read `CLAUDE.md`. ARIS/Codex are only needed on the overnight machine.

## Layout

| path | what | owner |
|---|---|---|
| `data/raw/` | matminer downloads (gitignored) | — |
| `data/splits/` | `train.csv`, `val.csv` (committed), `test.sha256` | A (frozen Wed hour 2) |
| `descriptors/` | `d_###.py`, one physical hypothesis each | agent / anyone |
| `sr/` | PySR runner | B |
| `eval/score.py` | the metric (MAE, GPa, on val) | A (frozen Wed hour 2) |
| `ledger/results.csv` | one row per Pareto point per run | agent machine only (append) |
| `wiki/` | ARIS research wiki + review verdicts | agent |
| `notebook.py` | marimo notebook | C |
| `skills/descriptor-cycle/` | Claude Code skill for the loop | — |

## Branch and merge conventions

- `main` is always runnable. Nobody commits to it directly; PRs only (0 approvals required), force-push blocked.
- Personal branches: `a/<topic>`, `b/<topic>`, `c/<topic>`. Short-lived: PR as soon as it works, self-merge, delete.
- Agent branch: `agent/overnight-1`. ARIS commits and pushes here each cycle; humans don't touch it until Thursday morning, then review and merge via PR.
- `git pull --rebase` before every push (`git config --global pull.rebase true`). Commit small and often.
- File ownership (above) is how we avoid merge conflicts. Tasks live in GitHub Issues, one owner each, labelled by role.

## Test-set quarantine

1. A generates the split with a fixed seed → `data/splits/train.csv`, `data/splits/val.csv` (committed) and `test.csv` to `~/quarantine/test.csv` **outside the repo** on A's laptop.
2. A commits `data/test.sha256` (hash of the test file) for provenance.
3. `.gitignore` excludes `data/test.csv`; `.claude/settings.json` denies the agent read access.
4. The test file is evaluated once, Thursday morning, by A, by hand.
