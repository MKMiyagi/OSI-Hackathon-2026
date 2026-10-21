# Thursday plan: the two one-shot evaluations (T1 runs both by hand)

Written Wed 2026-10-21 ~15:00, **before** cycle 020 and overnight 4 finish. The selection rule below is fixed now.
Thursday morning only fills in the formula strings it picks; nothing else changes after results are seen.

## Candidate list: the selection rule (fixed)
Every candidate goes into BOTH evaluations, on one command line each.
1. **Constants and baselines:** train-median constant (always included); `--svr` (Magpie SVR straight on hv_chen,
   the black-box bar, val 2.82).
2. **Incumbent compact formulas:**
   - `magpie_c9`: the recurring Magpie-only c9 equation (val 4.195)
   - `d008_c8`: `m_NUnfilled + 381.72168 / exp(d_008 + m_Row)` (val 4.030)
3. **d_023 formulas:**
   - `d023_c5` = `d_023 / (m_NdValence + 2.3757682)`, the knee law (val 3.904)
   - for each window c<=9, c<=12, c<=15: the single equation with the lowest val MAE among all hv_chen-target runs that
     use d_023 and only physical features (no MeltingT / SpaceGroupNumber), from cycle 020 (`t1_c020_*`), overnight-4
     cycles 020-024, and `t1_hvd23_*`. Ties go to the lower complexity.
4. **Magpie-only best at the same windows** (c<=9, c<=12, c<=15): same rule, Magpie-only runs. This gives the
   like-for-like comparison.
At most 10 predictors. If a window's pick is already listed, it is not added twice.

## Order of operations (Thursday morning)
1. `git pull` on main; note the commit hash. Fill the formula strings into the two commands below (rule above) and
   commit this file, so the list is fixed in git before anything runs.
2. **Rehearse:** `uv run python eval/test_once.py --rehearse-on-val <predictors>`. The val MAEs must match the ledger.
3. **Test, once:** `uv run python scripts/verify_splits.py --test ~/quarantine/test.csv` (must PASS), then
   `uv run python eval/test_once.py --test ~/quarantine/test.csv <predictors> --svr --confirm-one-shot`.
4. **External check:** `uv run python eval/external_zhang.py <predictors as --formula ...> --svr` (dry run, coverage
   only), then the same command with `--score --confirm-one-shot`.
5. Commit both output CSVs (`ledger/test_once_*.csv`, `ledger/external_zhang_*.csv`) and report every predictor,
   including the ones that lose.

## What each evaluation can and can't claim
- **Test** (held-out element sets, Chen-proxy labels): the only unselected estimate of emulator accuracy. It cannot
  say anything about measured hardness.
- **Zhang** (measured Vickers Hv, headline = median at 0.49-1.96 N): whether the emulator tracks real hardness, and
  how Chen on Materials Project DFT moduli does on the same compositions. Small n where MP moduli exist (144
  headline compositions). Expect formulas to overpredict metals (wiki/T1_ROUTES.md, "Where it fails").
