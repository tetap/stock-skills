"""雪球：讨论热度、帖子、研报等（热榜无需登录；帖子/研报需 Cookie）。"""

from __future__ import annotations

import time
from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.config import HEADERS
from eastmoney.xueqiu_auth import (
    XUEQIU_LOGIN_URL,
    XUEQIU_COOKIE_NAME,
    XUEQIU_TOKEN_ENV,
    XueqiuAuthRequired,
    ensure_xueqiu_cookie,
    resolve_xueqiu_cookie,
    xueqiu_cookie_diagnostics,
)

XUEQIU_SCREENER_URL = "https://xueqiu.com/service/v5/stock/screener/screen"
XUEQIU_LIVENEWS_URL = "https://xueqiu.com/statuses/livenews/list.json"
# category=6：雪球热门资讯（hq 页「热门」流）
XUEQIU_LIVENEWS_HOT_CATEGORY = 6

RANK_FIELDS = {
    "tweet": {"hot": "tweet", "week": "tweet7d"},
    "follow": {"hot": "follow", "week": "follow7d"},
    "deal": {"hot": "deal", "week": "deal7d"},
}


def code_to_xq_symbol(code: str) -> str:
    code = code.zfill(6)
    if code.startswith(("6", "5", "9")):
        return f"SH{code}"
    return f"SZ{code}"


def get_xueqiu_token() -> str:
    """兼容旧接口：返回 xq_a_token 值（非整串 Cookie）。"""
    cookie, _ = resolve_xueqiu_cookie(try_browser=False)
    if not cookie:
        return ""
    for part in cookie.split(";"):
        part = part.strip()
        if part.startswith("xq_a_token="):
            return part.split("=", 1)[1]
    return ""


def xueqiu_auth_guide(*, reason: str = "missing_token") -> dict[str, Any]:
    """雪球授权说明；token 缺失/失效时展示并等待用户配置。"""
    reason_text = {
        "missing_token": f"未检测到雪球 Cookie（{XUEQIU_COOKIE_NAME}）。",
        "auth_failed": f"已配置 {XUEQIU_TOKEN_ENV}，但雪球返回未授权或凭证失效。",
        "blocked": "雪球接口被 WAF 拦截，通常登录并更新 Cookie 后可恢复。",
    }.get(reason, "雪球接口需要有效登录凭证。")

    return {
        "auth_required": True,
        "interrupt": True,
        "reason": reason,
        "cookie_name": XUEQIU_COOKIE_NAME,
        "env_var": XUEQIU_TOKEN_ENV,
        "env_var_full_cookie": "XUEQIUTOKEN",
        "login_url": XUEQIU_LOGIN_URL,
        "message": reason_text,
        "user_message": (
            f"请先在本机浏览器登录雪球：{XUEQIU_LOGIN_URL}\n"
            "登录后组件会自动从 Chrome/Safari 读取 Cookie，一般无需手动配置环境变量。"
        ),
        "steps": [
            f"在 Chrome 或 Safari 打开 {XUEQIU_LOGIN_URL} 并完成登录。",
            "保持浏览器登录状态，直接重试 get_market_news / get_xueqiu_data（会自动读 Cookie）。",
            "若仍失败：macOS 给 Cursor/终端「完全磁盘访问权限」，或 pip install browser-cookie3。",
            "可选兜底：export XUEQIU_TOKEN='xq_a_token值'（仅 CI 或无浏览器环境需要）。",
            "诊断：python scripts/em.py get_xueqiu_auth_status",
        ],
        "note": "热榜无需登录；热门资讯/帖子/研报会自动读浏览器 Cookie。",
    }


def xueqiu_auth_hint_row(*, reason: str = "missing_token") -> dict[str, Any]:
    guide = xueqiu_auth_guide(reason=reason)
    return {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "title": f"请先登录雪球：{XUEQIU_LOGIN_URL}",
        "summary": guide["user_message"],
        "provider": "xueqiu_auth_hint",
        "url": guide["login_url"],
        "auth_required": True,
        "interrupt": True,
        "reason": reason,
    }


