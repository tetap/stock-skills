import unittest
from unittest.mock import MagicMock, patch

from eastmoney.news_sources import em_stock_news, merge_news_rows, sina_stock_news


class TestNewsSources(unittest.TestCase):
    @patch("eastmoney.news_sources._em_stock_news_native")
    def test_em_stock_news(self, mock_native: MagicMock) -> None:
        mock_native.return_value = [
            {
                "time": "2026-07-01",
                "title": "国轩高科合作",
                "summary": "摘要",
                "media": "财联社",
                "url": "http://example.com",
                "provider": "eastmoney_search",
            }
        ]
        client = MagicMock()

        rows = em_stock_news(client, "002074", limit=5)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["provider"], "eastmoney_search")
        self.assertIn("国轩", rows[0]["title"])

    def test_merge_dedupes(self) -> None:
        a = [{"title": "A", "summary": "1"}]
        b = [{"title": "A", "summary": "2"}, {"title": "B", "summary": "3"}]
        merged = merge_news_rows(a, b, limit=5)
        self.assertEqual([x["title"] for x in merged], ["A", "B"])

    @patch("eastmoney.news_sources.sina_live_flash")
    @patch("eastmoney.news_sources.sina_market_roll")
    def test_sina_stock_filter(
        self,
        mock_roll: MagicMock,
        mock_live: MagicMock,
    ) -> None:
        mock_live.return_value = [
            {"title": "比亚迪储能签约", "summary": "与国轩高科合作"},
            {"title": "油价下跌", "summary": "原油"},
        ]
        mock_roll.return_value = []
        client = MagicMock()

        rows = sina_stock_news(client, "002074", name="国轩高科", limit=5)

        self.assertEqual(len(rows), 1)
        self.assertIn("国轩", rows[0]["summary"])


if __name__ == "__main__":
    unittest.main()
