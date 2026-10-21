"""Unit test of the cycle rule on the stored reference runs. Run: uv run python -m pytest tests (or python tests/test_cycle_summary3.py)."""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "sr"))
import cycle_summary3 as cs  # noqa: E402

RES = pd.read_csv(ROOT / "ledger/results.csv")


def test_reference_has_nine_runs():
    assert len(cs.REF) == 9 and set(cs.REF) <= set(RES.run_id)


def test_reference_means_match_claude_md():
    st = cs.reference_stats(RES)
    for w, (m, sd) in {9: (4.1947, 0.0001), 12: (3.9802, 0.0609), 15: (3.9273, 0.0382)}.items():
        assert abs(st[w][0] - m) < 5e-5, (w, st[w])
        assert abs(st[w][1] - sd) < 5e-5, (w, st[w])


def test_improvement_rule():
    ref = 3.9802
    assert cs.is_improvement(ref - 0.08, ref, 2, 3)
    assert not cs.is_improvement(ref - 0.079, ref, 3, 3)   # drop too small
    assert not cs.is_improvement(ref - 0.2, ref, 1, 3)     # not selected in a majority
    assert not cs.is_improvement(ref - 0.2, ref, 2, 4)     # exactly half is not a majority
    assert cs.is_improvement(ref - 0.2, ref, 3, 5)


def test_selection_on_stored_runs():
    sel, minc = cs.selection(RES, ["c017_s2"], ["d_008"])
    assert sel == [True] and minc == [8]
    sel, _ = cs.selection(RES, ["v008_wo_s0"], ["d_008"])
    assert sel == [False]


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
            print("ok", n)