def xueqiu_auth_status(*, try_browser: bool = True) -> dict[str, Any]:
    return xueqiu_cookie_diagnostics(try_browser=try_browser)


def _pysnowball_available() -> bool:
    try:
        import pysnowball  # noqa: F401

        return True
    except ImportError:
        return False


def _xq_headers(referer: str = XUEQIU_LOGIN_URL) -> dict[str, str]:
    cookie, _ = resolve_xueqiu_cookie(try_browser=True)
    headers = {
        **HEADERS,
        "Referer": referer,
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    }
    if cookie:
        headers["Cookie"] = cookie
    return headers


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


def _parse_xueqiu_error(data: dict[str, Any]) -> bool:
    code = data.get("error_code")
    if code in {400016, 400001, 401, "400016", "400001"}:
        return True
    return bool(data.get("error_description"))


def _xq_session_get_json(
    client: EastMoneyClient,
    url: str,
    params: dict[str, Any],
    *,
    referer: str = XUEQIU_LOGIN_URL,
    require_auth: bool = False,
    cache_key: str | None = None,
    cache_ttl: float = 120,
) -> tuple[dict[str, Any] | None, str | None]:
    """雪球 xueqiu.com 域 JSON（livenews / 帖子等，需 Cookie）。"""
    cookie, _source = resolve_xueqiu_cookie(try_browser=True)
    if not cookie:
        if require_auth:
            raise XueqiuAuthRequired(reason="missing_token")
        return None, "missing_token"

    if cache_key:
        cached = client._cache.get(cache_key)
        if cached is not None:
            return cached, None

    try:
        client._throttle()
        resp = client._session.get(
            url,
            params=params,
            headers=_xq_headers(referer=referer),
            timeout=15,
        )
        if resp.status_code != 200 or resp.text.lstrip().startswith("<"):
            reason = "blocked" if resp.text.lstrip().startswith("<") else "auth_failed"
            if require_auth:
                raise XueqiuAuthRequired(reason=reason)
            return None, reason
        data = resp.json()
    except XueqiuAuthRequired:
        raise
    except Exception:
        if require_auth:
            raise XueqiuAuthRequired(reason="auth_failed")
        return None, "auth_failed"

    if not isinstance(data, dict):
        return None, "auth_failed"
    if _parse_xueqiu_error(data):
        if require_auth:
            raise XueqiuAuthRequired(reason="auth_failed")
        return None, "auth_failed"

    if cache_key and cache_ttl > 0:
        client._cache.set(cache_key, data, cache_ttl)
    return data, None


def _livenews_items(data: dict[str, Any]) -> list[dict[str, Any]]:
    items = data.get("items")
    if isinstance(items, list):
        return items
    nested = data.get("data")
    if isinstance(nested, dict) and isinstance(nested.get("items"), list):
        return nested["items"]
    if isinstance(data.get("list"), list):
        return data["list"]
    return []


def _livenews_item_url(item: dict[str, Any]) -> str:
    target = item.get("target") or item.get("url")
    if target:
        s = str(target)
        if s.startswith("http"):
            return s
        return f"https://xueqiu.com{s if s.startswith('/') else '/' + s}"
    item_id = item.get("id")
    if item_id:
        return f"https://xueqiu.com/{item_id}"
    return XUEQIU_LOGIN_URL


