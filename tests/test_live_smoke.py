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


if __name__ == "__main__":
    unittest.main()
