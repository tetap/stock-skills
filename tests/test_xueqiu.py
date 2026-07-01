import unittest
from unittest.mock import MagicMock, patch

from eastmoney.xueqiu import (
    code_to_xq_symbol,
    xueqiu_auth_guide,
    xueqiu_auth_hint_row,
    xueqiu_hot_as_news,
    xueqiu_hot_stocks,
    xueqiu_stock_heat,
    xueqiu_stock_sentiment,
)


class TestXueqiu(unittest.TestCase):
    def test_code_to_symbol(self) -> None:
        self.assertEqual(code_to_xq_symbol("600519"), "SH600519")
        self.assertEqual(code_to_xq_symbol("002074"), "SZ002074")

    @patch("eastmoney.xueqiu.EastMoneyClient.get_json")
    def test_hot_stocks(self, mock_get: MagicMock) -> None:
        mock_get.return_value = {
            "data": {
                "list": [
                    {
                        "symbol": "SZ002074",
                        "name": "国轩高科",
                        "current": 25.5,
                        "pct": 3.2,
                        "tweet": 5301,
                    }
                ]
            }
        }
        client = MagicMock()
        client.get_json = mock_get
        rows = xueqiu_hot_stocks(client, limit=5)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["code"], "002074")
        self.assertEqual(rows[0]["metric"], 5301)

    @patch("eastmoney.xueqiu.xueqiu_hot_stocks")
    def test_stock_heat(self, mock_hot: MagicMock) -> None:
        mock_hot.return_value = [
            {"symbol": "SZ002074", "name": "国轩高科", "metric": 5301, "pct": 1.0, "price": 25.0},
        ]
        client = MagicMock()
        heat = xueqiu_stock_heat(client, "002074", max_pages=1)
        self.assertIsNotNone(heat)
        self.assertEqual(heat["tweet_rank"], 1)
        self.assertEqual(heat["tweet"], 5301)

    @patch("eastmoney.xueqiu.xueqiu_hot_stocks")
    def test_hot_as_news(self, mock_hot: MagicMock) -> None:
        mock_hot.return_value = [
            {
                "symbol": "SZ002074",
                "code": "002074",
                "name": "国轩高科",
                "price": 25.5,
                "change_pct": 3.2,
                "metric": 5301,
                "metric_type": "tweet",
            }
        ]
        client = MagicMock()
        rows = xueqiu_hot_as_news(client, limit=1)
        self.assertEqual(len(rows), 1)
        self.assertIn("雪球", rows[0]["title"])
        self.assertEqual(rows[0]["provider"], "xueqiu_hot")

    def test_auth_guide(self) -> None:
        guide = xueqiu_auth_guide(reason="missing_token")
        self.assertTrue(guide["auth_required"])
        self.assertIn("xq_a_token", guide["cookie_name"])
        self.assertIn("xueqiu.com", guide["login_url"])

    def test_auth_hint_row(self) -> None:
        row = xueqiu_auth_hint_row(reason="missing_token")
        self.assertEqual(row["provider"], "xueqiu_auth_hint")
        self.assertTrue(row["auth_required"])

    @patch("eastmoney.xueqiu.xueqiu_stock_posts")
    @patch("eastmoney.xueqiu.xueqiu_stock_heat")
    def test_sentiment_includes_hint_when_no_token(
        self,
        mock_heat: MagicMock,
        mock_posts: MagicMock,
    ) -> None:
        mock_heat.return_value = None
        mock_posts.return_value = ([], "missing_token")
        client = MagicMock()
        rows = xueqiu_stock_sentiment(client, "002074", limit=3)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["provider"], "xueqiu_auth_hint")


if __name__ == "__main__":
    unittest.main()
