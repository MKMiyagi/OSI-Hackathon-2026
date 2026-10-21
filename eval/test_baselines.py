"""Scientific and protocol checks: uv run python -m unittest eval.test_baselines."""

import csv
import tempfile
import unittest
from pathlib import Path

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

from eval.baselines import (
    GRID, append_results, chen_hardness, element_groups, magpie_features,
    mazhnik_oganov_hardness, metrics,
    select_modulus_model, tian_hardness,
)


class BaselineTests(unittest.TestCase):
    def test_element_family_ignores_order_and_stoichiometry(self):
        groups = element_groups(["TiO2", "O3Ti2", "Ti2O", "TiN"])
        self.assertEqual(list(groups), ["O-Ti", "O-Ti", "O-Ti", "N-Ti"])

    def test_full_magpie_statistics(self):
        X = magpie_features(["NaCl", "TiO2"])
        self.assertEqual(X.shape, (2, 132))
        for stat in ("minimum", "maximum", "range", "mean", "avg_dev", "mode"):
            self.assertEqual(sum(c.startswith(f"MagpieData {stat} ") for c in X), 22)
        self.assertIn("MagpieData range MeltingT", X)
        self.assertIn("MagpieData mode SpaceGroupNumber", X)

    def test_svr_protocol_and_group_separation(self):
        groups = element_groups(["TiO", "TiO2", "BN", "B2N", "NaCl", "KCl", "MgO", "AlN"])
        X = np.array([[i, i % 2] for i in range(8)], dtype=float)
        X[0, 1] = np.nan
        y = np.arange(8, dtype=float) + 10
        search = select_modulus_model(X, y, groups)
        self.assertIsInstance(search.cv, GroupKFold)
        self.assertFalse(search.cv.shuffle)
        self.assertEqual(search.cv.n_splits, 5)
        for train, held in search.cv.split(X, y, groups):
            self.assertFalse(set(groups[train]) & set(groups[held]))
        self.assertEqual(search.param_grid, GRID)
        self.assertEqual(len(search.cv_results_["params"]), 9)
        self.assertEqual(search.scoring, "neg_mean_absolute_error")
        self.assertIsInstance(search.estimator["imputer"], SimpleImputer)
        self.assertIsInstance(search.estimator["scaler"], StandardScaler)
        self.assertEqual(search.estimator["svr"].kernel, "rbf")
        np.testing.assert_allclose(search.best_estimator_["scaler"].mean_[0], 3.5)
        self.assertTrue(np.isfinite(search.predict(X)).all())

    def test_published_mazhnik_oganov_diamond_example(self):
        # Original Table I: E=1114 GPa, nu=0.07, predicted H=98.9 GPa.
        E, nu = 1114.0, 0.07
        B, G = E / (3 * (1 - 2 * nu)), E / (2 * (1 + nu))
        self.assertAlmostEqual(float(mazhnik_oganov_hardness(B, G)), 98.9, delta=0.1)

    def test_chen_tian_limits_and_no_clipping(self):
        # k=G/B=1, G=1 makes both equations simple independent checks.
        self.assertAlmostEqual(float(chen_hardness(1, 1)), -1.0)
        self.assertAlmostEqual(float(tian_hardness(1, 1)), 0.92)
        for function in (chen_hardness, tian_hardness, mazhnik_oganov_hardness):
            with self.assertRaises(ValueError):
                function(0, 1)
            with self.assertRaises(ValueError):
                function(1, np.nan)

    def test_tail_uses_true_target_and_includes_threshold(self):
        result = metrics([-1, 20, 30], [100, 0, 40])
        self.assertEqual(result["n_tail"], 2)
        self.assertEqual(result["tail_mae"], 15)
        self.assertAlmostEqual(result["val_mae"], 131 / 3)
        self.assertIsNone(metrics([1], [2])["tail_mae"])
        with self.assertRaises(ValueError):
            metrics([1, 20], [1, np.nan])

    def test_raw_negative_svr_bulk_modulus_is_not_projected(self):
        np.testing.assert_array_equal(chen_hardness([-2, 2], [1, 1]),
                                      chen_hardness([2, 2], [1, 1]))
        with self.assertRaises(ValueError):
            chen_hardness(1, -1)

    def test_ledger_preserves_header_order_and_existing_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "results.csv"
            original = b"search,descriptor_set,complexity,val_mae\r\nold,old,1,2\r\n"
            path.write_bytes(original)
            row = {"descriptor_set": "baseline_example", "val_mae": "3.000000",
                   "complexity": 0, "search": "baseline"}
            append_results(path, [row])
            self.assertTrue(path.read_bytes().startswith(original))
            with path.open(newline="") as f:
                self.assertEqual(list(csv.DictReader(f))[-1], {k: str(v) for k, v in row.items()})


if __name__ == "__main__":
    unittest.main()