def xueqiu_livenews(
    client: EastMoneyClient,
    *,
    category: int = XUEQIU_LIVENEWS_HOT_CATEGORY,
    since_id: int = -1,
    limit: int = 15,
    require_auth: bool = False,
) -> tuple[list[dict[str, Any]], str | None]:
    """雪球热门资讯（livenews/list.json，category=6 为 hq 热门流）。"""
    params = {
        "category": str(category),
        "since_id": str(since_id),
        "count": str(min(limit, 50)),
    }
    cache_key = f"xq_livenews:{category}:{since_id}:{limit}"
    data, reason = _xq_session_get_json(
        client,
        XUEQIU_LIVENEWS_URL,
        params,
        referer=XUEQIU_LOGIN_URL,
        require_auth=require_auth,
        cache_key=cache_key,
        cache_ttl=120,
    )
    if not data:
        return [], reason

    rows: list[dict[str, Any]] = []
    for item in _livenews_items(data)[:limit]:
        if not isinstance(item, dict):
            continue
        text = (item.get("text") or item.get("title") or item.get("description") or "").strip()
        if not text:
            continue
        rows.append(
            {
                "id": item.get("id"),
                "time": _ts_ms_to_str(item.get("created_at") or item.get("timeBefore")),
                "title": text[:80] + ("…" if len(text) > 80 else ""),
                "summary": text[:500],
                "provider": "xueqiu_livenews",
                "url": _livenews_item_url(item),
                "category": category,
            }
        )
    if not rows and require_auth:
        raise XueqiuAuthRequired(reason="auth_failed")
    return rows, None if rows else reason


def xueqiu_livenews_as_news(
    client: EastMoneyClient,
    *,
    category: int = XUEQIU_LIVENEWS_HOT_CATEGORY,
    limit: int = 15,
    require_auth: bool = False,
) -> list[dict[str, Any]]:
    """格式化热门资讯为 merge_news_rows 兼容条目。"""
    rows, reason = xueqiu_livenews(
        client,
        category=category,
        limit=limit,
        require_auth=require_auth,
    )
    if rows:
        return rows
    if require_auth and reason:
        raise XueqiuAuthRequired(reason=reason or "missing_token")
    if reason:
        return [xueqiu_auth_hint_row(reason=reason)]
    return []


def xueqiu_hot_stocks(
    client: EastMoneyClient,
    *,
    rank_by: str = "tweet",
    period: str = "hot",
    limit: int = 30,
    page: int = 1,
) -> list[dict[str, Any]]:
    """雪球热度榜（公开 screener，无需登录）。"""
    order_by = RANK_FIELDS.get(rank_by, RANK_FIELDS["tweet"]).get(period, "tweet")
    params = {
        "category": "CN",
        "size": str(min(limit, 200)),
        "order": "desc",
        "order_by": order_by,
        "only_count": "0",
        "page": str(page),
    }
    data = client.get_json(
        XUEQIU_SCREENER_URL,
        params,
        cache_key=f"xq_hot:{rank_by}:{period}:{page}:{limit}",
        cache_ttl=300,
        headers=_xq_headers(),
    )
    rows: list[dict[str, Any]] = []
    for item in (data.get("data") or {}).get("list") or []:
        metric = item.get(order_by) or item.get(rank_by)
        rows.append(
            {
                "symbol": item.get("symbol"),
                "code": _symbol_to_code(item.get("symbol")),
                "name": item.get("name"),
                "price": item.get("current"),
                "change_pct": item.get("pct"),
                "metric": metric,
                "metric_type": rank_by,
                "period": period,
                "provider": "xueqiu_hot",
            }
        )
    return rows[:limit]


def xueqiu_hot_as_news(
    client: EastMoneyClient,
    *,
    rank_by: str = "tweet",
    period: str = "hot",
    limit: int = 15,
) -> list[dict[str, Any]]:
    hot = xueqiu_hot_stocks(client, rank_by=rank_by, period=period, limit=limit)
    label = {"tweet": "讨论", "follow": "关注", "deal": "交易"}.get(rank_by, rank_by)
    rows: list[dict[str, Any]] = []
    for i, item in enumerate(hot, start=1):
        rows.append(
            {
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "title": f"雪球{label}热榜 #{i} {item.get('name')} ({item.get('code')})",
                "summary": (
                    f"{label}量 {item.get('metric')}，现价 {item.get('price')}，"
                    f"涨跌幅 {item.get('change_pct')}%"
                ),
                "provider": "xueqiu_hot",
                "url": f"https://xueqiu.com/S/{item.get('symbol')}",
            }
        )
    return rows


