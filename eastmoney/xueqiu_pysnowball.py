"""pysnowball 封装：研报/资金/行情等需登录接口。"""

from __future__ import annotations

import time
from typing import Any, Callable

from eastmoney.xueqiu import code_to_xq_symbol
from eastmoney.xueqiu_auth import XueqiuAuthRequired, ensure_xueqiu_cookie

SUPPORTED_TYPES = (
    "report",
    "earningforecast",
    "capital_flow",
    "capital_history",
    "margin",
    "blocktrans",
    "quote",
    "pankou",
)


def _ts_ms_to_str(ts: Any) -> str | None:
    if not ts:
        return None
    try:
        val = float(ts)
        if val > 1e12:
            val /= 1000
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(val))
    except (TypeError, ValueError, OSError):
        return None


def _call_ball(fn: Callable[..., Any], symbol: str, **kwargs: Any) -> Any:
    ensure_xueqiu_cookie()
    try:
        import pysnowball as ball
    except ImportError as exc:
        raise RuntimeError("请安装 pysnowball: pip install pysnowball") from exc
    return fn(symbol, **kwargs) if kwargs else fn(symbol)


def fetch_xueqiu_data(
    code: str,
    data_type: str = "report",
    *,
    limit: int = 10,
    try_browser: bool = True,
) -> dict[str, Any]:
    """统一入口：调用 pysnowball 并返回原始 + 格式化条目。"""
    data_type = (data_type or "report").lower()
    if data_type not in SUPPORTED_TYPES:
        raise ValueError(f"不支持的 data_type: {data_type}，可选 {SUPPORTED_TYPES}")

    symbol = code_to_xq_symbol(code)
    try:
        ensure_xueqiu_cookie(try_browser=try_browser)
    except XueqiuAuthRequired:
        raise

    import pysnowball as ball

    raw: Any
    if data_type == "report":
        raw = ball.report(symbol)
        rows = _format_report_rows(raw, limit=limit)
    elif data_type == "earningforecast":
        raw = ball.earningforecast(symbol)
        rows = _format_report_rows(raw, limit=limit, provider="xueqiu_forecast")
    elif data_type == "capital_flow":
        raw = ball.capital_flow(symbol)
        rows = _format_capital_flow(raw)
    elif data_type == "capital_history":
        raw = ball.capital_history(symbol, count=min(limit, 60))
        rows = _format_capital_history(raw, limit=limit)
    elif data_type == "margin":
        raw = ball.margin(symbol, size=min(limit, 180))
        rows = _format_margin(raw, limit=limit)
    elif data_type == "blocktrans":
        raw = ball.blocktrans(symbol, size=min(limit, 30))
        rows = _format_blocktrans(raw, limit=limit)
    elif data_type == "quote":
        raw = ball.quotec(symbol)
        rows = _format_quote(raw, symbol=symbol)
    elif data_type == "pankou":
        raw = ball.pankou(symbol)
        rows = _format_pankou(raw, symbol=symbol)
    else:
        raw = {}
        rows = []

    return {
        "code": code.zfill(6),
        "symbol": symbol,
        "data_type": data_type,
        "provider": "pysnowball",
        "rows": rows,
        "raw": raw,
    }


def _format_report_rows(
    raw: Any,
    *,
    limit: int,
    provider: str = "xueqiu_report",
) -> list[dict[str, Any]]:
    items: list[Any] = []
    if isinstance(raw, dict):
        items = raw.get("data") or raw.get("list") or []
    elif isinstance(raw, list):
        items = raw

    rows: list[dict[str, Any]] = []
    for item in items[:limit]:
        if not isinstance(item, dict):
            continue
        title = item.get("title") or item.get("name") or item.get("report_title") or "雪球研报"
        summary = (
            item.get("summary")
            or item.get("description")
            or item.get("target_price")
            or item.get("rating")
            or ""
        )
        target = item.get("target") or item.get("url")
        url = target if str(target).startswith("http") else f"https://xueqiu.com{target or ''}"
        rows.append(
            {
                "time": _ts_ms_to_str(item.get("created_at") or item.get("pub_date")),
                "title": str(title),
                "summary": str(summary)[:500],
                "provider": provider,
                "url": url,
            }
        )
    return rows


def _format_capital_flow(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, dict):
        return []
    data = raw.get("data") or raw
    if isinstance(data, list) and data:
        data = data[0]
    if not isinstance(data, dict):
        return []
    parts = []
    for key, label in (
        ("main_net_inflow", "主力净流入"),
        ("super_net_inflow", "超大单净流入"),
        ("big_net_inflow", "大单净流入"),
        ("medium_net_inflow", "中单净流入"),
        ("small_net_inflow", "小单净流入"),
    ):
        if key in data:
            parts.append(f"{label} {data[key]}")
    return [
        {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "title": "雪球资金流向",
            "summary": "；".join(parts) or str(data)[:500],
            "provider": "xueqiu_capital_flow",
            "url": f"https://xueqiu.com/S/{data.get('symbol', '')}",
        }
    ]


def _format_capital_history(raw: Any, *, limit: int) -> list[dict[str, Any]]:
    items = (raw.get("data") or raw.get("items") or []) if isinstance(raw, dict) else []
    rows: list[dict[str, Any]] = []
    for item in items[:limit]:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "time": str(item.get("date") or item.get("timestamp") or ""),
                "title": f"资金历史 主力 {item.get('main_net_inflow', item.get('amount', '—'))}",
                "summary": str(item)[:400],
                "provider": "xueqiu_capital_history",
            }
        )
    return rows


def _format_margin(raw: Any, *, limit: int) -> list[dict[str, Any]]:
    items = (raw.get("data") or raw.get("items") or []) if isinstance(raw, dict) else []
    rows: list[dict[str, Any]] = []
    for item in items[:limit]:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "time": str(item.get("date") or ""),
                "title": f"融资融券 balance {item.get('balance', '—')}",
                "summary": str(item)[:400],
                "provider": "xueqiu_margin",
            }
        )
    return rows


def _format_blocktrans(raw: Any, *, limit: int) -> list[dict[str, Any]]:
    items = (raw.get("data") or raw.get("items") or []) if isinstance(raw, dict) else []
    rows: list[dict[str, Any]] = []
    for item in items[:limit]:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "time": str(item.get("trade_date") or item.get("date") or ""),
                "title": f"大宗交易 成交价 {item.get('price', '—')}",
                "summary": str(item)[:400],
                "provider": "xueqiu_blocktrans",
            }
        )
    return rows


def _format_quote(raw: Any, *, symbol: str) -> list[dict[str, Any]]:
    data = raw
    if isinstance(raw, dict) and raw.get("data"):
        data = raw["data"]
        if isinstance(data, list) and data:
            data = data[0]
    if not isinstance(data, dict):
        return []
    return [
        {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "title": f"{data.get('name', symbol)} 现价 {data.get('current', data.get('last_close', '—'))}",
            "summary": (
                f"涨跌 {data.get('chg', data.get('percent', '—'))}% "
                f"额 {data.get('amount', '—')} 量 {data.get('volume', '—')}"
            ),
            "provider": "xueqiu_quote",
            "url": f"https://xueqiu.com/S/{symbol}",
        }
    ]


def _format_pankou(raw: Any, *, symbol: str) -> list[dict[str, Any]]:
    if not isinstance(raw, dict):
        return []
    data = raw.get("data") or raw
    return [
        {
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "title": f"{symbol} 盘口",
            "summary": str(data)[:500],
            "provider": "xueqiu_pankou",
            "url": f"https://xueqiu.com/S/{symbol}",
        }
    ]
