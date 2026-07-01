"""市场资讯与热点：7×24 快讯、要闻、财经早餐。"""

from __future__ import annotations

import time
from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.config import FAST_NEWS_URL, NEWS_LIST_URL

NEWS_COLUMNS = {
    "headline": "350",
    "breakfast": "1207",
}


def get_market_news(
    client: EastMoneyClient,
    *,
    news_type: str = "flash",
    keyword: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """市场资讯。news_type: flash(7×24) / headline(要闻) / breakfast(财经早餐)。"""
    if news_type == "flash":
        rows = _fetch_flash_news(client, limit=limit)
    elif news_type in NEWS_COLUMNS:
        rows = _fetch_column_news(client, column=NEWS_COLUMNS[news_type], limit=limit)
    else:
        raise ValueError(f"不支持的 news_type: {news_type}，可选 flash/headline/breakfast")

    if keyword:
        kw = keyword.strip()
        rows = [
            r
            for r in rows
            if kw in (r.get("title") or "") or kw in (r.get("summary") or "")
        ]
    return rows[:limit]


def _fetch_flash_news(client: EastMoneyClient, *, limit: int) -> list[dict[str, Any]]:
    params = {
        "client": "web",
        "biz": "web_724",
        "fastColumn": "102",
        "sortEnd": "",
        "pageSize": str(min(limit, 50)),
        "req_trace": str(int(time.time() * 1000)),
    }
    data = client.get_json(
        FAST_NEWS_URL,
        params,
        cache_key=f"flash_news:{limit}",
        cache_ttl=120,
    )
    items = (data.get("data") or {}).get("fastNewsList") or []
    rows: list[dict[str, Any]] = []
    for item in items:
        rows.append(
            {
                "time": item.get("showTime"),
                "title": item.get("title"),
                "summary": item.get("summary"),
                "code": item.get("code"),
                "related": item.get("stockList") or [],
                "source": "flash",
            }
        )
    return rows


def _fetch_column_news(
    client: EastMoneyClient,
    *,
    column: str,
    limit: int,
) -> list[dict[str, Any]]:
    params = {
        "client": "web",
        "biz": "web_news_col",
        "column": column,
        "order": "1",
        "needInteractData": "0",
        "page_index": "1",
        "page_size": str(min(limit, 50)),
        "req_trace": str(int(time.time() * 1000)),
        "fields": "code,showTime,title,mediaName,summary,url",
        "types": "1,20",
    }
    data = client.get_json(
        NEWS_LIST_URL,
        params,
        cache_key=f"column_news:{column}:{limit}",
        cache_ttl=600,
    )
    items = (data.get("data") or {}).get("list") or []
    rows: list[dict[str, Any]] = []
    for item in items:
        rows.append(
            {
                "time": item.get("showTime"),
                "title": item.get("title"),
                "summary": item.get("summary"),
                "url": item.get("url"),
                "media": item.get("mediaName"),
                "code": item.get("code"),
                "source": "column",
            }
        )
    return rows