def xueqiu_stock_heat(
    client: EastMoneyClient,
    code: str,
    *,
    max_pages: int = 5,
) -> dict[str, Any] | None:
    symbol = code_to_xq_symbol(code)
    for page in range(1, max_pages + 1):
        batch = xueqiu_hot_stocks(
            client,
            rank_by="tweet",
            period="hot",
            limit=200,
            page=page,
        )
        for rank, item in enumerate(batch, start=1 + (page - 1) * 200):
            if item.get("symbol") == symbol:
                return {
                    **item,
                    "tweet_rank": rank,
                    "tweet": item.get("metric"),
                }
    return None


def xueqiu_stock_sentiment(
    client: EastMoneyClient,
    code: str,
    *,
    name: str | None = None,
    limit: int = 5,
    include_auth_hint: bool = True,
    require_auth: bool = False,
    include_reports: bool = True,
) -> list[dict[str, Any]]:
    """个股雪球情绪：热度 + 帖子 + pysnowball 研报（后两者需 Cookie）。"""
    rows: list[dict[str, Any]] = []
    heat = xueqiu_stock_heat(client, code)
    if heat:
        stock_name = name or heat.get("name") or code
        rows.append(
            {
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "title": f"雪球讨论热度：{stock_name} 讨论量 {heat.get('tweet')}",
                "summary": (
                    f"讨论榜约第 {heat.get('tweet_rank')} 位，讨论 {heat.get('tweet')} 次，"
                    f"现价 {heat.get('price')}，涨跌 {heat.get('change_pct')}%"
                ),
                "provider": "xueqiu_heat",
                "url": f"https://xueqiu.com/S/{heat.get('symbol')}",
            }
        )

    if include_reports and _pysnowball_available():
        try:
            from eastmoney.xueqiu_pysnowball import fetch_xueqiu_data

            rep = fetch_xueqiu_data(
                code,
                "report",
                limit=max(1, limit // 2),
            )
            rows.extend(rep.get("rows") or [])
        except XueqiuAuthRequired:
            if require_auth:
                raise
        except Exception:
            pass

    posts, auth_reason = xueqiu_stock_posts(
        client,
        code,
        limit=max(0, limit - len(rows)),
        require_auth=require_auth,
    )
    rows.extend(posts)

    if include_auth_hint and auth_reason and len(rows) < limit:
        rows.append(xueqiu_auth_hint_row(reason=auth_reason))
    return rows[:limit]


def xueqiu_stock_posts(
    client: EastMoneyClient,
    code: str,
    *,
    limit: int = 5,
    require_auth: bool = False,
) -> tuple[list[dict[str, Any]], str | None]:
    """个股帖子 timeline。require_auth=True 且无 Cookie 时抛出 XueqiuAuthRequired。"""
    symbol = code_to_xq_symbol(code)
    params = {
        "symbol": symbol,
        "count": str(min(limit, 20)),
        "source": "all",
    }
    data, reason = _xq_session_get_json(
        client,
        "https://xueqiu.com/statuses/stock_timeline.json",
        params,
        referer=f"https://xueqiu.com/S/{symbol}",
        require_auth=require_auth,
    )
    if not data:
        return [], reason

    items = data.get("list") or []
    rows: list[dict[str, Any]] = []
    for item in items[:limit]:
        text = (item.get("text") or item.get("description") or "").strip()
        if not text:
            continue
        rows.append(
            {
                "time": _ts_ms_to_str(item.get("created_at")),
                "title": text[:80] + ("…" if len(text) > 80 else ""),
                "summary": text[:500],
                "provider": "xueqiu_post",
                "url": _livenews_item_url(item),
            }
        )
    if not rows and require_auth:
        raise XueqiuAuthRequired(reason="auth_failed")
    return rows, None if rows else reason


def _symbol_to_code(symbol: str | None) -> str | None:
    if not symbol or len(symbol) < 3:
        return None
    return symbol[2:]
