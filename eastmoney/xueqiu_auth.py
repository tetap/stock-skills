"""雪球 Cookie / Token 解析：浏览器自动读取 → 本地缓存 → 环境变量兜底。"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

XUEQIU_LOGIN_URL = "https://xueqiu.com/hq"
XUEQIU_COOKIE_NAME = "xq_a_token"
XUEQIU_TOKEN_ENV = "XUEQIU_TOKEN"
XUEQIU_COOKIE_ENV = "XUEQIUTOKEN"
XUEQIU_COOKIE_CACHE_TTL = 12 * 3600  # 12h
XUEQIU_COOKIE_CACHE_FILE = Path.home() / ".cache" / "stock-skills" / "xueqiu_cookie.json"


class XueqiuAuthRequired(Exception):
    """需要雪球登录凭证；Agent 应中断并引导用户打开 hq 页登录。"""

    def __init__(self, reason: str = "missing_token", *, detail: str | None = None) -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(self.user_message)

    @property
    def user_message(self) -> str:
        base = (
            f"请先在本机浏览器登录雪球：{XUEQIU_LOGIN_URL}\n"
            "组件会自动从 Chrome / Safari / Edge 等读取 Cookie，无需手动配置环境变量。"
        )
        if self.reason == "browser_cookie3_missing":
            return base + "\n缺少依赖：pip install browser-cookie3（已写入 requirements.txt）。"
        if self.reason == "browser_locked":
            return (
                base
                + "\n未能读取浏览器 Cookie（macOS 需给终端/Cursor「完全磁盘访问权限」，或关闭浏览器后重试）。"
            )
        if self.detail:
            return base + f"\n{self.detail}"
        return base

    def to_dict(self) -> dict[str, Any]:
        from eastmoney.xueqiu import xueqiu_auth_guide

        guide = xueqiu_auth_guide(reason=self.reason)
        return {
            **guide,
            "interrupt": True,
            "user_message": self.user_message,
        }


def build_cookie_string(xq_a_token: str, u: str | None = None) -> str:
    raw = (xq_a_token or "").strip()
    if raw.startswith("xq_a_token="):
        return raw if raw.endswith(";") else f"{raw};"
    parts = [f"xq_a_token={raw}"]
    if u:
        parts.append(f"u={u}")
    return ";".join(parts) + ";"


def _jar_to_dict(jar: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    for c in jar:
        domain = (c.domain or "").lstrip(".")
        if domain == "xueqiu.com" or domain.endswith(".xueqiu.com") or "xueqiu" in domain:
            out[c.name] = c.value
    return out


def _browser_loaders() -> list[tuple[str, Any]]:
    try:
        import browser_cookie3 as bc3
    except ImportError:
        return []

    loaders: list[tuple[str, Any]] = [
        ("chrome", lambda: bc3.chrome(domain_name="xueqiu.com")),
        ("chromium", lambda: bc3.chromium(domain_name="xueqiu.com")),
        ("edge", lambda: bc3.edge(domain_name="xueqiu.com")),
        ("firefox", lambda: bc3.firefox(domain_name="xueqiu.com")),
        ("brave", lambda: bc3.brave(domain_name="xueqiu.com")),
    ]
    if sys.platform == "darwin":
        loaders.insert(0, ("safari", lambda: bc3.safari(domain_name="xueqiu.com")))
    # 部分环境 domain 过滤过严，再试全量 load
    loaders.append(("load", lambda: bc3.load(domain_name="xueqiu.com")))
    return loaders


def load_browser_cookies() -> tuple[dict[str, str], str | None]:
    """从本机浏览器 Cookie 库读取 xueqiu.com（需已登录 hq）。"""
    loaders = _browser_loaders()
    if not loaders:
        return {}, "browser_cookie3_missing"

    last_error: str | None = None
    for browser_name, loader in loaders:
        try:
            jar = loader()
            out = _jar_to_dict(jar)
            if out.get(XUEQIU_COOKIE_NAME):
                return out, browser_name
        except Exception as exc:
            msg = str(exc).lower()
            if "permission" in msg or "access" in msg or "denied" in msg:
                last_error = "browser_locked"
            continue
    return {}, last_error or "browser_not_logged_in"


def _load_env_cookie() -> tuple[str | None, str | None]:
    full = os.getenv(XUEQIU_COOKIE_ENV, "").strip()
    if full:
        return full, "env_xueqiutoken"

    token = os.getenv(XUEQIU_TOKEN_ENV, "").strip()
    if token:
        if token.startswith("xq_a_token="):
            return token if token.endswith(";") else f"{token};", "env_xueqiu_token"
        u = os.getenv("XUEQIU_U", "").strip() or None
        return build_cookie_string(token, u), "env_xueqiu_token"

    return None, None


def _save_cookie_cache(cookie: str, source: str) -> None:
    try:
        XUEQIU_COOKIE_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        XUEQIU_COOKIE_CACHE_FILE.write_text(
            json.dumps(
                {"cookie": cookie, "source": source, "saved_at": time.time()},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    except OSError:
        pass


def _load_cookie_cache() -> tuple[str | None, str | None]:
    try:
        if not XUEQIU_COOKIE_CACHE_FILE.is_file():
            return None, None
        data = json.loads(XUEQIU_COOKIE_CACHE_FILE.read_text(encoding="utf-8"))
        cookie = (data.get("cookie") or "").strip()
        saved_at = float(data.get("saved_at") or 0)
        if not cookie or time.time() - saved_at > XUEQIU_COOKIE_CACHE_TTL:
            return None, None
        return cookie, f"cache:{data.get('source', 'unknown')}"
    except (OSError, ValueError, TypeError):
        return None, None


def resolve_xueqiu_cookie(*, try_browser: bool = True) -> tuple[str | None, str | None]:
    """返回 (cookie 整串, 来源)。优先浏览器自动读取，环境变量可选手动覆盖。"""
    browser_or_err: str | None = None

    # 1. 浏览器（默认路径，用户无需配 env）
    if try_browser:
        jar, browser_or_err = load_browser_cookies()
        token = jar.get(XUEQIU_COOKIE_NAME)
        if token:
            cookie = build_cookie_string(token, jar.get("u"))
            _save_cookie_cache(cookie, browser_or_err or "browser")
            sync_pysnowball_token(cookie)
            return cookie, f"browser:{browser_or_err}"

    # 2. 本地缓存（浏览器暂时读不到时用）
    cached, cache_source = _load_cookie_cache()
    if cached:
        sync_pysnowball_token(cached)
        return cached, cache_source

    # 3. 环境变量（CI / 无浏览器场景兜底）
    cookie, source = _load_env_cookie()
    if cookie:
        sync_pysnowball_token(cookie)
        return cookie, source

    return None, browser_or_err if try_browser else None


def ensure_xueqiu_cookie(*, try_browser: bool = True, reason: str = "missing_token") -> str:
    cookie, source = resolve_xueqiu_cookie(try_browser=try_browser)
    if cookie:
        return cookie

    _, browser_err = load_browser_cookies() if try_browser else (None, None)
    fail_reason = reason
    if browser_err == "browser_cookie3_missing":
        fail_reason = "browser_cookie3_missing"
    elif browser_err == "browser_locked":
        fail_reason = "browser_locked"
    elif browser_err == "browser_not_logged_in":
        fail_reason = "missing_token"

    raise XueqiuAuthRequired(reason=fail_reason)


def sync_pysnowball_token(cookie: str) -> None:
    os.environ[XUEQIU_COOKIE_ENV] = cookie
    try:
        import pysnowball as ball

        ball.set_token(cookie)
    except ImportError:
        pass


def xueqiu_cookie_diagnostics(*, try_browser: bool = True) -> dict[str, Any]:
    """诊断：浏览器读取、缓存、环境变量各自状态。"""
    has_bc3 = True
    try:
        import browser_cookie3  # noqa: F401
    except ImportError:
        has_bc3 = False

    jar, browser_status = load_browser_cookies() if try_browser and has_bc3 else ({}, None)
    cached, cache_src = _load_cookie_cache()
    env_cookie, env_src = _load_env_cookie()
    resolved, resolved_src = resolve_xueqiu_cookie(try_browser=try_browser)

    return {
        "authenticated": bool(resolved),
        "cookie_source": resolved_src,
        "browser_cookie3_installed": has_bc3,
        "browser_read": {
            "ok": bool(jar.get(XUEQIU_COOKIE_NAME)),
            "browser": browser_status,
            "has_u": bool(jar.get("u")),
        },
        "cache": {
            "path": str(XUEQIU_COOKIE_CACHE_FILE),
            "available": bool(cached),
            "source": cache_src,
        },
        "env_override": {
            "available": bool(env_cookie),
            "source": env_src,
        },
        "login_url": XUEQIU_LOGIN_URL,
        "hint": "在 Chrome/Safari 打开 hq 页登录即可；一般无需配置 XUEQIU_TOKEN。",
    }
