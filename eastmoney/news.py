"""市场资讯与热点：7×24 快讯、要闻、财经早餐。"""

from __future__ import annotations

from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.news_sources import (
    NEWS_COLUMNS,
    em_market_column,
    em_market_flash,
    filter_by_keyword,
    merge_news_rows,
    sina_live_flash,
    sina_market_roll,
)
from eastmoney.xueqiu import xueqiu_hot_as_news, xueqiu_livenews_as_news


def _append_xueqiu_livenews(
    groups: list[list[dict[str, Any]]],
    client: EastMoneyClient,
    *,
    limit: int,
    source: str,
) -> None:
    """雪球热门资讯 livenews/list.json?category=6（需 Cookie）。"""
    require_auth = source == "xueqiu"
    rows = xueqiu_livenews_as_news(
        client,
        limit=limit,
        require_auth=require_auth,
    )
    if require_auth:
        groups.append(rows)
        return
    news_only = [r for r in rows if r.get("provider") == "xueqiu_livenews"]
    if news_only:
        groups.append(news_only)


def get_market_news(
    client: EastMoneyClient,
    *,
    news_type: str = "flash",
    keyword: str | None = None,
    limit: int = 20,
    source: str = "all",
) -> list[dict[str, Any]]:
    """市场资讯。

    news_type: flash / headline / breakfast / sina_roll / sina_live / xueqiu_hot / xueqiu_livenews
    source: eastmoney | sina | xueqiu | all（默认合并多源）
    """
    fetch_limit = min(limit * 3, 50) if keyword else limit
    groups: list[list[dict[str, Any]]] = []

    if news_type in {"flash", "headline", "breakfast"}:
        if source in {"eastmoney", "all"}:
            if news_type == "flash":
                groups.append(em_market_flash(client, limit=fetch_limit))
            else:
                groups.append(
                    em_market_column(
                        client,
                        column=NEWS_COLUMNS[news_type],
                        limit=fetch_limit,
                    )
                )
        if source in {"sina", "all"} and news_type == "flash":
            groups.append(sina_live_flash(client, limit=fetch_limit))
            groups.append(sina_market_roll(client, limit=fetch_limit))
        if source in {"xueqiu", "all"} and news_type == "flash":
            _append_xueqiu_livenews(
                groups,
                client,
                limit=min(fetch_limit, 15),
                source=source,
            )
            groups.append(xueqiu_hot_as_news(client, limit=min(fetch_limit, 10)))
    elif news_type == "sina_roll":
        groups.append(sina_market_roll(client, limit=fetch_limit, keyword=keyword))
    elif news_type == "sina_live":
        groups.append(sina_live_flash(client, limit=fetch_limit))
    elif news_type == "xueqiu_hot":
        if source in {"xueqiu", "all", "eastmoney", "sina"}:
            groups.append(xueqiu_hot_as_news(client, limit=fetch_limit))
    elif news_type == "xueqiu_livenews":
        if source in {"xueqiu", "all", "eastmoney", "sina"}:
            _append_xueqiu_livenews(
                groups,
                client,
                limit=fetch_limit,
                source=source if source == "xueqiu" else "all",
            )
    else:
        raise ValueError(
            f"不支持的 news_type: {news_type}，"
            "可选 flash/headline/breakfast/sina_roll/sina_live/xueqiu_hot/xueqiu_livenews"
        )

    rows = merge_news_rows(*groups, limit=fetch_limit) if groups else []

    if keyword and news_type not in {"sina_roll"}:
        rows = filter_by_keyword(rows, keyword)

    return rows[:limit]
