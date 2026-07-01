"""板块分析。"""

from __future__ import annotations

from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.config import BOARD_KLINE_URL, BOARD_LIST_URL, KLT_MAP


BOARD_FS = {
    "industry": "m:90+t:2",
    "concept": "m:90+t:3",
}


def get_sector_overview(
    client: EastMoneyClient,
    *,
    sector_type: str = "industry",
    sort: str = "change_pct",
    limit: int = 30,
) -> list[dict[str, Any]]:
    sort_map = {"change_pct": "f3", "amount": "f6"}
    fs = BOARD_FS.get(sector_type, BOARD_FS["industry"])
    params = {
        "pn": "1",
        "pz": str(limit),
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fid": sort_map.get(sort, "f3"),
        "fs": fs,
        "fields": "f12,f14,f2,f3,f4,f5,f6,f8,f104,f105,f128,f136,f115",
    }
    data = client.get_json(
        BOARD_LIST_URL,
        params,
        cache_key=f"board:{sector_type}:{sort}:{limit}",
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
                "change_amount": item.get("f4"),
                "volume": item.get("f5"),
                "amount": item.get("f6"),
                "turnover_rate": item.get("f8"),
                "up_count": item.get("f104"),
                "down_count": item.get("f105"),
                "leader": item.get("f128"),
            }
        )
    return rows


def get_sector_members(
    client: EastMoneyClient,
    board_code: str,
    *,
    limit: int = 100,
    sort_by_fund_flow: bool = False,
) -> list[dict[str, Any]]:
    params = {
        "pn": "1",
        "pz": str(limit),
        "po": "1",
        "np": "1",
        "fltt": "2",
        "invt": "2",
        "fid": "f62" if sort_by_fund_flow else "f3",
        "fs": f"b:{board_code}",
        "fields": "f12,f14,f2,f3,f4,f5,f6,f8,f20,f62,f184",
    }
    data = client.get_json(
        BOARD_LIST_URL,
        params,
        cache_key=f"board_members:{board_code}:{limit}",
        cache_ttl=3600,
    )
    rows = []
    for item in (data.get("data") or {}).get("diff") or []:
        row = {
            "code": item.get("f12"),
            "name": item.get("f14"),
            "price": item.get("f2"),
            "change_pct": item.get("f3"),
            "total_market_cap": item.get("f20"),
        }
        if sort_by_fund_flow:
            row["main_net_inflow"] = item.get("f62")
            row["main_net_inflow_pct"] = item.get("f184")
        rows.append(row)
    return rows


def get_sector_kline(
    client: EastMoneyClient,
    board_code: str,
    *,
    period: str = "daily",
    limit: int = 120,
) -> list[dict[str, Any]]:
    secid = f"90.{board_code}"
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": KLT_MAP.get(period, 101),
        "fqt": "1",
        "lmt": str(limit),
        "end": "20500101",
    }
    data = client.get_json(
        BOARD_KLINE_URL,
        params,
        cache_key=f"board_kline:{board_code}:{period}:{limit}",
        cache_ttl=3600,
    )
    klines = (data.get("data") or {}).get("klines") or []
    rows: list[dict[str, Any]] = []
    for line in klines:
        parts = line.split(",")
        if len(parts) < 7:
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
            }
        )
    return rows


def search_sectors(
    client: EastMoneyClient,
    query: str,
    *,
    sector_type: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """模糊搜索板块名（行业/概念），用于「电池板块」等口语化输入。"""
    q = query.strip()
    if not q:
        return []

    types = [sector_type] if sector_type else ["concept", "industry"]
    matches: list[dict[str, Any]] = []
    seen: set[str] = set()

    for st in types:
        overview = get_sector_overview(client, sector_type=st, limit=500)
        for item in overview:
            name = item.get("name") or ""
            code = str(item.get("code") or "")
            key = f"{st}:{code}"
            if key in seen:
                continue
            if q in name or name in q:
                seen.add(key)
                score = 100 if name == q else (80 if name.startswith(q) else 60)
                matches.append({**item, "sector_type": st, "match_score": score})

    matches.sort(key=lambda x: (-x.get("match_score", 0), -(x.get("change_pct") or 0)))
    return matches[:limit]


def _resolve_board(
    client: EastMoneyClient,
    board_name: str,
    sector_type: str,
) -> dict[str, Any]:
    overview = get_sector_overview(client, sector_type=sector_type, limit=500)
    exact = next((x for x in overview if x.get("name") == board_name), None)
    if exact:
        return exact

    contains = [x for x in overview if board_name in (x.get("name") or "")]
    if not contains:
        # 跨类型再搜一次
        alt = "concept" if sector_type == "industry" else "industry"
        alt_overview = get_sector_overview(client, sector_type=alt, limit=500)
        contains = [x for x in alt_overview if board_name in (x.get("name") or "")]
        if contains:
            return contains[0]

        searched = search_sectors(client, board_name, limit=1)
        if searched:
            return searched[0]
        raise ValueError(f"未找到板块: {board_name}")

    contains.sort(key=lambda x: (len(x.get("name") or ""), -(x.get("change_pct") or 0)))
    return contains[0]


def get_sector_detail(
    client: EastMoneyClient,
    *,
    board_code: str | None = None,
    board_name: str | None = None,
    sector_type: str = "industry",
    detail_type: str = "members",
    limit: int = 50,
) -> dict[str, Any]:
    if board_code is None and board_name:
        match = _resolve_board(client, board_name, sector_type)
        board_code = str(match["code"])
        board_name = match.get("name")
        sector_type = match.get("sector_type", sector_type)

    if not board_code:
        raise ValueError("需要提供 board_code 或 board_name")

    result: dict[str, Any] = {
        "board_code": board_code,
        "board_name": board_name,
        "sector_type": sector_type,
        "detail_type": detail_type,
    }
    if detail_type == "members":
        result["members"] = get_sector_members(client, board_code, limit=limit)
    elif detail_type == "kline":
        result["kline"] = get_sector_kline(client, board_code, limit=limit)
    elif detail_type == "fund_flow":
        result["fund_flow"] = get_sector_members(
            client,
            board_code,
            limit=limit,
            sort_by_fund_flow=True,
        )
    else:
        raise ValueError(f"不支持的 detail_type: {detail_type}")
    return result
