"""Walk-forward 切分与回测。"""

from __future__ import annotations

import unittest

from eastmoney.walk_forward import SignalSeries, run_walk_forward_backtest, walk_forward_fold_ranges


class TestWalkForward(unittest.TestCase):
    def test_fold_ranges_cover_oos(self) -> None:
        folds = walk_forward_fold_ranges(200, n_folds=5, min_train=60)
        self.assertGreaterEqual(len(folds), 3)
        train0, test0 = folds[0]
        self.assertEqual(train0.start, 0)
        self.assertGreaterEqual(test0.start, 60)

    def test_walk_forward_combined_stats(self) -> None:
        n = 120
        series = SignalSeries(
            dates=[f"d{i}" for i in range(n)],
            scores=[25.0 if i % 3 == 0 else 5.0 for i in range(n)],
            forward_returns=[0.01 if i % 2 == 0 else -0.005 for i in range(n)],
            method="test",
        )
        out = run_walk_forward_backtest(series, n_folds=4, min_train=60, fee_rate=0.0)
        self.assertEqual(out["n_folds"], 4)
        self.assertIn("combined_out_of_sample", out)
        self.assertIn("sharpe", out["combined_out_of_sample"])


if __name__ == "__main__":
    unittest.main()
