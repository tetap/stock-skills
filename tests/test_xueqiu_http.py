import unittest
from unittest.mock import MagicMock, patch

from eastmoney.xueqiu_http import _is_waf_html, probe_stock_status_api


class TestXueqiuHttp(unittest.TestCase):
    def test_is_waf_html(self) -> None:
        self.assertTrue(_is_waf_html('<textarea id="renderData">{"_waf_x":1}</textarea>'))
        self.assertFalse(_is_waf_html('{"list":[]}'))

    @patch("eastmoney.xueqiu_http.xueqiu_http_get_json_via_cdp", return_value={"list": [{"text": "ok"}]})
    @patch(
        "eastmoney.xueqiu_http.xueqiu_http_get",
        return_value=(200, '<textarea id="renderData">{"_waf_x":1}</textarea>'),
    )
    def test_probe_cdp_fallback(self, _mock_get: MagicMock, _mock_cdp: MagicMock) -> None:
        out = probe_stock_status_api(symbol="SH600519", cookie="xq_a_token=abc;")
        self.assertFalse(out["curl_ok"])
        self.assertTrue(out["cdp_ok"])
        self.assertEqual(out["cdp_posts"], 1)


if __name__ == "__main__":
    unittest.main()
