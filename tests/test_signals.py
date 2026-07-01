"""指标解读与涨停基因单元测试。"""

from __future__ import annotations

import unittest

from eastmoney.signals import _collect_kdj_signals, _kdj, _limit_threshold


class SignalsTest(unittest.TestCase):
    def test_limit_threshold_main_board(self) -> None:
        self.assertEqual(_limit_threshold("002039"), 9.9)
        self.assertEqual(_limit_threshold("300750"), 19.5)

    def test_kdj_golden_cross_detection(self) -> None:
        highs = [10 + i * 0.1 for i in range(30)]
        lows = [9 + i * 0.1 for i in range(30)]
        closes = [9.5 + i * 0.15 for i in range(30)]
        ks, ds, js = _kdj(highs, lows, closes)
        signals = _collect_kdj_signals(ks, ds, js)
        self.assertIn("kdj_golden_cross", signals)


if __name__ == "__main__":
    unittest.main()
