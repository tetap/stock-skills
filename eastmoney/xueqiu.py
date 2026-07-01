"""雪球：讨论热度、热度榜（公开 screener API）。"""

from __future__ import annotations

import os
import time
from typing import Any

from eastmoney.client import EastMoneyClient
from eastmoney.config import HEADERS

XUEQIU_SCREENER_URL = "https://xueqiu.com/service/v5/stock/screener/screen"
XUEQIU_HOME_URL = "https://xueqiu.com"
XUEQIU_COOKIE_NAME = "xq_a_token"
XUEQIU_TOKEN_ENV = "XUEQIU_TOKEN"

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
    """从环境变量读取 xq_a_token（值即浏览器 Cookie 中的 xq_a_token）。"""
    return os.getenv(XUEQIU_TOKEN_ENV, "").strip()


def xueqiu_auth_guide(*, reason: str = "missing_token") -> dict[str, Any]:
    """雪球帖子接口授权说明；Agent 可在 token 缺失/失效时展示并等待用户配置后继续。"""
    reason_text = {
        "missing_token": "未检测到 XUEQIU_TOKEN（浏览器 Cookie 中的 xq_a_token）。",
        "auth_failed": "已配置 XUEQIU_TOKEN，但雪球返回未授权或凭证失效。",
        "blocked": "雪球接口被 WAF 拦截，通常登录并更新 Cookie 后可恢复。",
    }.get(reason, "雪球帖子接口需要有效登录凭证。")

    return {
        "auth_required": True,
        "reason": reason,
        "cookie_name": XUEQIU_COOKIE_NAME,
        "env_var": XUEQIU_TOKEN_ENV,
        "login_url": XUEQIU_HOME_URL,
        "message": reason_text,
        "steps": [
            f"在浏览器打开 {XUEQIU_HOME_URL}，使用手机号/微信等方式登录雪球（未完成登录请先授权）。",
            "登录后按 F12 → Application（应用）→ Cookies → xueqiu.com，找到并复制 xq_a_token 的值。",
            f"在本机终端执行：export {XUEQIU_TOKEN_ENV}='粘贴的token'（或写入 ~/.zshrc / ~/.bashrc 持久化）。",
            "若使用 MCP：在 ~/.cursor/mcp.json 的 eastmoney-stock 环境变量中加入 XUEQIU_TOKEN，并重启 Cursor。",
            "配置完成后回复「已配置雪球 token」，再重试 get_news_and_reports --source xueqiu 或 --source all。",
        ],
        "note": "讨论热榜/个股讨论热度无需 token；仅个股帖子正文需要 xq_a_token。",
    }


def xueqiu_auth_hint_row(*, reason: str = "missing_token") -> dict[str, Any]:
    """格式化为资讯条目，便于与新闻合并返回。"""
    guide = xueqiu_auth_guide(reason=reason)
    steps = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(guide["steps"]))
    return {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "title": "雪球帖子需登录：请从浏览器 Cookie 获取 xq_a_token",
        "summary": f"{guide['message']}\n{steps}",
        "provider": "xueqiu_auth_hint",
        "url": guide["login_url"],
        "auth_required": True,
        "reason": reason,
    }


def _xq_headers(referer: str = "https://xueqiu.com/hq") -> dict[str, str]:
    token = get_xueqiu_token()
    headers = {
        **HEADERS,
        "Referer": referer,
        "X-Requested-With": "XMLHttpRequest",
    }
    if token:
        headers["Cookie"] = f"xq_a_token={token};"
    return headers


def xueqiu_hot_stocks(
    client: EastMoneyClient,
    *,
    rank_by: str = "tweet",
    period: str = "hot",
    limit: int = 30,
    page: int = 1,
) -> list[dict[str, Any]]:
    """雪球热度榜：讨论/关注/交易活跃。"""
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
    """将雪球热度榜格式化为资讯条目（用于市场情绪/热点）。"""
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
    """查询个股在雪球讨论榜中的热度（分页扫描 screener）。"""
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
) -> list[dict[str, Any]]:
    """个股雪球情绪：热度摘要 + 可选帖子（需环境变量 XUEQIU_TOKEN）。"""
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

    posts, auth_reason = xueqiu_stock_posts(client, code, limit=max(0, limit - len(rows)))
    rows.extend(posts)
    if include_auth_hint and auth_reason and len(rows) < limit:
        rows.append(xueqiu_auth_hint_row(reason=auth_reason))
    return rows[:limit]


def xueqiu_stock_posts(
    client: EastMoneyClient,
    code: str,
    *,
    limit: int = 5,
) -> tuple[list[dict[str, Any]], str | None]:
    """个股雪球帖子。返回 (帖子列表, 授权失败原因)；原因见 xueqiu_auth_guide。"""
    token = get_xueqiu_token()
    if not token:
        return [], "missing_token"

    symbol = code_to_xq_symbol(code)
    params = {
        "symbol": symbol,
        "count": str(min(limit, 20)),
        "source": "all",
    }
    url = "https://xueqiu.com/statuses/stock_timeline.json"
    try:
        client._throttle()
        resp = client._session.get(
            url,
            params=params,
            headers=_xq_headers(referer=f"https://xueqiu.com/S/{symbol}"),
            timeout=15,
        )
        if resp.status_code != 200 or resp.text.lstrip().startswith("<"):
            reason = "blocked" if resp.text.lstrip().startswith("<") else "auth_failed"
            return [], reason
        data = resp.json()
    except Exception:
        return [], "auth_failed"

    if data.get("error_code") in {400016, 400001, 401} or data.get("error_description"):
        return [], "auth_failed"

    items = data.get("list") or []
    rows: list[dict[str, Any]] = []
    for item in items[:limit]:
        text = (item.get("text") or item.get("description") or "").strip()
        if not text:
            continue
        created = item.get("created_at")
        time_str = (
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(created / 1000))
            if created
            else None
        )
        rows.append(
            {
                "time": time_str,
                "title": text[:80] + ("…" if len(text) > 80 else ""),
                "summary": text[:500],
                "provider": "xueqiu_post",
                "url": f"https://xueqiu.com/{item.get('target') or item.get('id', '')}",
            }
        )
    return rows, None if rows else None


def _symbol_to_code(symbol: str | None) -> str | None:
    if not symbol or len(symbol) < 3:
        return None
    return symbol[2:]
