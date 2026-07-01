"""资金面。"""

from __future__ import annotations

from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.config import DATACENTER_URL, FUND_FLOW_URL, MARKET_FUND_FLOW_URL, QUOTE_LIST_URL


def get_stock_fund_flow(
    client: EastMoneyClient,
    secid: str,
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    params = {
        "lmt": str(limit),
        "klt": "101",
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63",
    }
    data = client.get_json(
        FUND_FLOW_URL,
        params,
        cache_key=f"fflow:{secid}:{limit}",
        cache_ttl=3600,
    )
    klines = (data.get("data") or {}).get("klines") or []
    rows: list[dict[str, Any]] = []
    for line in klines:
        parts = line.split(",")
        if len(parts) < 6:
            continue
        rows.append(
            {
                "date": parts[0],
                "main_net_inflow": float(parts[1]) if parts[1] else 0,
                "small_net_inflow": float(parts[2]) if parts[2] else 0,
                "medium_net_inflow": float(parts[3]) if parts[3] else 0,
                "large_net_inflow": float(parts[4]) if parts[4] else 0,
                "super_large_net_inflow": float(parts[5]) if parts[5] else 0,
            }
        )
    return rows


def get_fund_flow_rank(
    client: EastMoneyClient,
    *,
    limit: int = 20,
) -> list[dict[str, Any]]:
    params = {
        "pn": "1",
        "pz": str(limit),
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fid": "f62",
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205",
    }
    data = client.get_json(
        QUOTE_LIST_URL,
        params,
        cache_key=f"ffrank:{limit}",
        cache_ttl=300,
    )
    rows = []
    for item in (data.get("data") or {}).get("diff") or []:
        rows.append(
            {
                "code": item.get("f12"),
                "name": item.get("f14"),
                "price": item.get("f2"),
                "change_pct": item.get("f3"),
                "main_net_inflow": item.get("f62"),
                "main_net_inflow_pct": item.get("f184"),
            }
        )
    return rows


def get_market_fund_flow(client: EastMoneyClient, *, limit: int = 20) -> list[dict[str, Any]]:
    params = {
        "lmt": str(limit),
        "klt": "101",
        "secid": "1.000001",
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63",
    }
    data = client.get_json(
        MARKET_FUND_FLOW_URL,
        params,
        cache_key=f"mfflow:{limit}",
        cache_ttl=3600,
    )
    klines = (data.get("data") or {}).get("klines") or []
    rows: list[dict[str, Any]] = []
    for line in klines:
        parts = line.split(",")
        if len(parts) < 6:
            continue
        rows.append(
            {
                "date": parts[0],
                "main_net_inflow": float(parts[1]) if parts[1] else 0,
                "small_net_inflow": float(parts[2]) if parts[2] else 0,
                "medium_net_inflow": float(parts[3]) if parts[3] else 0,
                "large_net_inflow": float(parts[4]) if parts[4] else 0,
                "super_large_net_inflow": float(parts[5]) if parts[5] else 0,
            }
        )
    return rows
