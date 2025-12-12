from __future__ import annotations
import requests
from typing import Any, Dict, Optional
from .rate_limiter import RateLimiter

BASE_URL = "https://mpcfill.com/"
TIMEOUT = 10

# Default rate limiter (10 requests/sec)
rate_limit = RateLimiter(max_calls_per_second=10)


class Client:
    """
    Small wrapper around `requests` with:
    - Global base URL and timeout
    - Consistent error handling
    - Rate limiting via decorator
    """

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = base_url or BASE_URL
        self.timeout = timeout or TIMEOUT

    def _make_url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    @rate_limit
    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = self._make_url(path)
        resp = requests.get(url, params=params, timeout=self.timeout)
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(f"HTTP GET failed: {exc}, url={url}, params={params}") from exc
        return resp.json()

    @rate_limit
    def post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Any:
        url = self._make_url(path)
        resp = requests.post(url, json=data, timeout=self.timeout)
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(f"HTTP POST failed: {exc}, url={url}, data={data}") from exc
        return resp.json()

    @rate_limit
    def raw_get(self, url: str) -> bytes:
        resp = requests.get(url, timeout=self.timeout)
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(f"HTTP GET failed: {exc}, url={url}") from exc
        return resp.content


__all__ = ["Client", "client"]

# Default client singleton
client = Client()