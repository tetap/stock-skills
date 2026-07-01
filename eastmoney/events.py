"""大事提醒、股东户数等 F10 事件数据。"""

from __future__ import annotations

from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.config import DATACENTER_URL
from eastmoney.news_sources import em_stock_news, merge_news_rows, sina_stock_news
from eastmoney.xueqiu import xueqiu_stock_sentiment


def get_shareholders(client: EastMoneyClient, code: str, *, limit: int = 10) -> list[dict[str, Any]]:
    params = {
        "reportName": "RPT_F10_EH_HOLDERS",
        "columns": "ALL",
        "filter": f'(SECURITY_CODE="{code}")',
        "pageNumber": "1",
        "pageSize": str(limit),
        "sortColumns": "END_DATE",
        "sortTypes": "-1",
        "source": "WEB",
        "client": "WEB",
    }
    data = client.get_json(
        DATACENTER_URL,
        params,
        cache_key=f"holders:{code}:{limit}",
        cache_ttl=86400,
    )
    return (data.get("result") or {}).get("data") or []


def get_shareholder_count(
    client: EastMoneyClient,
    code: str,
    *,
    limit: int = 8,
) -> list[dict[str, Any]]:
    """股东户数趋势（对应 App「股东户数」）。"""
    params = {
        "reportName": "RPT_F10_EH_HOLDERNUM",
        "columns": "ALL",
        "filter": f'(SECURITY_CODE="{code}")',
        "pageNumber": "1",
        "pageSize": str(limit),
        "sortColumns": "END_DATE",
        "sortTypes": "-1",
        "source": "WEB",
        "client": "WEB",
    }
    data = client.get_json(
        DATACENTER_URL,
        params,
        cache_key=f"holdernum:{code}:{limit}",
        cache_ttl=3600,
    )
    rows = (data.get("result") or {}).get("data") or []
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(
            {
                "date": (row.get("END_DATE") or "")[:10],
                "holder_count": row.get("HOLDER_TOTAL_NUM"),
                "holder_count_a": row.get("HOLDER_A_NUM"),
                "change_ratio_pct": row.get("TOTAL_NUM_RATIO"),
                "avg_hold_amount": row.get("AVG_HOLD_AMT"),
                "avg_free_shares": row.get("AVG_FREE_SHARES"),
                "hold_focus": row.get("HOLD_FOCUS"),
                "price_at_date": row.get("PRICE"),
            }
        )
    return out


def get_major_events(
    client: EastMoneyClient,
    code: str,
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """大事提醒时间线（对应 App「大事提醒」：报表披露、融资融券、资本运作、股东户数等）。"""
    params = {
        "reportName": "RPT_F10_REMIND",
        "columns": "ALL",
        "filter": f'(SECURITY_CODE="{code}")',
        "pageNumber": "1",
        "pageSize": str(limit),
        "sortColumns": "NOTICE_DATE",
        "sortTypes": "-1",
        "source": "WEB",
        "client": "WEB",
    }
    data = client.get_json(
        DATACENTER_URL,
        params,
        cache_key=f"major_events:{code}:{limit}",
        cache_ttl=1800,
    )
    rows = (data.get("result") or {}).get("data") or []
    out: list[dict[str, Any]] = []
    for row in rows:
        notice = (row.get("NOTICE_DATE") or "")[:10]
        out.append(
            {
                "date": notice,
                "event_type": row.get("EVENT_TYPE"),
                "event_type_code": row.get("EVENT_TYPE_CODE"),
                "specific_type": row.get("SPECIFIC_EVENTTYPE"),
                "content": row.get("LEVEL1_CONTENT"),
                "is_future": notice > _today_str(),
            }
        )
    return out


def _today_str() -> str:
    from datetime import date

    return date.today().isoformat()


def get_dragon_tiger(
    client: EastMoneyClient,
    code: str,
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    params = {
        "reportName": "RPT_DAILYBILLBOARD_DETAILS",
        "columns": "ALL",
        "filter": f'(SECURITY_CODE="{code}")',
        "pageNumber": "1",
        "pageSize": str(limit),
        "sortColumns": "TRADE_DATE",
        "sortTypes": "-1",
        "source": "WEB",
        "client": "WEB",
    }
    data = client.get_json(
        DATACENTER_URL,
        params,
        cache_key=f"lhb:{code}:{limit}",
        cache_ttl=3600,
    )
    return (data.get("result") or {}).get("data") or []


def get_news_and_reports(
    client: EastMoneyClient,
    code: str,
    *,
    content_type: str = "news",
    limit: int = 10,
    source: str = "all",
    stock_name: str | None = None,
) -> list[dict[str, Any]]:
    """个股新闻/公告/研报。新闻优先走东方财富搜索 API，并可合并新浪筛选结果。"""
    if content_type == "news":
        groups: list[list[dict[str, Any]]] = []
        if source in {"eastmoney", "all"}:
            groups.append(em_stock_news(client, code, limit=limit))
        if source in {"sina", "all"}:
            groups.append(
                sina_stock_news(client, code, name=stock_name, limit=limit)
            )
        if source in {"xueqiu", "all"}:
            groups.append(
                xueqiu_stock_sentiment(
                    client, code, name=stock_name, limit=min(limit, 5)
                )
            )
        rows = merge_news_rows(*groups, limit=limit) if len(groups) > 1 else (groups[0] if groups else [])
        if rows:
            return rows
        # 兼容旧 datacenter（多数已失效）
        return _get_news_datacenter(client, code, content_type=content_type, limit=limit)

    if content_type in {"announcement", "report"}:
        rows = _get_news_datacenter(client, code, content_type=content_type, limit=limit)
        if rows:
            return rows
        return []

    return _get_news_datacenter(client, code, content_type=content_type, limit=limit)


def _get_news_datacenter(
    client: EastMoneyClient,
    code: str,
    *,
    content_type: str,
    limit: int,
) -> list[dict[str, Any]]:
    report_map = {
        "news": "RPTA_WEB_NEWS",
        "announcement": "RPTA_APP_F10_NOTICE",
        "report": "RPT_REPORT_ANALYSIS",
    }
    report = report_map.get(content_type, report_map["news"])
    params = {
        "reportName": report,
        "columns": "ALL",
        "filter": f'(SECURITY_CODE="{code}")',
        "pageNumber": "1",
        "pageSize": str(limit),
        "sortColumns": "NOTICE_DATE,PUBLISH_DATE,REPORT_DATE",
        "sortTypes": "-1,-1,-1",
        "source": "WEB",
        "client": "WEB",
    }
    data = client.get_json(
        DATACENTER_URL,
        params,
        cache_key=f"{content_type}:{code}:{limit}",
        cache_ttl=1800,
    )
    return (data.get("result") or {}).get("data") or []
