# Decisions

## Target and baseline (2026-10-20) — PROVISIONAL, may change Wednesday
- Baseline is composition-only (Tehrani 2018 SVM: composition -> B,G -> Chen Hv), not Chen, since Chen needs DFT B,G.
- Target = `hv_chen` = Chen(2011) applied to DFT B,G from data/raw/brgoch_superhard_training.csv.
- Caveat (see codex_review_run_pysr.md): labels are Chen-derived, so any formula is fit to Chen's output, not measured hardness. Revisit Wednesday.
- Splits: 70/15/15, seed 42, grouped by sorted element set. Test lives in ~/quarantine/test.csv (sha256 in data/test.sha256), never read by agents.
