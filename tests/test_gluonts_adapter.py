"""GluonTS 长表适配（无 gluonts 时 skip）。"""

from __future__ import annotations

import unittest

from eastmoney.gluonts_adapter import GLUONTS_AVAILABLE, bars_to_long_dataframe, gluonts_status


class TestGluontsAdapter(unittest.TestCase):
    def test_status_keys(self) -> None:
        st = gluonts_status()
        self.assertIn("available", st)
        self.assertIn("models", st)
        self.assertIn("gluonts_deepar", st["models"])
        self.assertIn("gluonts_tft", st["models"])

    @unittest.skipUnless(GLUONTS_AVAILABLE, "未安装 gluonts")
    def test_bars_to_long_dataframe(self) -> None:
        bars = [
            {
                "date": "2026-01-01",
                "open": 10,
                "high": 11,
                "low": 9,
                "close": 10.5,
                "volume": 1000,
                "amount": 10500,
            },
            {
                "date": "2026-01-02",
                "open": 10.5,
                "high": 11,
                "low": 10,
                "close": 10.8,
                "volume": 1100,
                "amount": 11880,
            },
        ]
        df = bars_to_long_dataframe("1.600519", bars)
        self.assertEqual(len(df), 2)
        self.assertIn("item_id", df.columns)
        self.assertIn("timestamp", df.columns)
        self.assertIn("target", df.columns)
        self.assertIn("return_1d", df.columns)


if __name__ == "__main__":
    unittest.main()
