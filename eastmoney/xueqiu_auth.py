"""雪球 Cookie / Token 解析：环境变量 → 浏览器 → 中断引导登录。"""

from __future__ import annotations

import os
import sys
from typing import Any

XUEQIU_LOGIN_URL = "https://xueqiu.com/hq"
XUEQIU_COOKIE_NAME = "xq_a_token"
XUEQIU_TOKEN_ENV = "XUEQIU_TOKEN"
XUEQIU_COOKIE_ENV = "XUEQIUTOKEN"  # pysnowball 原生整串 Cookie


class XueqiuAuthRequired(Exception):
    """需要雪球登录凭证；Agent 应中断并引导用户打开 hq 页登录。"""

    def __init__(self, reason: str = "missing_token") -> None:
        self.reason = reason
        super().__init__(self.user_message)

    @property
    def user_message(self) -> str:
        return (
            f"请先登录雪球：{XUEQIU_LOGIN_URL}\n"
            "登录后在浏览器 Cookie 中复制 xq_a_token，"
            f"配置环境变量 {XUEQIU_TOKEN_ENV} 或 {XUEQIU_COOKIE_ENV} 后重试。"
        )

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


def _load_browser_cookies() -> dict[str, str]:
    try:
        import browser_cookie3
    except ImportError:
        return {}

    collectors: list[Any] = []
    if sys.platform == "darwin":
        collectors.extend(
            [
                lambda: browser_cookie3.chrome(domain_name="xueqiu.com"),
                lambda: browser_cookie3.safari(domain_name="xueqiu.com"),
            ]
        )
    else:
        collectors.append(lambda: browser_cookie3.chrome(domain_name="xueqiu.com"))

    for collect in collectors:
        try:
            jar = collect()
            out: dict[str, str] = {}
            for c in jar:
                domain = c.domain or ""
                if "xueqiu" in domain:
                    out[c.name] = c.value
            if out.get(XUEQIU_COOKIE_NAME):
                return out
        except Exception:
            continue
    return {}


def resolve_xueqiu_cookie(*, try_browser: bool = True) -> tuple[str | None, str | None]:
    """返回 (cookie 整串, 来源)；来源 env_xueqiu_token / env_xueqiutoken / browser。"""
    cookie, source = _load_env_cookie()
    if cookie:
        return cookie, source

    if try_browser:
        jar = _load_browser_cookies()
        token = jar.get(XUEQIU_COOKIE_NAME)
        if token:
            return build_cookie_string(token, jar.get("u")), "browser"

    return None, None


def ensure_xueqiu_cookie(*, try_browser: bool = True, reason: str = "missing_token") -> str:
    """获取有效 Cookie；失败则抛出 XueqiuAuthRequired（中断流程）。"""
    cookie, _ = resolve_xueqiu_cookie(try_browser=try_browser)
    if not cookie:
        raise XueqiuAuthRequired(reason=reason)
    sync_pysnowball_token(cookie)
    return cookie


def sync_pysnowball_token(cookie: str) -> None:
    """同步到 pysnowball 与环境变量，供后续 API 复用。"""
    os.environ[XUEQIU_COOKIE_ENV] = cookie
    try:
        import pysnowball as ball

        ball.set_token(cookie)
    except ImportError:
        pass
