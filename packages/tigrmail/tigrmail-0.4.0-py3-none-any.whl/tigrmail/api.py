from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx


DEFAULT_BASE_URL = "https://api.tigrmail.com"
DEFAULT_TIMEOUT = 180.0  # seconds


class ApiClient:
    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = max(0, retries)
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"},
        )

    def close(self) -> None:
        self._client.close()

    def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        json: Any = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        delay = 0.0
        last_exc: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            if attempt > 0:
                # exponential backoff (httpx has no built-in retry)
                delay = 0.5 * (2 ** (attempt - 1))
                time.sleep(delay)
            try:
                resp = self._client.request(
                    method,
                    url,
                    headers=headers,
                    json=json,
                    params=params,
                )
                # mirror axios-retry's retryCondition: retry on any status
                if 200 <= resp.status_code < 300:
                    return resp
                # Raise to unify error handling and allow retry loop to continue
                resp.raise_for_status()
            except (httpx.HTTPError,) as exc:
                last_exc = exc
                # continue loop to retry
                continue
        # Exhausted retries
        assert last_exc is not None
        raise last_exc

    def post(self, url: str, *, headers: Optional[Dict[str, str]] = None, json: Any = None) -> httpx.Response:
        return self._request_with_retry("POST", url, headers=headers, json=json)

    def get(self, url: str, *, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        return self._request_with_retry("GET", url, headers=headers, params=params)

