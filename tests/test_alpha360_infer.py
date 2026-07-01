import unittest

from eastmoney.alpha360 import build_alpha360_from_bars
from eastmoney.alpha360_infer import score_alpha360, score_alpha360_heuristic


def _mock_bars(n: int = 60, *, trend: float = 0.1) -> list[dict]:
    bars = []
    for i in range(n):
        close = 10.0 + i * trend
        bars.append(
            {
                "date": f"2026-01-{i + 1:02d}",
                "open": close - 0.05,
                "high": close + 0.2,
                "low": close - 0.2,
                "close": close,
                "volume": 1000.0 + i * 10,
                "amount": (1000.0 + i * 10) * close,
            }
        )
    return bars


class TestAlpha360Infer(unittest.TestCase):
    def test_uptrend_positive_score(self) -> None:
        built = build_alpha360_from_bars(_mock_bars(60, trend=0.1), include_tensor=True)
        result = score_alpha360_heuristic(built)
        self.assertGreater(result["score"], 0)
        self.assertIn("偏多", result["verdict"])

    def test_downtrend_negative_score(self) -> None:
        built = build_alpha360_from_bars(_mock_bars(60, trend=-0.15), include_tensor=True)
        result = score_alpha360_heuristic(built)
        self.assertLess(result["score"], 0)

    def test_score_alpha360_fallback_heuristic(self) -> None:
        built = build_alpha360_from_bars(_mock_bars(60), include_tensor=True)
        result = score_alpha360(built)
        self.assertEqual(result["method"], "heuristic")
        self.assertIn("score", result)


if __name__ == "__main__":
    unittest.main()
