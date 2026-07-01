"""历史数据分析与指标。"""

from __future__ import annotations

import math
from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.kline import get_kline
from eastmoney.symbols import code_to_secid


def _sma(values: list[float], window: int) -> list[float | None]:
    out: list[float | None] = []
    for i in range(len(values)):
        if i + 1 < window:
            out.append(None)
            continue
        out.append(sum(values[i + 1 - window : i + 1]) / window)
    return out


def _max_drawdown(closes: list[float]) -> float | None:
    if not closes:
        return None
    peak = closes[0]
    max_dd = 0.0
    for price in closes:
        peak = max(peak, price)
        if peak > 0:
            max_dd = max(max_dd, (peak - price) / peak)
    return round(max_dd * 100, 2)


def _period_return(closes: list[float]) -> float | None:
    if len(closes) < 2 or closes[0] == 0:
        return None
    return round((closes[-1] / closes[0] - 1) * 100, 2)


def _volatility(daily_returns: list[float]) -> float | None:
    if len(daily_returns) < 2:
        return None
    mean = sum(daily_returns) / len(daily_returns)
    var = sum((x - mean) ** 2 for x in daily_returns) / (len(daily_returns) - 1)
    return round(math.sqrt(var) * math.sqrt(252) * 100, 2)


def get_historical_series(
    client: EastMoneyClient,
    secid: str,
    *,
    period: str = "daily",
    adjust: str = "qfq",
    limit: int = 250,
    indicators: list[str] | None = None,
) -> dict[str, Any]:
    rows = get_kline(client, secid, period=period, adjust=adjust, limit=limit)
    closes = [r["close"] for r in rows]
    daily_returns = []
    for i in range(1, len(closes)):
        if closes[i - 1]:
            daily_returns.append(closes[i] / closes[i - 1] - 1)

    result: dict[str, Any] = {
        "secid": secid,
        "period": period,
        "bars": rows,
        "stats": {
            "period_return_pct": _period_return(closes),
            "max_drawdown_pct": _max_drawdown(closes),
            "annualized_volatility_pct": _volatility(daily_returns),
        },
    }

    indicators = indicators or []
    if "ma" in indicators:
        result["ma5"] = _sma(closes, 5)
        result["ma20"] = _sma(closes, 20)
        result["ma60"] = _sma(closes, 60)
    return result


def compare_performance(
    client: EastMoneyClient,
    secid: str,
    *,
    benchmark_code: str = "000300",
    period: str = "daily",
    limit: int = 250,
) -> dict[str, Any]:
    target = get_historical_series(client, secid, period=period, limit=limit)
    bench_secid = code_to_secid(benchmark_code)
    benchmark = get_historical_series(client, bench_secid, period=period, limit=limit)

    target_ret = target["stats"]["period_return_pct"]
    bench_ret = benchmark["stats"]["period_return_pct"]
    relative = None
    if target_ret is not None and bench_ret is not None:
        relative = round(target_ret - bench_ret, 2)

    return {
        "target_secid": secid,
        "benchmark_code": benchmark_code,
        "benchmark_secid": bench_secid,
        "target_stats": target["stats"],
        "benchmark_stats": benchmark["stats"],
        "relative_return_pct": relative,
    }
