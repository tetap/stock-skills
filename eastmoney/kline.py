"""K 线数据。"""

from __future__ import annotations

from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.config import FQT_MAP, KLINE_URL, KLT_MAP


def get_kline(
    client: EastMoneyClient,
    secid: str,
    *,
    period: str = "daily",
    adjust: str = "qfq",
    limit: int = 120,
) -> list[dict[str, Any]]:
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65",
        "klt": KLT_MAP.get(period, 101),
        "fqt": FQT_MAP.get(adjust, 1),
        "lmt": str(limit),
        "end": "20500101",
    }
    data = client.get_json(
        KLINE_URL,
        params,
        cache_key=f"kline:{secid}:{period}:{adjust}:{limit}",
        cache_ttl=3600,
    )
    klines = (data.get("data") or {}).get("klines") or []
    rows: list[dict[str, Any]] = []
    for line in klines:
        parts = line.split(",")
        if len(parts) < 11:
            continue
        rows.append(
            {
                "date": parts[0],
                "open": float(parts[1]),
                "close": float(parts[2]),
                "high": float(parts[3]),
                "low": float(parts[4]),
                "volume": float(parts[5]),
                "amount": float(parts[6]),
                "amplitude": float(parts[7]) if parts[7] else None,
                "change_pct": float(parts[8]) if parts[8] else None,
                "change_amount": float(parts[9]) if parts[9] else None,
                "turnover_rate": float(parts[10]) if parts[10] else None,
            }
        )
    return rows


def get_kline_resilient(
    client: EastMoneyClient,
    secid: str,
    *,
    period: str = "daily",
    adjust: str = "qfq",
    limit: int = 120,
) -> list[dict[str, Any]]:
    """K 线：东财直连失败时降级 AkShare。"""
    try:
        return get_kline(client, secid, period=period, adjust=adjust, limit=limit)
    except Exception as primary_error:
        from eastmoney.fallback import available, run_fallback

        if not available():
            raise primary_error
        rows = run_fallback(
            "get_kline",
            secid=secid,
            period=period,
            adjust=adjust,
            limit=limit,
        )
        if isinstance(rows, list) and rows:
            return rows
        raise primary_error
