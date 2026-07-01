"""多源新闻：东方财富搜索、7×24 快讯、新浪滚动/直播。"""

from __future__ import annotations

import json
import re
import time
from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.config import FAST_NEWS_URL, HEADERS, NEWS_LIST_URL

SINA_ROLL_URL = "https://feed.mix.sina.com.cn/api/roll/get"
SINA_ZHIBO_FEED_URL = "https://zhibo.sina.com.cn/api/zhibo/feed"

NEWS_COLUMNS = {
    "headline": "350",
    "breakfast": "1207",
}

SINA_ROLL_LIDS = {
    "finance": "2516",
    "china": "2515",
}


def _parse_jsonp(text: str) -> Any:
    start = text.find("(")
    end = text.rfind(")")
    if start < 0 or end <= start:
        raise ValueError("invalid jsonp response")
    return json.loads(text[start + 1 : end])


def _strip_html(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text)


def em_stock_news(
    client: EastMoneyClient,
    code: str,
    *,
    limit: int = 10,
    keyword: str | None = None,
) -> list[dict[str, Any]]:
    """东方财富资讯搜索（so.eastmoney.com，替代已下线 datacenter 报表）。"""
    try:
        rows = _em_stock_news_native(client, code, limit=limit, keyword=keyword)
        if rows:
            return rows
    except Exception:
        pass
    return _em_stock_news_akshare(code, limit=limit)


def _em_stock_news_native(
    client: EastMoneyClient,
    code: str,
    *,
    limit: int,
    keyword: str | None,
) -> list[dict[str, Any]]:
    q = (keyword or code).strip()
    inner_param = {
        "uid": "",
        "keyword": q,
        "type": ["cmsArticleWebOld"],
        "client": "web",
        "clientType": "web",
        "clientVersion": "curr",
        "param": {
            "cmsArticleWebOld": {
                "searchScope": "default",
                "sort": "default",
                "pageIndex": 1,
                "pageSize": min(limit, 50),
                "preTag": "",
                "postTag": "",
            }
        },
    }
    params = {
        "cb": "jQuery35101792940631092459_1764599530165",
        "param": json.dumps(inner_param, ensure_ascii=False),
        "_": str(int(time.time() * 1000)),
    }
    headers = {
        **HEADERS,
        "Referer": f"https://so.eastmoney.com/news/s?keyword={q}",
        "Host": "search-api-web.eastmoney.com",
    }
    client._throttle()
    try:
        from curl_cffi import requests as curl_requests

        resp = curl_requests.get(
            "https://search-api-web.eastmoney.com/search/jsonp",
            params=params,
            headers=headers,
            timeout=20,
            impersonate="chrome120",
        )
    except ImportError:
        resp = client._session.get(
            "https://search-api-web.eastmoney.com/search/jsonp",
            params=params,
            headers=headers,
            timeout=20,
        )
    resp.raise_for_status()
    data = _parse_jsonp(resp.text)
    items = (data.get("result") or {}).get("cmsArticleWebOld") or []
    rows: list[dict[str, Any]] = []
    for item in items[:limit]:
        code_id = item.get("code") or ""
        rows.append(
            {
                "time": item.get("date"),
                "title": _strip_html(item.get("title")),
                "summary": _strip_html(item.get("content")),
                "media": item.get("mediaName"),
                "url": f"http://finance.eastmoney.com/a/{code_id}.html" if code_id else None,
                "provider": "eastmoney_search",
            }
        )
    return rows


def _em_stock_news_akshare(code: str, *, limit: int) -> list[dict[str, Any]]:
    try:
        import akshare as ak
    except ImportError:
        return []
    df = ak.stock_news_em(symbol=code)
    rows: list[dict[str, Any]] = []
    for _, r in df.head(limit).iterrows():
        rows.append(
            {
                "time": r.get("发布时间"),
                "title": r.get("新闻标题"),
                "summary": r.get("新闻内容"),
                "media": r.get("文章来源"),
                "url": r.get("新闻链接"),
                "provider": "eastmoney_search",
            }
        )
    return rows


def em_market_flash(client: EastMoneyClient, *, limit: int = 20) -> list[dict[str, Any]]:
    params = {
        "client": "web",
        "biz": "web_724",
        "fastColumn": "102",
        "sortEnd": "",
        "pageSize": str(min(limit, 50)),
        "req_trace": str(int(time.time() * 1000)),
    }
    data = client.get_json(
        FAST_NEWS_URL,
        params,
        cache_key=f"flash_news:{limit}",
        cache_ttl=120,
    )
    items = (data.get("data") or {}).get("fastNewsList") or []
    rows: list[dict[str, Any]] = []
    for item in items:
        rows.append(
            {
                "time": item.get("showTime"),
                "title": item.get("title"),
                "summary": item.get("summary"),
                "related": item.get("stockList") or [],
                "provider": "eastmoney_flash",
            }
        )
    return rows[:limit]


