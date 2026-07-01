"""量化训练：embargo 切分与 LGB 调参结构。"""

from __future__ import annotations

import unittest

from eastmoney.backtest import Sample
from eastmoney.quant_training import (
    LGB_TUNED_PARAMS,
    temporal_split_with_embargo,
)


class TestQuantTraining(unittest.TestCase):
    def test_embargo_reduces_overlap(self) -> None:
        samples = [
            Sample(date=f"2026-01-{i:02d}", secid="1.600519", features=[1.0], label=0.01 * i)
            for i in range(1, 21)
        ]
        train, test = temporal_split_with_embargo(samples, train_ratio=0.8, embargo_days=3)
        self.assertGreater(len(train), 0)
        self.assertGreater(len(test), 0)
        train_dates = {s.date for s in train}
        test_dates = {s.date for s in test}
        self.assertFalse(train_dates & test_dates)

    def test_lgb_tuned_has_regularization(self) -> None:
        self.assertIn("lambda_l1", LGB_TUNED_PARAMS)
        self.assertIn("feature_fraction", LGB_TUNED_PARAMS)
        self.assertLessEqual(LGB_TUNED_PARAMS["learning_rate"], 0.05)


if __name__ == "__main__":
    unittest.main()
