"""短线盯盘 / 涨停基因 — 东方财富 datacenter 官方接口。"""

from __future__ import annotations

from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.config import DATACENTER_URL


def get_short_term_monitor(
    client: EastMoneyClient,
    code: str,
) -> dict[str, Any]:
    """涨停基因 + 短线盯盘汇总（RPT_INTSELECTION_MONITOR，与 App 同源）。"""
    params = {
        "reportName": "RPT_INTSELECTION_MONITOR",
        "columns": "ALL",
        "filter": f'(SECURITY_CODE="{code}")',
        "pageNumber": "1",
        "pageSize": "1",
        "source": "WEB",
        "client": "WEB",
    }
    data = client.get_json(
        DATACENTER_URL,
        params,
        cache_key=f"short_monitor:{code}",
        cache_ttl=1800,
    )
    rows = (data.get("result") or {}).get("data") or []
    if not rows:
        return {"code": code, "error": "无短线盯盘数据"}
    row = rows[0]
    return {
        "code": code,
        "name": row.get("SECURITY_NAME_ABBR"),
        "board": row.get("BOARD_NAME"),
        "limit_up_gene_score": row.get("ZTJY"),
        "limit_up_days_year": row.get("HIGHDAYS_YEAR"),
        "limit_down_days": row.get("LLIMITEDDAYS"),
        "first_board_seal_rate_pct": row.get("SEALING_RATE_YEAR"),
        "avg_price_5d": row.get("AVGPRICE_5DAYS"),
        "avg_price_10d": row.get("AVGPRICE_10DAYS"),
        "avg_price_20d": row.get("AVGPRICE_20DAYS"),
        "has_margin": row.get("IS_MARGININFO") == 1,
        "_source": "RPT_INTSELECTION_MONITOR",
    }


def get_limit_up_history(
    client: EastMoneyClient,
    code: str,
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """涨跌停明细（RPT_INTSELECTION_LIMITUP）。"""
    params = {
        "reportName": "RPT_INTSELECTION_LIMITUP",
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
        cache_key=f"limitup_hist:{code}:{limit}",
        cache_ttl=3600,
    )
    rows = (data.get("result") or {}).get("data") or []
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(
            {
                "date": (row.get("TRADE_DATE") or "")[:10],
                "last_limit_up_time": row.get("LAST_LIMITUP_TIME"),
            }
        )
    return out
