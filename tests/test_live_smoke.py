"""真实接口冒烟（默认跳过；本地: LIVE=1 bash scripts/smoke_live.sh）。"""

from __future__ import annotations

import os
import unittest

from eastmoney.tools import run_tool

LIVE = os.getenv("LIVE", "").lower() in {"1", "true", "yes"}
SKIP = not LIVE


@unittest.skipUnless(LIVE, "设置 LIVE=1 启用真实接口冒烟")
class TestLiveSmoke(unittest.TestCase):
    def test_resolve_symbol(self) -> None:
        result = run_tool("resolve_symbol", query="600519")
        self.assertEqual(result["code"], "600519")
        self.assertEqual(result["secid"], "1.600519")

    def test_realtime_quote(self) -> None:
        result = run_tool("get_realtime_quote", secid="1.600519")
        self.assertIsInstance(result, dict)
        self.assertIn("price", result)
        self.assertGreater(float(result["price"]), 0)

    def test_market_news_flash(self) -> None:
        rows = run_tool("get_market_news", news_type="flash", source="eastmoney", limit=5)
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0)
        self.assertIn("title", rows[0])

    def test_review_protocol(self) -> None:
        proto = run_tool("get_review_protocol", flow="B")
        self.assertEqual(proto["flow"], "B")
        self.assertGreaterEqual(proto["min_tool_calls"], 20)

    def test_quant_technical_oos_status(self) -> None:
        result = run_tool("get_quant_technical", secid="1.600519")
        self.assertIn("oos_status", result)
        self.assertIn("quant_verdict", result)
        oos = result["oos_status"]
        if oos.get("available"):
            self.assertFalse(oos["oos_passed"])
            self.assertIn("oos_warning", result["quant_verdict"])

    def test_kline_daily(self) -> None:
        rows = run_tool(
            "get_kline",
            secid="1.600519",
            period="daily",
            limit=5,
        )
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0)
        self.assertIn("close", rows[0])

    def test_company_profile(self) -> None:
        result = run_tool("get_company_profile", secid="1.600519")
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("code"), "600519")

    def test_search_sectors_live(self) -> None:
        rows = run_tool("search_sectors", query="银行", limit=5)
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0)
        self.assertIn("name", rows[0])
        self.assertIn("match_score", rows[0])

    def test_review_protocol_c(self) -> None:
        proto = run_tool("get_review_protocol", flow="C")
        self.assertEqual(proto["flow"], "C")
        self.assertIn("search_sectors", proto["required_tools"])


if __name__ == "__main__":
    unittest.main()
