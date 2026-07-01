import unittest

from eastmoney.alpha360 import build_alpha360_from_bars


def _mock_bars(n: int = 60) -> list[dict]:
    bars = []
    for i in range(n):
        close = 10.0 + i * 0.1
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


class TestAlpha360(unittest.TestCase):
    def test_shapes(self) -> None:
        built = build_alpha360_from_bars(_mock_bars(60), include_tensor=True)
        self.assertEqual(len(built["tensor_rnn"]), 60)
        self.assertEqual(len(built["tensor_rnn"][0]), 6)
        self.assertEqual(len(built["tensor_conv"]), 6)
        self.assertEqual(len(built["tensor_conv"][0]), 60)
        self.assertEqual(len(built["flat_qlib"]), 360)

    def test_close0_is_one(self) -> None:
        built = build_alpha360_from_bars(_mock_bars(60), include_tensor=True)
        close_channel = built["tensor_conv"][3]
        self.assertAlmostEqual(close_channel[-1], 1.0)
        self.assertAlmostEqual(built["tensor_rnn"][-1][3], 1.0)

    def test_volume0_is_one(self) -> None:
        built = build_alpha360_from_bars(_mock_bars(60), include_tensor=True)
        vol_channel = built["tensor_conv"][5]
        self.assertAlmostEqual(vol_channel[-1], 1.0)

    def test_qlib_flat_order(self) -> None:
        built = build_alpha360_from_bars(_mock_bars(60), include_tensor=True)
        close_in_flat = built["flat_qlib"][:60]
        self.assertEqual(close_in_flat, built["tensor_conv"][3])
        open_in_flat = built["flat_qlib"][60:120]
        self.assertEqual(open_in_flat, built["tensor_conv"][0])

    def test_summary_without_tensor(self) -> None:
        built = build_alpha360_from_bars(_mock_bars(60), include_tensor=False)
        self.assertNotIn("tensor_rnn", built)
        self.assertIn("sequence_summary", built)
        self.assertEqual(built["sequence_summary"]["pattern"], "上升通道")

    def test_insufficient_bars(self) -> None:
        with self.assertRaises(ValueError):
            build_alpha360_from_bars(_mock_bars(30), seq_len=60)


if __name__ == "__main__":
    unittest.main()
