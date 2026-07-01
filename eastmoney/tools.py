"""统一工具入口，供 CLI 与 MCP 调用。"""

from __future__ import annotations

import os
from typing import Any

from eastmoney.alpha158 import get_alpha158_factors, get_alpha158_score
from eastmoney.alpha360 import get_alpha360_tensor
from eastmoney.alpha360_infer import get_alpha360_score
from eastmoney.chip import get_chip_distribution
from eastmoney.client import EastMoneyClient
from eastmoney.events import (
    get_dragon_tiger,
    get_major_events,
    get_news_and_reports,
    get_shareholder_count,
    get_shareholders,
)
from eastmoney.fallback import available as akshare_available
from eastmoney.fallback import run_fallback
from eastmoney.financial import get_company_profile, get_financial_statements, get_valuation_metrics
from eastmoney.fund_flow import get_fund_flow_rank, get_market_fund_flow, get_stock_fund_flow
from eastmoney.historical import compare_performance, get_historical_series
from eastmoney.kline import get_kline
from eastmoney.news import get_market_news
from eastmoney.quote import get_market_snapshot, get_realtime_quote
from eastmoney.quant import get_quant_technical
from eastmoney.sector import get_sector_detail, get_sector_overview, search_sectors
from eastmoney.short_term import get_limit_up_history, get_short_term_monitor
from eastmoney.signals import get_indicator_interpretation, get_limit_up_gene
from eastmoney.symbols import resolve_symbol, search_stocks
from eastmoney.xueqiu import xueqiu_auth_guide, xueqiu_auth_status
from eastmoney.xueqiu_auth import XueqiuAuthRequired
from eastmoney.xueqiu_pysnowball import SUPPORTED_TYPES, fetch_xueqiu_data

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
    "get_company_profile",
    "get_financial_statements",
    "get_news_and_reports",
}

