import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eval import metrics_extra as me  # noqa: E402


def test_log_mae_counts_failures_and_excludes_them():
    y = np.array([1.0, 2.0, 3.0])
    p = np.array([1.0, -3.0, -5.0])
    lm, nf = me.log_mae(y, p)
    assert nf == 2 and lm == pytest.approx(0.0)


def test_log_mae_value():
    lm, nf = me.log_mae([0.0], [math.e - 3])
    assert nf == 0 and lm == pytest.approx(abs(math.log(3) - 1))


def test_log_mae_rejects_target_below_minus_three():
    with pytest.raises(ValueError):
        me.log_mae([-3.5], [0.0])


def test_bins_half_open_edges():
    idx = me.bin_index([4.99, 5, 14.99, 15, 24.99, 25, 80])
    assert list(idx) == [0, 1, 1, 2, 2, 3, 3]


def test_binned_mae_empty_bin_is_nan():
    b, n = me.binned_mae([1.0, 2.0], [2.0, 4.0])
    assert b[0] == pytest.approx(1.5) and math.isnan(b[1]) and n == [2, 0, 0, 0]


def test_spearman_perfect_reverse_and_constant():
    y = np.arange(10.0)
    assert me.spearman(y, y**3) == pytest.approx(1.0)
    assert me.spearman(y, -y) == pytest.approx(-1.0)
    assert math.isnan(me.spearman(y, np.ones(10)))


def test_precision_top10_perfect_and_constant_chance():
    y = np.arange(100.0)
    assert me.precision_top(y, y) == pytest.approx(1.0)
    assert me.precision_top(y, np.ones(100)) == pytest.approx(0.1)
    assert me.precision_top(y, -y) == pytest.approx(0.0)


def test_precision_top10_tie_straddling_cut_is_expected_overlap():
    y = np.arange(20.0)  # k = 2, true top = {18, 19}
    p = np.zeros(20)
    p[19] = 1.0  # one clear hit; the second slot is a 19-way tie, 1 of which (index 18) is a true top row
    assert me.precision_top(y, p) == pytest.approx((1 + 1 / 19) / 2)


def test_all_metrics_gap_and_mase():
    y = np.array([1.0, 6.0, 10.0, 30.0])
    m = me.all_metrics(y, y + 1.0, const_mae=4.0, svr_mae=0.5)
    assert m["mae"] == pytest.approx(1.0)
    assert m["mase_const"] == pytest.approx(0.25) and m["mase_svr"] == pytest.approx(2.0)
    assert m["gap_closed"] == pytest.approx((4.0 - 1.0) / (4.0 - 0.5))
    assert m["n_ge25"] == 1 and m["n_lt5"] == 1
