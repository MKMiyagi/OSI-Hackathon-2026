# Review of PR #12 (t1/wed)

Reviewer: executor (checks run against `git diff main...origin/t1/wed`, 25 files + 6 figures) plus one Codex question. Findings only; PR not merged by the reviewer.

## Checklist
| Check | Result |
|---|---|
| `eval/score.py` untouched | Yes, not in the diff. |
| `data/splits/train.csv`, `val.csv` untouched | Yes. The only file under `data/splits/` is the new `SHA256SUMS`. |
| 9 reference runs untouched | Yes. Nothing under `ledger/` or `ledger/runs/` is in the diff (`ref_s5-8`, `v008_wo_s0-4` unchanged). |
| `run_pysr.py` defaults unchanged | Yes, with one note. `--loss` defaults to `L2`, which maps to `elementwise_loss=None` (PySR default). `--units` and `--dimensionless-constants` are store_true and default off, so no `X_units`/`y_units` are passed. `featurize`, `magpie_means`, `add_descriptors` are not edited. The note: the diff adds `loss`/`units`/`dimensionless_constants` keys to the run JSON, so new run metadata differs from the reference arm's. Scoring is unaffected. |
| `eval/test_once.py` cannot run silently | Yes. `--test` or `--rehearse-on-val` is required (mutually exclusive group). `--test` additionally needs `--confirm-one-shot`, a sha256 match against `data/test.sha256`, and no existing `ledger/test_once_*.csv`. The test path is a CLI argument, never hardcoded. |
| Imports can't read the test file | Yes. No file under `eval/ sr/ scripts/ descriptors/` other than `test_once.py` names the test file. `make_splits.py` (imported for `chen_hardness`) writes `~/quarantine/test.csv`, but only inside `main()` behind `if __name__ == "__main__"`. `get_external`, `tehrani_baseline`, `external_zhang` and `run_pysr` have no import-time reads. `verify_splits.py --test` only hashes bytes. |

Caveats (not blockers):
- The guard is procedural. An agent given the path could still pass `--test ... --confirm-one-shot`. CLAUDE.md's "never reference ~/quarantine" rule remains the real control. `test_once.py` itself says agents must never run it.
- `test_once.py` imports `scripts.make_splits`, so any future top-level code added there would run on a test-set invocation. Consider moving `chen_hardness` to a neutral module.
- GitHub reported `mergeable: UNKNOWN` at review time; not yet confirmed conflict-free against main after PR #10.

## d_023 elemental cohesive-energy table
- Source: `matminer/utils/data_files/cohesive_energies.json`, loaded from the installed matminer package (90 elements). The d_023 docstring attributes it to Kittel.
- Independent of this dataset: it is a fixed external table shipped with matminer. Nothing in `d_023.py` reads `data/raw`, B, G, or any split. The other input, `m_GSvolume_pa`, is the Magpie elemental ground-state volume, also an external elemental table.
- Spot check (Ti 4.85, C 7.37, Fe 4.28, Si 4.63 eV/atom) agrees with Kittel values as I remember them. I did not find a provenance note inside the matminer package, so the Kittel attribution rests on the docstring and this spot check. Recommend citing the matminer file path and checking its upstream reference.
- Elements missing from the table (H, He, Pm, At, Fr, Pa) give NaN, not an exception or a fill value. Such rows are dropped at fit time (`keep` mask) and counted as non-finite at scoring. Report coverage.

## Codex verdict (regular tier, thread 01a16002-f70d-7801-a4a9-9254c39a9b35)
Question: "Is d_023 = (composition-weighted elemental cohesive energy)/(composition-weighted elemental volume) a leakage risk for a Chen(B,G) target, and how should it be framed?"

**Verdict: no leakage in d_023 itself; conditional on the downstream pipeline.** Residual risks:
1. Held-out DFT B, G, or k must never enter predictions. Supplying the true held-out k while predicting B leaks target-defining information.
2. Val reuse: repeated feature, exponent or model selection on val makes val optimistic. Element-set grouping does not prevent that.
3. Missing elements: define coverage and rules; any imputation fitted on train only; no B/G-based fallbacks and no zero fill.
4. The 3.26 prefactor is a learned calibration, not leakage if fit on train only, and not a universal constant.

Recommended framing, adopted: *d_023 is a composition-only proxy for cohesive-energy density from fixed external elemental tables, independent of this dataset's DFT elastic properties. The binding-energy relation motivates its association with B but does not establish an exact composition-averaged identity. A train-only calibration B = 3.26·d_023^0.994 gives val R² 0.81 under element-set-grouped splitting. It is a physically motivated predictor, not label leakage, provided calibration is train-only, missing elements are documented, and the Pugh ratio is predicted without held-out DFT B/G.*

## Action items for T1 before or after merge
- Confirm `eval/compose_hv.py` predicts k from composition only (Codex risk 1). I read the diff for d_023 and the flags but did not audit `compose_hv.py`.
- Add a d_023 coverage count (rows with NaN) to the cycle 020 report.
- The prefactor and exponent were fit on train, but the R² 0.81 is a val number already consulted in selection, so label it a development-set figure.
