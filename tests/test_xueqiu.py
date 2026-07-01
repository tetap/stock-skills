import os
import unittest
from unittest.mock import MagicMock, patch

from eastmoney.xueqiu import (
    code_to_xq_symbol,
    xueqiu_auth_guide,
    xueqiu_auth_hint_row,
    xueqiu_auth_status,
    xueqiu_hot_as_news,
    xueqiu_hot_stocks,
    xueqiu_livenews,
    xueqiu_livenews_as_news,
    xueqiu_stock_heat,
    xueqiu_stock_posts,
    xueqiu_stock_sentiment,
)
from eastmoney.xueqiu_auth import (
    XUEQIU_LOGIN_URL,
    XueqiuAuthRequired,
    build_cookie_string,
    jar_to_cookie_string,
    load_browser_cookies,
    resolve_xueqiu_cookie,
)


class TestXueqiuAuth(unittest.TestCase):
    def test_build_cookie_string(self) -> None:
        self.assertEqual(build_cookie_string("abc123"), "xq_a_token=abc123;")
        self.assertEqual(
            build_cookie_string("abc123", "u42"),
            "xq_a_token=abc123;u=u42;",
        )

    def test_jar_to_cookie_string(self) -> None:
        self.assertEqual(
            jar_to_cookie_string({"xq_a_token": "a", "device_id": "d"}),
            "xq_a_token=a;device_id=d;",
        )

    @patch("eastmoney.xueqiu_auth._load_cookie_cache", return_value=(None, None))
    @patch("eastmoney.xueqiu_auth.load_browser_cookies", return_value=({}, "browser_not_logged_in"))
    def test_resolve_env_fallback(self, _mock_browser: MagicMock, _mock_cache: MagicMock) -> None:
        with patch.dict(os.environ, {"XUEQIU_TOKEN": "tok123"}, clear=False):
            os.environ.pop("XUEQIUTOKEN", None)
            cookie, source = resolve_xueqiu_cookie(try_browser=True)
        self.assertEqual(source, "env_xueqiu_token")
        self.assertIn("tok123", cookie or "")

    @patch("eastmoney.xueqiu_auth.load_browser_cookies")
    def test_resolve_browser_first(self, mock_browser: MagicMock) -> None:
        mock_browser.return_value = (
            {"xq_a_token": "from_browser", "u": "123"},
            "chrome",
        )
        cookie, source = resolve_xueqiu_cookie(try_browser=True)
        self.assertTrue(source.startswith("browser:"))
        self.assertIn("from_browser", cookie or "")

    def test_auth_required_message(self) -> None:
        exc = XueqiuAuthRequired()
        self.assertIn("xueqiu.com/hq", exc.user_message)
        d = exc.to_dict()
        self.assertTrue(d["interrupt"])

    def test_auth_guide_hq_url(self) -> None:
        guide = xueqiu_auth_guide()
        self.assertEqual(guide["login_url"], XUEQIU_LOGIN_URL)
        self.assertIn("/hq", guide["login_url"])


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

    @patch("eastmoney.xueqiu.xueqiu_hot_stocks")
    def test_stock_heat(self, mock_hot: MagicMock) -> None:
        mock_hot.return_value = [
            {"symbol": "SZ002074", "name": "国轩高科", "metric": 5301, "pct": 1.0, "price": 25.0},
        ]
        client = MagicMock()
        heat = xueqiu_stock_heat(client, "002074", max_pages=1)
        self.assertIsNotNone(heat)
        self.assertEqual(heat["tweet_rank"], 1)

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
        self.assertEqual(rows[0]["provider"], "xueqiu_hot")

    @patch("eastmoney.xueqiu._xq_session_get_json")
    def test_livenews(self, mock_get: MagicMock) -> None:
        mock_get.return_value = (
            {
                "items": [
                    {
                        "id": 123,
                        "text": "热门资讯测试标题内容",
                        "created_at": 1700000000000,
                        "target": "/123456789",
                    }
                ]
            },
            None,
        )
        client = MagicMock()
        rows, reason = xueqiu_livenews(client, limit=5)
        self.assertIsNone(reason)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["provider"], "xueqiu_livenews")
        self.assertIn("热门资讯", rows[0]["title"])

    @patch("eastmoney.xueqiu._xq_session_get_json")
    def test_livenews_as_news_no_auth_hint_when_empty(self, mock_get: MagicMock) -> None:
        mock_get.return_value = (None, "missing_token")
        client = MagicMock()
        rows = xueqiu_livenews_as_news(client, limit=3, require_auth=False)
        self.assertEqual(rows[0]["provider"], "xueqiu_auth_hint")

    def test_auth_hint_row_interrupt(self) -> None:
        row = xueqiu_auth_hint_row()
        self.assertTrue(row["interrupt"])
        self.assertIn("/hq", row["url"])

    @patch("eastmoney.xueqiu.resolve_xueqiu_cookie", return_value=(None, None))
    def test_posts_require_auth_raises(self, _mock: MagicMock) -> None:
        client = MagicMock()
        with self.assertRaises(XueqiuAuthRequired):
            xueqiu_stock_posts(client, "002074", require_auth=True)

    @patch("eastmoney.xueqiu.resolve_xueqiu_cookie", return_value=(None, None))
    def test_sentiment_hint_when_no_token(self, _mock: MagicMock) -> None:
        client = MagicMock()
        with patch("eastmoney.xueqiu.xueqiu_stock_heat", return_value=None):
            with patch("eastmoney.xueqiu._pysnowball_available", return_value=False):
                rows = xueqiu_stock_sentiment(client, "002074", limit=3)
        self.assertEqual(rows[0]["provider"], "xueqiu_auth_hint")

    @patch("eastmoney.xueqiu._xq_session_get_json")
    def test_posts_waf_returns_hint_not_raise(self, mock_get: MagicMock) -> None:
        mock_get.return_value = (None, "waf_captcha")
        client = MagicMock()
        with patch("eastmoney.xueqiu.resolve_xueqiu_cookie", return_value=("xq_a_token=abc;", "browser:chrome")):
            rows, reason = xueqiu_stock_posts(client, "600519", require_auth=False)
        self.assertEqual(rows, [])
        self.assertEqual(reason, "waf_captcha")

    @patch("eastmoney.xueqiu.xueqiu_stock_posts", return_value=([], "waf_captcha"))
    @patch("eastmoney.xueqiu.xueqiu_stock_heat")
    def test_sentiment_waf_includes_heat_and_hint(self, mock_heat: MagicMock, _mock_posts: MagicMock) -> None:
        mock_heat.return_value = {
            "symbol": "SH600519",
            "name": "贵州茅台",
            "metric": 83474,
            "tweet_rank": 2,
            "price": 1193.0,
            "change_pct": 0.6,
        }
        client = MagicMock()
        with patch("eastmoney.xueqiu.resolve_xueqiu_cookie", return_value=("xq_a_token=abc;", "browser:chrome")):
            with patch("eastmoney.xueqiu._pysnowball_available", return_value=False):
                rows = xueqiu_stock_sentiment(client, "600519", limit=3, include_auth_hint=True)
        providers = [r["provider"] for r in rows]
        self.assertIn("xueqiu_heat", providers)
        self.assertIn("xueqiu_waf_hint", providers)
        self.assertFalse(rows[-1]["interrupt"])

    def test_waf_auth_message(self) -> None:
        exc = XueqiuAuthRequired(
            reason="waf_captcha",
            detail="请在 Chrome 打开 https://xueqiu.com/S/SH600519 完成滑动验证。",
        )
        self.assertIn("滑动验证", exc.user_message)
        self.assertIn("已检测到", exc.user_message)

    @patch("eastmoney.xueqiu_auth.load_browser_cookies", return_value=({}, "browser_not_logged_in"))
    @patch("eastmoney.xueqiu_auth._load_cookie_cache", return_value=(None, None))
    def test_auth_status(self, _c: MagicMock, _b: MagicMock) -> None:
        with patch.dict(os.environ, {"XUEQIU_TOKEN": "abc"}, clear=False):
            os.environ.pop("XUEQIUTOKEN", None)
            st = xueqiu_auth_status(try_browser=False)
        self.assertTrue(st["authenticated"])
        self.assertEqual(st["cookie_source"], "env_xueqiu_token")


if __name__ == "__main__":
    unittest.main()
