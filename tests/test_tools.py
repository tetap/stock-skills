import unittest
from unittest.mock import MagicMock, patch

from eastmoney.tools import run_tool


class TestRunToolFallback(unittest.TestCase):
    @patch("eastmoney.tools._run_primary")
    @patch("eastmoney.tools.run_fallback")
    @patch("eastmoney.tools.akshare_available", return_value=True)
    @patch("eastmoney.tools.FALLBACK_ENABLED", True)
    def test_uses_fallback_on_primary_failure(
        self,
        _available: MagicMock,
        mock_fallback: MagicMock,
        mock_primary: MagicMock,
    ) -> None:
        mock_primary.side_effect = ConnectionError("blocked")
        mock_fallback.return_value = {"price": 1.0, "_data_source": "akshare"}

        result = run_tool("get_realtime_quote", secid="1.600519")

        self.assertEqual(result["price"], 1.0)
        mock_fallback.assert_called_once()

    @patch("eastmoney.tools._run_primary")
    @patch("eastmoney.tools.run_fallback")
    @patch("eastmoney.tools.akshare_available", return_value=True)
    @patch("eastmoney.tools.FALLBACK_ENABLED", True)
    def test_raises_primary_when_fallback_also_fails(
        self,
        _available: MagicMock,
        mock_fallback: MagicMock,
        mock_primary: MagicMock,
    ) -> None:
        mock_primary.side_effect = ConnectionError("primary")
        mock_fallback.side_effect = RuntimeError("fallback")

        with self.assertRaises(ConnectionError):
            run_tool("get_realtime_quote", secid="1.600519")

    @patch("eastmoney.tools._run_primary")
    @patch("eastmoney.tools.FALLBACK_ENABLED", True)
    def test_no_fallback_for_unsupported_tool(self, mock_primary: MagicMock) -> None:
        mock_primary.side_effect = ValueError("missing")

        with self.assertRaises(ValueError):
            run_tool("get_shareholders", code="600519")


class TestResolveSymbolLocal(unittest.TestCase):
    def test_numeric_code_without_network(self) -> None:
        result = run_tool("resolve_symbol", query="600519")
        self.assertEqual(result["code"], "600519")
        self.assertEqual(result["secid"], "1.600519")


class TestXueqiuInterrupt(unittest.TestCase):
    @patch("eastmoney.tools._run_primary")
    def test_auth_required_has_status(self, mock_primary: MagicMock) -> None:
        from eastmoney.xueqiu_auth import XueqiuAuthRequired

        mock_primary.side_effect = XueqiuAuthRequired(reason="missing_token")
        result = run_tool("get_news_and_reports", code="600519", source="xueqiu")
        self.assertEqual(result["status"], "auth_required")
        self.assertTrue(result["interrupt"])


if __name__ == "__main__":
    unittest.main()
