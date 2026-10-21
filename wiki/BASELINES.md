# Independent replication of the SVR baseline (Codex implementation, 2.905 vs T1's 2.82)

Run `baseline_v1`; 2026-10-21T18:23:44+00:00; branch `m/baseline`.

All errors are MAE in GPa against `hv_chen`, a Chen proxy derived from DFT
elastic moduli, not measured hardness. Val has been reused during formula
development; these are descriptive development-set comparisons.

| Baseline | Inputs at inference | Overall MAE | MAE for target >= 20 GPa |
|---|---|---:|---:|
| Tehrani-style Magpie → SVR(B,G) → Chen | Composition only | 2.905320 | 7.670724 |
| Train mean | Train target constant | 5.258939 | 21.030398 |
| Train median | Train target constant | 5.044224 | 22.508477 |
| Oracle upper bound: Chen (2011) | True DFT B,G | 0.000000 | 0.000000 |
| Oracle upper bound: Tian (2012) | True DFT B,G | 1.142035 | 1.215403 |
| Oracle upper bound: Mazhnik–Oganov (2019) | True DFT B,G | 3.125986 | 4.785472 |

Train: 1746 rows / 1150 element-set groups. Val: 374 rows / 256 groups; 17 rows have **true target** `hv_chen >= 20`.

## Exact fixed protocol

1. Read only `data/splits/train.csv` and `data/splits/val.csv`. Keep every row,
   including negative Chen targets. Reject nonfinite labels/predictions and
   nonpositive true DFT moduli. Do not clip hardness. Verify train/val
   element-set groups are disjoint. No split files are changed.
2. From formulas alone, use matminer `ElementProperty.from_preset('magpie',
   impute_nan=False)`: all **132 features**, 22 elemental properties times
   minimum, maximum, range, mean, average deviation, and mode. Include all
   properties (also MeltingT and SpaceGroupNumber); no SR exclusions or
   descriptor modules. Element tables are fixed, not learned from this dataset.
3. Each estimator is `SimpleImputer(strategy='median', keep_empty_features=True)`
   -> `StandardScaler()` -> `SVR(kernel='rbf', epsilon=0.1, tol=0.001)`.
   Median imputation and scaling are fitted inside each training fold; an
   entirely missing training column is filled with zero. No target scaling.
4. Fit bulk_modulus and shear_modulus separately in GPa. For each, select
   C in `[1, 10, 100]` and gamma in `['scale', 0.01, 0.001]` by
   `GridSearchCV(scoring='neg_mean_absolute_error', cv=GroupKFold(5),
   n_jobs=1, refit=True)`. Groups are the sorted unique element symbols
   joined with `-`, exactly as in `scripts/make_splits.py`; folds are
   deterministic, unshuffled, and identical for B and G. Minimize the
   unweighted mean of the five held-out **modulus** MAEs. Ties take the first
   grid candidate in the stated order. All other SVR defaults are unchanged.
   The selected pipeline is refitted on all train rows. Val is read only
   after both model selections/refits; no val-based selection is performed.
5. Predict B and G from val formulas and apply the declared Chen equation
   directly, with no clipping or positivity projection. Unconstrained SVR
   can predict nonphysical negative moduli. Negative B still gives a real
   Chen value because B enters squared; retain it and report its count.
   Zero B or negative G would make Chen undefined; fail rather than drop
   rows or invent a prediction. Keep all negative hardness outputs.
   This is a simple **Tehrani-2018-style composition-only baseline**, not an
   exact reproduction of the paper or an extensively tuned competitor.
6. Constants are train `hv_chen` mean = 7.22797055707 and
   median = 5.74989140317; neither uses val labels to fit.
7. Compute all three elastic formulas from **true val DFT B,G** separately.
   These are **oracle / privileged-input upper bounds**, not composition-only
   baselines. Only Chen is an exact target-reconstruction bound. Tian and
   Mazhnik–Oganov are oracle-input comparators, not guaranteed mathematical
   error bounds. Their error against Chen labels cannot rank physical accuracy.
8. Report row-weighted overall MAE and MAE restricted by true `hv_chen >= 20`,
   using the same rows for every method. No rounding precedes scoring.

## Elastic formulas

All B, G, E and H values are in GPa; k = G/B.

- Chen (2011): `H = 2 (k^2 G)^0.585 - 3`.
- Tian (2012): `H = 0.92 k^1.137 G^0.708`.
- Mazhnik–Oganov (2019): `E = 9BG/(3B+G)`, `nu = (3B-2G)/(2(3B+G))`,
  `chi = (1-8.5nu+19.5nu^2)/(1-7.5nu+12.2nu^2+19.6nu^3)`,
  `H = 0.096 chi E`. See [original paper, Eqs. 10–11](https://uspex-team.org/static/file/mazhnik2019.pdf).

## Train-only model selection

| Modulus | Selected C | Selected gamma | Mean CV modulus MAE (GPa) |
|---|---:|---|---:|
| bulk_modulus | 100 | scale | 15.675128 |
| shear_modulus | 100 | scale | 13.611122 |

All fixed grid candidates (mean of five fold MAEs, GPa):

| C | gamma | B CV MAE | G CV MAE |
|---:|---|---:|---:|
| 1 | scale | 40.726751 | 21.203584 |
| 1 | 0.01 | 42.117449 | 21.693095 |
| 1 | 0.001 | 48.119345 | 23.872975 |
| 10 | scale | 21.375112 | 15.441234 |
| 10 | 0.01 | 21.927732 | 15.394729 |
| 10 | 0.001 | 28.270346 | 18.406641 |
| 100 | scale | 15.675128 | 13.611122 |
| 100 | 0.01 | 15.914189 | 13.701193 |
| 100 | 0.001 | 20.509741 | 15.770424 |

CV held-out fold sizes (rows / element-set groups): 350 / 230, 349 / 230, 349 / 230, 349 / 230, 349 / 230.

## Reproduce and provenance

```bash
uv sync --frozen
uv run python eval/baselines.py --run-id baseline_v1
```

Each invocation appends six rows to `ledger/results.csv` using its existing
header: `descriptor_set=baseline_<name>`, `complexity=0`, `search=baseline`,
`split=val`, `val_mae` = overall MAE. JSON `notes` store tail MAE, subset
counts, oracle labels, and selected SVR parameters. Reruns append a new block
and overwrite this report; they do not deduplicate prior ledger rows.

- `data/splits/train.csv` SHA256: `0e65cb9f3549114e3f56643f511c6d9af62ffdcd8625c8c489e582f289b81f4a`
- `data/splits/val.csv` SHA256: `7cba5f21dfcb9c87d7acf8fdec854cb14e52def29494a2e60dcbe5df5a6f3fd7`
- Versions: numpy 2.5.4, pandas 2.3.3, scikit-learn 1.9.1, matminer 0.10.1, pymatgen 2026.9.24.
- Raw nonfinite feature entries before fold-local imputation: train 0.
- Raw predicted-modulus diagnostics on val (no clipping): {"bulk_modulus": {"minimum_raw_GPa": -1.7575352991867277, "n_nonpositive": 1}, "shear_modulus": {"minimum_raw_GPa": 3.477899980904894, "n_nonpositive": 0}}.
