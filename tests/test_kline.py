import unittest
from unittest.mock import MagicMock, patch

from eastmoney.tools import run_tool


class TestKlineImport(unittest.TestCase):
    @patch("eastmoney.tools._run_primary")
    def test_get_kline_registered(self, mock_primary: MagicMock) -> None:
        mock_primary.return_value = [{"date": "2026-01-01", "close": 1.0}]
        result = run_tool("get_kline", secid="0.002074", limit=3)
        mock_primary.assert_called_once()
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
