"""HTTP 客户端：限流 + 缓存 + 重试。"""

from __future__ import annotations

import time
from typing import Any

import requests

from eastmoney.cache import TTLCache
from eastmoney.config import HEADERS, UT_TOKEN


class EastMoneyClient:
    """东方财富非官方接口客户端。"""

    def __init__(self, min_interval: float = 0.6, max_retries: int = 2) -> None:
        self._session = requests.Session()
        self._session.headers.update(HEADERS)
        self._min_interval = min_interval
        self._max_retries = max_retries
        self._last_request = 0.0
        self._cache = TTLCache()

    def _throttle(self) -> None:
        elapsed = time.time() - self._last_request
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request = time.time()

    def get_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        *,
        cache_key: str | None = None,
        cache_ttl: float = 0,
        headers: dict[str, str] | None = None,
    ) -> Any:
        if cache_key:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        req_params = dict(params or {})
        if "eastmoney.com" in url and "ut" not in req_params:
            req_params["ut"] = UT_TOKEN

        req_headers = {**self._session.headers, **(headers or {})}

        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                self._throttle()
                resp = self._session.get(
                    url,
                    params=req_params,
                    headers=req_headers,
                    timeout=15,
                )
                resp.raise_for_status()
                data = resp.json()
                if cache_key and cache_ttl > 0:
                    self._cache.set(cache_key, data, cache_ttl)
                return data
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                if attempt + 1 < self._max_retries:
                    time.sleep(0.8 * (attempt + 1))
        assert last_error is not None
        raise last_error
