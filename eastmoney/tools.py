"""统一工具入口，供 CLI 与 MCP 调用。"""

from __future__ import annotations

import os
from typing import Any

from eastmoney.chip import get_chip_distribution
from eastmoney.client import EastMoneyClient
from eastmoney.events import get_dragon_tiger, get_news_and_reports, get_shareholders
from eastmoney.fallback import available as akshare_available
from eastmoney.fallback import run_fallback
from eastmoney.financial import get_company_profile, get_financial_statements, get_valuation_metrics
from eastmoney.fund_flow import get_fund_flow_rank, get_market_fund_flow, get_stock_fund_flow
from eastmoney.historical import compare_performance, get_historical_series
from eastmoney.kline import get_kline
from eastmoney.quote import get_market_snapshot, get_realtime_quote
from eastmoney.sector import get_sector_detail, get_sector_overview
from eastmoney.symbols import resolve_symbol, search_stocks

_client: EastMoneyClient | None = None

FALLBACK_ENABLED = os.getenv("EASTMONEY_DISABLE_FALLBACK", "").lower() not in {"1", "true", "yes"}
FALLBACK_TOOLS = {
    "resolve_symbol",
    "get_realtime_quote",
    "get_kline",
    "get_stock_fund_flow",
    "get_fund_flow_rank",
    "get_market_fund_flow",
    "get_chip_distribution",
    "get_sector_overview",
    "get_sector_detail",
}


def get_client() -> EastMoneyClient:
    global _client
    if _client is None:
        _client = EastMoneyClient()
    return _client


def _run_primary(name: str, **kwargs: Any) -> Any:
    client = get_client()

    if name == "resolve_symbol":
        return resolve_symbol(client, kwargs["query"])
    if name == "search_stocks":
        return search_stocks(client, kwargs["query"], kwargs.get("limit", 10))
    if name == "get_realtime_quote":
        return get_realtime_quote(client, kwargs["secid"])
    if name == "get_kline":
        return get_kline(
            client,
            kwargs["secid"],
            period=kwargs.get("period", "daily"),
            adjust=kwargs.get("adjust", "qfq"),
            limit=int(kwargs.get("limit", 120)),
        )
    if name == "get_market_snapshot":
        return get_market_snapshot(
            client,
            sort=kwargs.get("sort", "change_pct"),
            limit=int(kwargs.get("limit", 20)),
        )
    if name == "get_company_profile":
        return get_company_profile(client, kwargs["secid"], kwargs["code"])
    if name == "get_financial_statements":
        return get_financial_statements(
            client,
            kwargs["code"],
            report_type=kwargs.get("report_type", "income"),
            limit=int(kwargs.get("limit", 8)),
        )
    if name == "get_valuation_metrics":
        return get_valuation_metrics(client, kwargs["secid"])
    if name == "get_shareholders":
        return get_shareholders(client, kwargs["code"], limit=int(kwargs.get("limit", 10)))
    if name == "get_dragon_tiger":
        return get_dragon_tiger(client, kwargs["code"], limit=int(kwargs.get("limit", 10)))
    if name == "get_news_and_reports":
        return get_news_and_reports(
            client,
            kwargs["code"],
            content_type=kwargs.get("content_type", "news"),
            limit=int(kwargs.get("limit", 10)),
        )
    if name == "get_stock_fund_flow":
        return get_stock_fund_flow(client, kwargs["secid"], limit=int(kwargs.get("limit", 20)))
    if name == "get_fund_flow_rank":
        return get_fund_flow_rank(client, limit=int(kwargs.get("limit", 20)))
    if name == "get_market_fund_flow":
        return get_market_fund_flow(client, limit=int(kwargs.get("limit", 20)))
    if name == "get_chip_distribution":
        return get_chip_distribution(client, kwargs["secid"], limit=int(kwargs.get("limit", 60)))
    if name == "get_historical_series":
        indicators = kwargs.get("indicators")
        if isinstance(indicators, str):
            indicators = [x.strip() for x in indicators.split(",") if x.strip()]
        return get_historical_series(
            client,
            kwargs["secid"],
            period=kwargs.get("period", "daily"),
            adjust=kwargs.get("adjust", "qfq"),
            limit=int(kwargs.get("limit", 250)),
            indicators=indicators,
        )
    if name == "compare_performance":
        return compare_performance(
            client,
            kwargs["secid"],
            benchmark_code=kwargs.get("benchmark_code", "000300"),
            limit=int(kwargs.get("limit", 250)),
        )
    if name == "get_sector_overview":
        return get_sector_overview(
            client,
            sector_type=kwargs.get("sector_type", "industry"),
            sort=kwargs.get("sort", "change_pct"),
            limit=int(kwargs.get("limit", 30)),
        )
    if name == "get_sector_detail":
        return get_sector_detail(
            client,
            board_code=kwargs.get("board_code"),
            board_name=kwargs.get("board_name"),
            sector_type=kwargs.get("sector_type", "industry"),
            detail_type=kwargs.get("detail_type", "members"),
            limit=int(kwargs.get("limit", 50)),
        )

    raise ValueError(f"未知工具: {name}")


def run_tool(name: str, **kwargs: Any) -> Any:
    if name not in TOOL_NAMES:
        raise ValueError(f"未知工具: {name}")

    try:
        return _run_primary(name, **kwargs)
    except Exception as primary_error:
        if not FALLBACK_ENABLED or name not in FALLBACK_TOOLS or not akshare_available():
            raise primary_error
        try:
            return run_fallback(name, **kwargs)
        except Exception:
            raise primary_error


TOOL_NAMES = [
    "resolve_symbol",
    "search_stocks",
    "get_realtime_quote",
    "get_kline",
    "get_market_snapshot",
    "get_company_profile",
    "get_financial_statements",
    "get_valuation_metrics",
    "get_shareholders",
    "get_dragon_tiger",
    "get_news_and_reports",
    "get_stock_fund_flow",
    "get_fund_flow_rank",
    "get_market_fund_flow",
    "get_chip_distribution",
    "get_historical_series",
    "compare_performance",
    "get_sector_overview",
    "get_sector_detail",
]
