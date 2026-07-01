"""雪球 HTTP：curl_cffi 浏览器指纹 + 可选 Chrome CDP 复用已登录会话。"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import urlencode

XUEQIU_CDP_ENV = "XUEQIU_CDP_URL"
DEFAULT_CDP_URL = "http://127.0.0.1:9222"
IMPERSONATE = "chrome131"


def _is_waf_html(text: str) -> bool:
    head = (text or "").lstrip()
    return head.startswith("<") and ("_waf_" in head or "滑动验证" in head or "aliyun_waf" in head)


def _curl_session(cookie: str | None):
    from curl_cffi import requests as curl_requests

    session = curl_requests.Session(impersonate=IMPERSONATE)
    if cookie:
        for part in cookie.split(";"):
            part = part.strip()
            if not part or "=" not in part:
                continue
            name, value = part.split("=", 1)
            session.cookies.set(name.strip(), value.strip(), domain=".xueqiu.com")
    return session


def xueqiu_http_get(
    url: str,
    params: dict[str, Any] | None,
    *,
    headers: dict[str, str],
    cookie: str | None,
    timeout: float = 20,
) -> tuple[int, str]:
    """curl_cffi GET；返回 (status_code, text)。"""
    session = _curl_session(cookie)
    resp = session.get(url, params=params or {}, headers=headers, timeout=timeout)
    return int(resp.status_code), resp.text


def xueqiu_http_get_json_via_cdp(
    url: str,
    params: dict[str, Any] | None,
    *,
    referer: str,
    cdp_url: str | None = None,
    timeout_ms: int = 20000,
) -> dict[str, Any] | None:
    """通过 Chrome DevTools 在真实浏览器上下文 fetch（需 --remote-debugging-port）。"""
    endpoint = cdp_url or os.getenv(XUEQIU_CDP_ENV, DEFAULT_CDP_URL).strip()
    if not endpoint:
        return None

    qs = urlencode(params or {}, doseq=True)
    full_url = f"{url}?{qs}" if qs else url

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(endpoint, timeout=timeout_ms)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()
            if referer and "xueqiu.com/S/" in referer and page.url != referer:
                try:
                    page.goto(referer, wait_until="domcontentloaded", timeout=timeout_ms)
                    page.wait_for_timeout(1500)
                except Exception:
                    pass
            payload = page.evaluate(
                """async ({ url, referer }) => {
                    const r = await fetch(url, {
                        credentials: 'include',
                        headers: { 'Accept': 'application/json, text/plain, */*' },
                    });
                    const text = await r.text();
                    return { status: r.status, text };
                }""",
                {"url": full_url, "referer": referer},
            )
    except Exception:
        return None

    if not payload or _is_waf_html(payload.get("text") or ""):
        return None
    try:
        data = json.loads(payload["text"])
    except (TypeError, ValueError, KeyError):
        return None
    return data if isinstance(data, dict) else None


def probe_stock_status_api(
    *,
    symbol: str = "SH600519",
    cookie: str | None,
) -> dict[str, Any]:
    """诊断：Cookie 可读但 API 是否可用。"""
    url = "https://xueqiu.com/query/v1/symbol/search/status"
    referer = f"https://xueqiu.com/S/{symbol}"
    params = {
        "count": "3",
        "comment": "0",
        "symbol": symbol,
        "hl": "0",
        "source": "all",
        "sort": "time",
        "page": "1",
        "q_type": "",
        "type": "11,12",
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Referer": referer,
        "Origin": "https://xueqiu.com",
        "X-Requested-With": "XMLHttpRequest",
    }
    if cookie:
        headers["Cookie"] = cookie
    status, text = xueqiu_http_get(
        url,
        params,
        headers=headers,
        cookie=cookie,
    )
    curl_ok = not _is_waf_html(text)
    posts = 0
    if curl_ok:
        try:
            posts = len(json.loads(text).get("list") or [])
        except (TypeError, ValueError):
            curl_ok = False

    cdp_data = None
    if not curl_ok:
        cdp_data = xueqiu_http_get_json_via_cdp(
            url,
            params,
            referer=referer,
        )
    cdp_ok = bool(cdp_data and (cdp_data.get("list") or []))

    note = (
        "Cookie 已读取，但 curl 请求被 WAF 拦截（需浏览器动态签名 md5__1038）。"
        if cookie and not curl_ok
        else "未检测到 Cookie。"
        if not cookie
        else "curl 直连 API 正常。"
    )
    if not curl_ok and not cdp_ok:
        note += (
            " 可选：Chrome 加启动参数 --remote-debugging-port=9222 后设置 "
            f"export {XUEQIU_CDP_ENV}=http://127.0.0.1:9222，或在 Network 复制 Cookie 到 XUEQIUTOKEN。"
        )
    elif cdp_ok:
        note = "curl 被 WAF 拦截，但 Chrome CDP 复用会话成功。"

    return {
        "symbol": symbol,
        "curl_ok": curl_ok,
        "curl_posts": posts,
        "cdp_ok": cdp_ok,
        "cdp_posts": len((cdp_data or {}).get("list") or []) if cdp_ok else 0,
        "note": note,
    }
