"""基本面与估值。"""

from __future__ import annotations

from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.config import DATACENTER_URL
from eastmoney.quote import get_realtime_quote


def get_company_profile(client: EastMoneyClient, secid: str, code: str) -> dict[str, Any]:
    params = {
        "reportName": "RPT_F10_BASIC_ORGINFO",
        "columns": (
            "SECUCODE,SECURITY_CODE,SECURITY_NAME_ABBR,ORG_NAME,EM2016,"
            "TRADE_MARKET,FOUND_DATE,LISTING_DATE,INDUSTRYCSRC1,MAIN_BUSINESS"
        ),
        "filter": f'(SECURITY_CODE="{code}")',
        "pageNumber": "1",
        "pageSize": "1",
        "source": "WEB",
        "client": "WEB",
    }
    data = client.get_json(
        DATACENTER_URL,
        params,
        cache_key=f"profile:{code}",
        cache_ttl=86400,
    )
    rows = (data.get("result") or {}).get("data") or []
    if not rows:
        return {"secid": secid, "code": code}
    row = rows[0]
    return {
        "secid": secid,
        "code": row.get("SECURITY_CODE"),
        "name": row.get("SECURITY_NAME_ABBR"),
        "org_name": row.get("ORG_NAME"),
        "industry": row.get("INDUSTRYCSRC1") or row.get("EM2016"),
        "main_business": row.get("MAIN_BUSINESS"),
        "listing_date": row.get("LISTING_DATE"),
        "market": row.get("TRADE_MARKET"),
    }


REPORT_TYPES = {
    "income": "RPT_LICO_FN_CPD",
    "balance": "RPT_LICO_FN_BSD",
    "cashflow": "RPT_LICO_FN_CSD",
}


def get_financial_statements(
    client: EastMoneyClient,
    code: str,
    *,
    report_type: str = "income",
    limit: int = 8,
) -> list[dict[str, Any]]:
    report = REPORT_TYPES.get(report_type, REPORT_TYPES["income"])
    params = {
        "reportName": report,
        "columns": "ALL",
        "filter": f'(SECURITY_CODE="{code}")',
        "pageNumber": "1",
        "pageSize": str(limit),
        "sortColumns": "REPORTDATE",
        "sortTypes": "-1",
        "source": "WEB",
        "client": "WEB",
    }
    data = client.get_json(
        DATACENTER_URL,
        params,
        cache_key=f"fin:{code}:{report_type}:{limit}",
        cache_ttl=86400,
    )
    return (data.get("result") or {}).get("data") or []


def get_valuation_metrics(client: EastMoneyClient, secid: str) -> dict[str, Any]:
    quote = get_realtime_quote(client, secid)
    return {
        "secid": secid,
        "code": quote.get("code"),
        "name": quote.get("name"),
        "price": quote.get("price"),
        "pe_ttm": quote.get("pe_ttm"),
        "pb": quote.get("pb"),
        "total_market_cap": quote.get("total_market_cap"),
        "float_market_cap": quote.get("float_market_cap"),
        "turnover_rate": quote.get("turnover_rate"),
    }
