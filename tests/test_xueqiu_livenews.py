import unittest
from unittest.mock import MagicMock, patch

from eastmoney.news import get_market_news


class TestXueqiuLivenewsNews(unittest.TestCase):
    @patch("eastmoney.news.xueqiu_livenews_as_news")
    @patch("eastmoney.news.xueqiu_hot_as_news")
    @patch("eastmoney.news.em_market_flash")
    def test_flash_all_includes_livenews(
        self,
        mock_em: MagicMock,
        mock_hot: MagicMock,
        mock_live: MagicMock,
    ) -> None:
        mock_em.return_value = [{"time": "t", "title": "东财", "provider": "eastmoney"}]
        mock_live.return_value = [
            {"time": "t", "title": "雪球热门", "provider": "xueqiu_livenews", "summary": "x"}
        ]
        mock_hot.return_value = [
            {"time": "t", "title": "热榜", "provider": "xueqiu_hot", "summary": "x"}
        ]
        client = MagicMock()
        rows = get_market_news(client, news_type="flash", source="all", limit=10)
        providers = {r["provider"] for r in rows}
        self.assertIn("xueqiu_livenews", providers)

    @patch("eastmoney.news.xueqiu_livenews_as_news")
    def test_xueqiu_livenews_type(self, mock_live: MagicMock) -> None:
        mock_live.return_value = [
            {"time": "t", "title": "资讯1", "provider": "xueqiu_livenews", "summary": "a"}
        ]
        client = MagicMock()
        rows = get_market_news(client, news_type="xueqiu_livenews", source="xueqiu", limit=5)
        self.assertEqual(rows[0]["provider"], "xueqiu_livenews")


if __name__ == "__main__":
    unittest.main()
