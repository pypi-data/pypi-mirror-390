"""
Pure HTTP client for Weibo API

Simple, focused HTTP client that does one thing well.
No business logic, just HTTP requests.
"""

import json
import logging
from typing import Any, Awaitable, Callable, TypeVar

import httpx

from ..exceptions import NetworkError, ParseError
from .rate_limit import RequestGate

T = TypeVar("T")


class HttpClient:
    """Pure HTTP client

    Responsibilities:
    - Make HTTP requests
    - Handle basic HTTP errors
    - Manage connection lifecycle

    Does NOT handle:
    - Authentication/cookies (that's auth.py)
    - Retries (that's retry.py)
    - Business logic parsing (that's parsers/)
    """

    def __init__(
        self,
        timeout: float = 10.0,
        max_connections: int = 20,
        max_keepalive_connections: int = 5,
        logger: logging.Logger | None = None,
        gate: RequestGate | None = None,
    ):
        self._timeout = timeout
        self._max_connections = max_connections
        self._max_keepalive_connections = max_keepalive_connections
        self._logger = logger or logging.getLogger(__name__)
        self._client: httpx.AsyncClient | None = None
        self._gate = gate if gate and gate.enabled else None

    async def __aenter__(self) -> "HttpClient":
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self._timeout),
            limits=httpx.Limits(
                max_connections=self._max_connections,
                max_keepalive_connections=self._max_keepalive_connections,
            ),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_json(
        self, url: str, headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Get JSON response"""
        if not self._client:
            raise RuntimeError(
                "Client not initialized. Use 'async with' context manager"
            )

        async def _request() -> dict[str, Any]:
            response = await self._client.get(url, headers=headers or {})
            response.raise_for_status()

            data = response.json()
            self._logger.debug(f"GET {url} -> {response.status_code}")
            return data

        try:
            return await self._with_limits(_request)
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise NetworkError(f"HTTP {e.response.status_code}", e.response.status_code)

        except httpx.RequestError as e:
            self._logger.error(f"Request failed: {url} - {e}")
            raise NetworkError(f"Request failed: {e}")

        except json.JSONDecodeError as e:
            self._logger.error(f"Invalid JSON response: {url}")
            raise ParseError(f"Invalid JSON: {e}")

    async def get_text(self, url: str, headers: dict[str, str] | None = None) -> str:
        """Get text response"""
        if not self._client:
            raise RuntimeError(
                "Client not initialized. Use 'async with' context manager"
            )

        async def _request() -> str:
            response = await self._client.get(url, headers=headers or {})
            response.raise_for_status()

            self._logger.debug(f"GET {url} -> {response.status_code}")
            return response.text

        try:
            return await self._with_limits(_request)
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise NetworkError(f"HTTP {e.response.status_code}", e.response.status_code)

        except httpx.RequestError as e:
            self._logger.error(f"Request failed: {url} - {e}")
            raise NetworkError(f"Request failed: {e}")

    async def get_raw(
        self, url: str, headers: dict[str, str] | None = None, follow_redirects: bool = True
    ) -> httpx.Response:
        """Get raw response with cookies

        Args:
            url: URL to fetch
            headers: Optional request headers
            follow_redirects: Whether to follow redirects. If False, 3xx responses are returned as-is.

        Returns:
            Raw HTTP response
        """
        if not self._client:
            raise RuntimeError(
                "Client not initialized. Use 'async with' context manager"
            )

        async def _request() -> httpx.Response:
            response = await self._client.get(
                url, headers=headers or {}, follow_redirects=follow_redirects
            )

            if response.status_code >= 400:
                response.raise_for_status()

            self._logger.debug(f"GET {url} -> {response.status_code}")
            return response

        try:
            return await self._with_limits(_request)
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise NetworkError(f"HTTP {e.response.status_code}", e.response.status_code)

        except httpx.RequestError as e:
            self._logger.error(f"Request failed: {url} - {e}")
            raise NetworkError(f"Request failed: {e}")

    async def post_form(
        self, url: str, data: dict[str, Any], headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """POST form data and get JSON response"""
        if not self._client:
            raise RuntimeError(
                "Client not initialized. Use 'async with' context manager"
            )

        async def _request() -> dict[str, Any]:
            response = await self._client.post(url, data=data, headers=headers or {})
            response.raise_for_status()

            result = response.json()
            self._logger.debug(f"POST {url} -> {response.status_code}")
            return result

        try:
            return await self._with_limits(_request)
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise NetworkError(f"HTTP {e.response.status_code}", e.response.status_code)

        except httpx.RequestError as e:
            self._logger.error(f"Request failed: {url} - {e}")
            raise NetworkError(f"Request failed: {e}")

        except json.JSONDecodeError as e:
            self._logger.error(f"Invalid JSON response: {url}")
            raise ParseError(f"Invalid JSON: {e}")

    async def post_form_raw(
        self, url: str, data: dict[str, Any], headers: dict[str, str] | None = None
    ) -> httpx.Response:
        """POST form data and get raw response with cookies"""
        if not self._client:
            raise RuntimeError(
                "Client not initialized. Use 'async with' context manager"
            )

        async def _request() -> httpx.Response:
            response = await self._client.post(url, data=data, headers=headers or {})
            response.raise_for_status()

            self._logger.debug(f"POST {url} -> {response.status_code}")
            return response

        try:
            return await self._with_limits(_request)
        except httpx.HTTPStatusError as e:
            self._logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise NetworkError(f"HTTP {e.response.status_code}", e.response.status_code)

        except httpx.RequestError as e:
            self._logger.error(f"Request failed: {url} - {e}")
            raise NetworkError(f"Request failed: {e}")

    async def _with_limits(self, call: Callable[[], Awaitable[T]]) -> T:
        if not self._gate:
            return await call()

        async with self._gate.slot():
            return await call()
