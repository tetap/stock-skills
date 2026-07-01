"""实时行情。"""

from __future__ import annotations

from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.config import QUOTE_FIELDS, QUOTE_LIST_URL, QUOTE_URL, UT_TOKEN


def _parse_quote_item(item: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {}
    for src, dst in QUOTE_FIELDS.items():
        val = item.get(src)
        if val is not None and val != "-":
            if dst in {"price", "change_pct", "change_amount", "open", "high", "low", "prev_close"}:
                try:
                    val = float(val)
                except (TypeError, ValueError):
                    pass
            elif dst in {"volume", "amount", "turnover_rate", "pe_ttm", "pb"}:
                try:
                    val = float(val)
                except (TypeError, ValueError):
                    pass
            row[dst] = val
    return row


def get_realtime_quote(client: EastMoneyClient, secid: str) -> dict[str, Any]:
    params = {
        "secid": secid,
        "fields": ",".join(QUOTE_FIELDS.keys()),
        "fltt": "2",
        "invt": "2",
        "ut": UT_TOKEN,
    }
    data = client.get_json(
        QUOTE_URL,
        params,
        cache_key=f"quote:{secid}",
        cache_ttl=30,
    )
    item = (data.get("data") or {})
    if not item:
        raise ValueError(f"无行情数据: {secid}")
    return {"secid": secid, **_parse_quote_item(item)}


def get_market_snapshot(
    client: EastMoneyClient,
    *,
    sort: str = "change_pct",
    limit: int = 20,
) -> list[dict[str, Any]]:
    """A 股涨幅榜快照。"""
    sort_map = {
        "change_pct": "f3",
        "turnover": "f6",
        "volume": "f5",
    }
    params = {
        "pn": "1",
        "pz": str(limit),
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fid": sort_map.get(sort, "f3"),
        "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
        "fields": "f12,f14,f2,f3,f4,f5,f6,f7,f8,f9,f10,f20,f21",
        "ut": UT_TOKEN,
    }
    data = client.get_json(
        QUOTE_LIST_URL,
        params,
        cache_key=f"snapshot:{sort}:{limit}",
        cache_ttl=30,
    )
    rows = []
    for item in (data.get("data") or {}).get("diff") or []:
        rows.append(
            {
                "code": item.get("f12"),
                "name": item.get("f14"),
                "price": item.get("f2"),
                "change_pct": item.get("f3"),
                "change_amount": item.get("f4"),
                "volume": item.get("f5"),
                "amount": item.get("f6"),
                "turnover_rate": item.get("f8"),
                "pe": item.get("f9"),
                "total_market_cap": item.get("f20"),
            }
        )
    return rows
