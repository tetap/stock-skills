"""事件类数据：股东、龙虎榜、资讯。"""

from __future__ import annotations

from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.config import DATACENTER_URL


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
