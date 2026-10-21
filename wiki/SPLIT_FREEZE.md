# Split and metric freeze (T1, 2026-10-21) — closes #3

Frozen as of this commit: `data/splits/train.csv`, `data/splits/val.csv`, `data/test.sha256`, `eval/score.py`, and the
feature pipeline `featurize()` / `magpie_means()` / `add_descriptors()` in `sr/run_pysr.py` (see coupling note below).
Check with `uv run python scripts/verify_splits.py` (agent-safe; hashes in `data/splits/SHA256SUMS`).

## Verification
- **Reproducibility.** `make_splits.py` re-run from a fresh `uv sync` + `get_data.py` on a second machine (x86 macOS):
  `val.csv` and the test file are byte-identical to the committed ones (test checked only by sha256 against
  `data/test.sha256`, contents not read). `train.csv` differs in one value (CoSb3 shear modulus,
  `57.0143269800793` vs committed `57.014326980079304`, |diff| ~ 4e-15 GPa): float-repr noise, numerically irrelevant.
  **The committed CSVs are canonical; never regenerate them.**
- **Disjointness.** train/val share 0 element-set groups and 0 reduced formulas (1746 / 374 rows; 1150 / 256 groups).
  Every element in val also occurs in train.
- **Test quarantine.** T1 (Lafe) now holds `~/quarantine/test.csv` (regenerated, hash-verified). Thursday's single test
  evaluation is run by T1 by hand: `uv run python scripts/verify_splits.py --test ~/quarantine/test.csv` first.

## Review findings (no code changed in score.py or make_splits.py)
1. **"Held-out chemical families" means held-out *exact element sets*.** 285/374 val rows (76%) have an element set that
   is a strict subset or superset of a train element set (e.g. val Ti-B-C when train has Ti-B). Use the wording
   "held-out element sets" in the pitch; a stricter family split is not worth re-splitting for now.
2. **The frozen metric includes `sr/run_pysr.py:featurize`.** `score.py` imports the feature pipeline from the runner, so
   any edit to `magpie_means()`/`add_descriptors()` (or a matminer upgrade; pinned by `uv.lock`) silently changes the
   metric. Rule: run_pysr.py changes may add search options but must not touch those three functions.
3. **Train loss != metric.** PySR fits squared error (default) but we score MAE on a right-skewed target (median 5.75,
   mean 7.23). Refitting only the constants of the Magpie reference Pareto (ref_s5) under L1 lowers val MAE by
   0.22 (c1), 0.12 (c3), 0.08 (c5), ~0.03 (c10-13), ~0 (c9, c15). Small at the knee but systematic and free; an opt-in
   `--loss L1` is worth using only together with a fresh reference arm (the stored 9-seed arm is L2).
4. `score.py` aborts the whole run if any single Pareto equation is non-finite on val (e.g. `log` of a value that is
   positive on train but not on val). Has not happened in 60 runs; loud failure is the intended behaviour.
5. Data: only binaries and ternaries; 7% train / 10% val targets are negative (Chen goes below 0 when G/B is small);
   17 val rows >= 20 GPa and 1 val row >= 40 GPa, so this split cannot support a superhard-screening claim.
   Duplicates/polymorphs: see wiki/DATA_AUDIT.md (PR #10).