# 主接口「成功但空结果」时也尝试 AkShare
EMPTY_FALLBACK_TOOLS = {
    "get_company_profile",
    "get_financial_statements",
    "get_news_and_reports",
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
    if name == "get_shareholder_count":
        return get_shareholder_count(client, kwargs["code"], limit=int(kwargs.get("limit", 8)))
    if name == "get_major_events":
        return get_major_events(client, kwargs["code"], limit=int(kwargs.get("limit", 20)))
    if name == "get_dragon_tiger":
        return get_dragon_tiger(client, kwargs["code"], limit=int(kwargs.get("limit", 10)))
    if name == "get_news_and_reports":
        return get_news_and_reports(
            client,
            kwargs["code"],
            content_type=kwargs.get("content_type", "news"),
            limit=int(kwargs.get("limit", 10)),
            source=kwargs.get("source", "all"),
            stock_name=kwargs.get("stock_name"),
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
    if name == "get_market_news":
        return get_market_news(
            client,
            news_type=kwargs.get("news_type", "flash"),
            keyword=kwargs.get("keyword"),
            limit=int(kwargs.get("limit", 20)),
            source=kwargs.get("source", "all"),
        )
    if name == "search_sectors":
        return search_sectors(
            client,
            kwargs["query"],
            sector_type=kwargs.get("sector_type"),
            limit=int(kwargs.get("limit", 10)),
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
    if name == "get_indicator_interpretation":
        return get_indicator_interpretation(
            client,
            kwargs["secid"],
            code=kwargs.get("code"),
            limit=int(kwargs.get("limit", 250)),
        )
    if name == "get_limit_up_gene":
        return get_limit_up_gene(
            client,
            kwargs["secid"],
            code=kwargs.get("code"),
            limit=int(kwargs.get("limit", 250)),
        )
    if name == "get_short_term_monitor":
        return get_short_term_monitor(client, kwargs["code"])
    if name == "get_limit_up_history":
        return get_limit_up_history(client, kwargs["code"], limit=int(kwargs.get("limit", 10)))
    if name == "get_xueqiu_auth_guide":
        return xueqiu_auth_guide(reason=kwargs.get("reason", "missing_token"))
    if name == "get_xueqiu_auth_status":
        try_browser = kwargs.get("try_browser", True)
        if isinstance(try_browser, str):
            try_browser = try_browser.lower() in {"1", "true", "yes"}
        return xueqiu_auth_status(try_browser=bool(try_browser))
    if name == "get_xueqiu_data":
        tb = kwargs.get("try_browser", True)
        if isinstance(tb, str):
            tb = tb.lower() in {"1", "true", "yes"}
        return fetch_xueqiu_data(
            kwargs["code"],
            kwargs.get("data_type", "report"),
            limit=int(kwargs.get("limit", 10)),
            try_browser=bool(tb),
        )
    if name == "get_alpha360_tensor":
        include_tensor = kwargs.get("include_tensor", False)
        if isinstance(include_tensor, str):
            include_tensor = include_tensor.lower() in {"1", "true", "yes"}
        return get_alpha360_tensor(
            client,
            kwargs["secid"],
            seq_len=int(kwargs.get("seq_len", 60)),
            period=kwargs.get("period", "daily"),
            adjust=kwargs.get("adjust", "qfq"),
            include_tensor=bool(include_tensor),
        )
    if name == "get_alpha360_score":
        include_tensor = kwargs.get("include_tensor", False)
        if isinstance(include_tensor, str):
            include_tensor = include_tensor.lower() in {"1", "true", "yes"}
        return get_alpha360_score(
            client,
            kwargs["secid"],
            seq_len=int(kwargs.get("seq_len", 60)),
            period=kwargs.get("period", "daily"),
            adjust=kwargs.get("adjust", "qfq"),
            include_tensor=bool(include_tensor),
        )
    if name == "get_alpha158_factors":
        include_all = kwargs.get("include_all_factors", False)
        if isinstance(include_all, str):
            include_all = include_all.lower() in {"1", "true", "yes"}
        return get_alpha158_factors(
            client,
            kwargs["secid"],
            period=kwargs.get("period", "daily"),
            adjust=kwargs.get("adjust", "qfq"),
            include_all_factors=bool(include_all),
        )
    if name == "get_alpha158_score":
        include_all = kwargs.get("include_all_factors", False)
        if isinstance(include_all, str):
            include_all = include_all.lower() in {"1", "true", "yes"}
        return get_alpha158_score(
            client,
            kwargs["secid"],
            period=kwargs.get("period", "daily"),
            adjust=kwargs.get("adjust", "qfq"),
            include_all_factors=bool(include_all),
        )
    if name == "get_quant_technical":
        return get_quant_technical(
            client,
            kwargs["secid"],
            period=kwargs.get("period", "daily"),
            adjust=kwargs.get("adjust", "qfq"),
        )

    raise ValueError(f"未知工具: {name}")


def _is_empty_result(name: str, result: Any) -> bool:
    if name == "get_company_profile":
        return isinstance(result, dict) and not result.get("name") and not result.get("industry")
    if isinstance(result, list):
        return len(result) == 0
    return False


def _try_fallback(name: str, kwargs: dict[str, Any], primary_error: Exception | None = None) -> Any:
    if not FALLBACK_ENABLED or name not in FALLBACK_TOOLS or not akshare_available():
        if primary_error:
            raise primary_error
        return None
    try:
        return run_fallback(name, **kwargs)
    except Exception:
        if primary_error:
            raise primary_error
        return None


def run_tool(name: str, **kwargs: Any) -> Any:
    if name not in TOOL_NAMES:
        raise ValueError(f"未知工具: {name}")

    try:
        result = _run_primary(name, **kwargs)
        if (
            name in EMPTY_FALLBACK_TOOLS
            and _is_empty_result(name, result)
        ):
            fb = _try_fallback(name, kwargs)
            if fb is not None and not _is_empty_result(name, fb):
                return fb
        return result
    except XueqiuAuthRequired as auth_exc:
        return auth_exc.to_dict()
    except Exception as primary_error:
        fb = _try_fallback(name, kwargs, primary_error)
        if fb is not None:
            return fb
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
    "get_shareholder_count",
    "get_major_events",
    "get_dragon_tiger",
    "get_news_and_reports",
    "get_stock_fund_flow",
    "get_fund_flow_rank",
    "get_market_fund_flow",
    "get_chip_distribution",
    "get_historical_series",
    "compare_performance",
    "get_market_news",
    "search_sectors",
    "get_sector_overview",
    "get_sector_detail",
    "get_indicator_interpretation",
    "get_limit_up_gene",
    "get_short_term_monitor",
    "get_limit_up_history",
    "get_xueqiu_auth_guide",
    "get_xueqiu_auth_status",
    "get_xueqiu_data",
    "get_alpha360_tensor",
    "get_alpha360_score",
    "get_alpha158_factors",
    "get_alpha158_score",
    "get_quant_technical",
]
