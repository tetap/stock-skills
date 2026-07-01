import unittest

from eastmoney.alpha158 import build_alpha158_from_bars, score_alpha158_heuristic


def _mock_bars(n: int = 65, *, trend: float = 0.1) -> list[dict]:
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


class TestAlpha158(unittest.TestCase):
    def test_factor_count(self) -> None:
        built = build_alpha158_from_bars(_mock_bars(65), include_all_factors=True)
        self.assertGreaterEqual(built["factor_count"], 158)

    def test_build_summary(self) -> None:
        built = build_alpha158_from_bars(_mock_bars(65), include_all_factors=False)
        self.assertEqual(built["factor_count"], 159)
        self.assertIn("highlights", built)
        self.assertIn("inference", built)
        self.assertIn("MA20", built["highlights"])

    def test_uptrend_positive_score(self) -> None:
        built = build_alpha158_from_bars(_mock_bars(65, trend=0.2), include_all_factors=True)
        score = score_alpha158_heuristic(built["factors"])
        self.assertGreater(score["score"], 0)

    def test_insufficient_bars(self) -> None:
        with self.assertRaises(ValueError):
            build_alpha158_from_bars(_mock_bars(30))


if __name__ == "__main__":
    unittest.main()
