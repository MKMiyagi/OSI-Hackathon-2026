# Codex review of wiki/STORYLINE.md (one pass, 2026-10-21)
Reviewer: Codex, thread `01a160ce-2d59-75c3-9135-5e4d8d7e47f9`, read-only, high effort. Question: overclaimed or metric-shopped?

**Verdict: MINOR EDITS; no evidence of secondary-metric shopping.** It confirmed the pre-registration commits (`ac4d493`, `01c27df`) precede `eval/metrics_extra.py`, reproduced the table, candidate metrics, bin counts, 1,032/986 equation counts and the 15 log-failures, and noted the summary uses per-seed means, not the best seed. Gap-closed was pre-registered, so not an invented favourable metric; but the three candidates were frozen after primary val results were known.

Seven edits, all applied (numbers re-checked by the executor before applying):
1. bootstrap interval is [43.9%, 76.5%], not [44%, 77%]; "reliably worse" removed (intervals ignore adaptive selection); "all 1,032 equations have higher val MAE than the SVR".
2. lead with raw MAEs (3.980 / 3.684 vs 2.839 / 5.044) rather than "roughly half the gap".
3. 5-15 GPa bin: c8 ties the constant (3.28 vs 3.31); c5, c9 worse; "no better" was too harsh.
4. "inside sampling noise" replaced by 20-22 vs 23 hits of 38, uncertainty unquantified.
5. tail: report the SVR's own signed error (-7.30 vs c8 -6.33; MAE 7.52 vs 7.26) so the c8 underprediction is not read in isolation; removed the "not worse than the SVR" non-inferiority wording.
6. Zhang paragraph: it compares our direct hardness formulas (not Chen-on-formulas) with measured Hv, and the load window is already frozen in `eval/external_zhang.py`; the earlier text wrongly said a headline load was still to be fixed.
7. added: cohesive energy and volume are composition averages of elemental values; "about 5 reference sd" is optimizer variation, not five-sigma predictive evidence.
