"""股票代码解析与搜索。"""

from __future__ import annotations

import re
from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.config import SEARCH_URL


def _normalize_code(raw: str) -> str:
    code = raw.strip().upper()
    code = re.sub(r"^(SH|SZ|BJ)", "", code)
    return code.zfill(6) if code.isdigit() else code


def code_to_secid(code: str) -> str:
    """6 位代码 -> secid。"""
    code = _normalize_code(code)
    if code.startswith(("6", "5", "9")):
        return f"1.{code}"
    if code.startswith(("4", "8")):
        return f"0.{code}"
    return f"0.{code}"


def resolve_symbol(client: EastMoneyClient, query: str) -> dict[str, Any]:
    """名称或代码 -> secid、名称、代码。"""
    query = query.strip()
    if re.fullmatch(r"\d{6}", _normalize_code(query)):
        code = _normalize_code(query)
        return {"query": query, "code": code, "secid": code_to_secid(code), "name": None}

    params = {
        "input": query,
        "type": "14",
        "token": "D43AEA724D8AEDB8BBBBA093A0B46CC3",
        "count": "5",
    }
    data = client.get_json(SEARCH_URL, params, cache_key=f"search:{query}", cache_ttl=3600)
    items = (data.get("QuotationCodeTable") or {}).get("Data") or []
    if not items:
        raise ValueError(f"未找到匹配股票: {query}")

    hit = items[0]
    code = str(hit.get("Code", "")).zfill(6)
    market = str(hit.get("MarketType", hit.get("MktNum", "0")))
    secid = f"{market}.{code}" if "." not in str(hit.get("QuoteID", "")) else str(hit["QuoteID"])
    if secid.count(".") == 0:
        secid = code_to_secid(code)
    return {
        "query": query,
        "code": code,
        "secid": secid,
        "name": hit.get("Name"),
        "market": market,
    }


def search_stocks(client: EastMoneyClient, query: str, limit: int = 10) -> list[dict[str, Any]]:
    params = {
        "input": query,
        "type": "14",
        "token": "D43AEA724D8AEDB8BBBBA093A0B46CC3",
        "count": str(limit),
    }
    data = client.get_json(SEARCH_URL, params, cache_key=f"search:{query}:{limit}", cache_ttl=1800)
    items = (data.get("QuotationCodeTable") or {}).get("Data") or []
    results: list[dict[str, Any]] = []
    for hit in items:
        code = str(hit.get("Code", "")).zfill(6)
        results.append(
            {
                "code": code,
                "name": hit.get("Name"),
                "secid": code_to_secid(code),
                "type": hit.get("SecurityTypeName"),
            }
        )
    return results
