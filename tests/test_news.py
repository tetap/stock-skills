import unittest
from unittest.mock import MagicMock, patch

from eastmoney.news import get_market_news


class TestMarketNews(unittest.TestCase):
    @patch("eastmoney.news._fetch_flash_news")
    def test_keyword_filter(self, mock_flash: MagicMock) -> None:
        mock_flash.return_value = [
            {"title": "比亚迪储能签约", "summary": "电池储能项目", "time": "2026-07-01"},
            {"title": "油价下跌", "summary": "原油", "time": "2026-07-01"},
        ]
        client = MagicMock()

        rows = get_market_news(client, news_type="flash", keyword="电池", limit=10)

        self.assertEqual(len(rows), 1)
        self.assertIn("电池", rows[0]["summary"])

    def test_invalid_news_type(self) -> None:
        client = MagicMock()
        with self.assertRaises(ValueError):
            get_market_news(client, news_type="unknown")


if __name__ == "__main__":
    unittest.main()