def em_market_column(
    client: EastMoneyClient,
    *,
    column: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    params = {
        "client": "web",
        "biz": "web_news_col",
        "column": column,
        "order": "1",
        "needInteractData": "0",
        "page_index": "1",
        "page_size": str(min(limit, 50)),
        "req_trace": str(int(time.time() * 1000)),
        "fields": "code,showTime,title,mediaName,summary,url",
        "types": "1,20",
    }
    data = client.get_json(
        NEWS_LIST_URL,
        params,
        cache_key=f"column_news:{column}:{limit}",
        cache_ttl=600,
    )
    items = (data.get("data") or {}).get("list") or []
    rows: list[dict[str, Any]] = []
    for item in items:
        rows.append(
            {
                "time": item.get("showTime"),
                "title": item.get("title"),
                "summary": item.get("summary"),
                "url": item.get("url"),
                "media": item.get("mediaName"),
                "provider": "eastmoney_column",
            }
        )
    return rows[:limit]


def sina_market_roll(
    client: EastMoneyClient,
    *,
    category: str = "finance",
    limit: int = 20,
    keyword: str | None = None,
) -> list[dict[str, Any]]:
    """新浪滚动资讯 feed.mix.sina.com.cn。"""
    lid = SINA_ROLL_LIDS.get(category, SINA_ROLL_LIDS["finance"])
    params = {
        "pageid": "153",
        "lid": lid,
        "k": keyword or "",
        "num": str(min(limit, 50)),
        "page": "1",
    }
    data = client.get_json(
        SINA_ROLL_URL,
        params,
        cache_key=f"sina_roll:{lid}:{keyword}:{limit}",
        cache_ttl=120,
        headers={**HEADERS, "Referer": "https://finance.sina.com.cn/"},
    )
    items = (data.get("result") or {}).get("data") or []
    rows: list[dict[str, Any]] = []
    for item in items:
        ts = item.get("ctime")
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(ts))) if ts else None
        rows.append(
            {
                "time": time_str,
                "title": item.get("title"),
                "summary": item.get("intro") or item.get("summary"),
                "url": item.get("url"),
                "media": item.get("author") or "新浪财经",
                "provider": "sina_roll",
            }
        )
    return rows[:limit]


def sina_live_flash(client: EastMoneyClient, *, limit: int = 20) -> list[dict[str, Any]]:
    """新浪 7×24 直播快讯 zhibo.sina.com.cn。"""
    params = {
        "zhibo_id": "152",
        "tag_id": "0",
        "page": "1",
        "page_size": str(min(limit, 50)),
    }
    data = client.get_json(
        SINA_ZHIBO_FEED_URL,
        params,
        cache_key=f"sina_zhibo:{limit}",
        cache_ttl=120,
        headers={**HEADERS, "Referer": "https://finance.sina.com.cn/"},
    )
    items = (data.get("result") or {}).get("data", {}).get("feed", {}).get("list") or []
    rows: list[dict[str, Any]] = []
    for item in items:
        text = item.get("rich_text") or item.get("text") or ""
        title = text.split("\n", 1)[0][:120]
        rows.append(
            {
                "time": item.get("create_time") or item.get("update_time"),
                "title": title,
                "summary": text[:500],
                "url": item.get("url"),
                "media": "新浪7×24",
                "provider": "sina_zhibo",
            }
        )
    return rows[:limit]


def sina_stock_news(
    client: EastMoneyClient,
    code: str,
    *,
    name: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """新浪侧：从 7×24 + 滚动中筛出含代码/简称的条目（无稳定个股 JSON 接口时的补充）。"""
    keywords = [code]
    if name:
        keywords.append(name)
        if len(name) > 2:
            keywords.append(name[:2])

    pool: list[dict[str, Any]] = []
    pool.extend(sina_live_flash(client, limit=50))
    pool.extend(sina_market_roll(client, limit=50))

    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for item in pool:
        blob = f"{item.get('title','')} {item.get('summary','')}"
        if not any(k in blob for k in keywords):
            continue
        key = item.get("title") or ""
        if key in seen:
            continue
        seen.add(key)
        rows.append(item)
        if len(rows) >= limit:
            break
    return rows


def merge_news_rows(
    *groups: list[dict[str, Any]],
    limit: int = 20,
) -> list[dict[str, Any]]:
    """按来源交替合并，避免单一源占满配额。"""
    seen: set[str] = set()
    merged: list[dict[str, Any]] = []
    indices = [0] * len(groups)
    while len(merged) < limit:
        added = False
        for i, group in enumerate(groups):
            while indices[i] < len(group):
                item = group[indices[i]]
                indices[i] += 1
                key = (item.get("title") or "").strip()
                if not key or key in seen:
                    continue
                seen.add(key)
                merged.append(item)
                added = True
                break
        if not added:
            break
    return merged


def filter_by_keyword(rows: list[dict[str, Any]], keyword: str | None) -> list[dict[str, Any]]:
    if not keyword:
        return rows
    kw = keyword.strip()
    return [
        r
        for r in rows
        if kw in (r.get("title") or "") or kw in (r.get("summary") or "")
    ]
