"""常量与请求头。"""

from __future__ import annotations

UT_TOKEN = "fa5fd1943c7e38603317b5283aa9671d"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://quote.eastmoney.com/",
    "Accept": "application/json",
}

# 市场编号: 沪 1, 深 0, 北 0 (8/4 开头)
MARKET_PREFIX = {
    "sh": "1",
    "sz": "0",
    "bj": "0",
}

QUOTE_URL = "https://push2.eastmoney.com/api/qt/stock/get"
QUOTE_LIST_URL = "https://push2.eastmoney.com/api/qt/clist/get"
KLINE_URL = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
FUND_FLOW_URL = "https://push2.eastmoney.com/api/qt/stock/fflow/daykline/get"
MARKET_FUND_FLOW_URL = "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
SEARCH_URL = "https://searchapi.eastmoney.com/api/suggest/get"
CHIP_URL = "https://push2his.eastmoney.com/api/qt/stock/cyq/get"
BOARD_LIST_URL = "https://push2.eastmoney.com/api/qt/clist/get"
BOARD_KLINE_URL = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
NEWS_LIST_URL = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
FAST_NEWS_URL = "https://np-weblist.eastmoney.com/comm/web/getFastNewsList"

KLT_MAP = {
    "daily": 101,
    "weekly": 102,
    "monthly": 103,
    "1min": 1,
    "5min": 5,
    "15min": 15,
    "30min": 30,
    "60min": 60,
}

FQT_MAP = {"none": 0, "qfq": 1, "hfq": 2}

QUOTE_FIELDS = {
    "f57": "code",
    "f58": "name",
    "f43": "price",
    "f170": "change_pct",
    "f169": "change_amount",
    "f46": "open",
    "f44": "high",
    "f45": "low",
    "f60": "prev_close",
    "f47": "volume",
    "f48": "amount",
    "f168": "turnover_rate",
    "f162": "pe_ttm",
    "f167": "pb",
    "f116": "total_market_cap",
    "f117": "float_market_cap",
}
