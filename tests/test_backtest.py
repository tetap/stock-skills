import unittest
from unittest.mock import MagicMock, patch

from eastmoney.backtest import (
    Sample,
    evaluate_predictions,
    get_kline_resilient,
    grid_search_thresholds,
    run_long_only_backtest,
    score_to_signal,
    spearman_ic,
    temporal_split,
)


class TestBacktest(unittest.TestCase):
    def test_temporal_split_80_20(self) -> None:
        samples = [Sample(date=f"2024-01-{i:02d}", secid="0.1", features=[1.0], label=0.01 * i) for i in range(1, 11)]
        train, test = temporal_split(samples, train_ratio=0.8)
        self.assertEqual(len(train), 8)
        self.assertEqual(len(test), 2)
        self.assertLess(train[-1].date, test[0].date)

    def test_spearman_ic_perfect(self) -> None:
        labels = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.assertAlmostEqual(spearman_ic(labels, labels), 1.0, places=4)

    def test_evaluate_predictions(self) -> None:
        preds = [1.0, -1.0, 0.5]
        labels = [0.8, -0.5, 0.1]
        m = evaluate_predictions(preds, labels)
        self.assertEqual(m["count"], 3.0)
        self.assertGreater(m["direction_accuracy"], 0.5)

    def test_long_only_backtest(self) -> None:
        rets = [0.01, 0.02, -0.01, 0.03]
        pos = [1, 1, 0, 1]
        stats = run_long_only_backtest(rets, pos, fee_rate=0.0)
        self.assertIn("sharpe", stats)
        self.assertIn("max_drawdown", stats)

    def test_grid_search_thresholds(self) -> None:
        scores = [10, 25, 30, 5, 22, 18, 28, 12]
        fwd = [0.01, 0.02, 0.03, -0.01, 0.015, 0.0, 0.025, -0.005]
        out = grid_search_thresholds(scores, fwd, long_grid=(15, 20, 25))
        self.assertIsNotNone(out["best"])
        self.assertEqual(len(out["grid"]), 3)

    def test_score_to_signal(self) -> None:
        self.assertEqual(score_to_signal(25), 1)
        self.assertEqual(score_to_signal(-25), -1)
        self.assertEqual(score_to_signal(0), 0)

    @patch("eastmoney.fallback.run_fallback")
    @patch("eastmoney.fallback.available", return_value=True)
    @patch("eastmoney.kline.get_kline")
    def test_get_kline_resilient_fallback(
        self,
        mock_kline: MagicMock,
        _available: MagicMock,
        mock_fallback: MagicMock,
    ) -> None:
        mock_kline.side_effect = ConnectionError("blocked")
        mock_fallback.return_value = [{"date": "2024-01-01", "close": 10.0, "open": 9.0, "high": 11.0, "low": 8.0, "volume": 1.0, "amount": 10.0}]
        client = MagicMock()
        rows = get_kline_resilient(client, "1.600519", limit=10)
        self.assertEqual(len(rows), 1)
        mock_fallback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
