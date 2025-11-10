"""
Cookie authentication manager

Simple cookie management with clear state.
No complex state machines, just basic validation and generation.
"""

import asyncio
import json
import logging
import re
import time

import httpx

from .client import HttpClient
from ..exceptions import AuthError, ParseError


class CookieManager:
    """Simple cookie manager

    Responsibilities:
    - Generate visitor cookies
    - Validate cookies
    - Cache cookies for configured TTL

    Does NOT handle:
    - Complex state management
    - Retry logic (that's retry.py)
    - HTTP requests (uses HttpClient)
    """

    def __init__(
        self,
        http_client: HttpClient,
        ttl: float = 300.0,  # 5 minutes
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        logger: logging.Logger | None = None,
    ):
        self._http = http_client
        self._ttl = ttl
        self._user_agent = user_agent
        self._logger = logger or logging.getLogger(__name__)

        # Simple state
        self._cookies: str | None = None
        self._xsrf_token: str | None = None
        self._expires_at: float | None = None
        self._lock = asyncio.Lock()

    def set_cookies(self, cookies: str) -> None:
        """Set cookies manually"""
        self._cookies = cookies
        self._expires_at = time.time() + self._ttl

    def get_cookies(self) -> str | None:
        """Get current valid cookies"""
        if self._is_expired():
            return None
        return self._cookies

    def get_xsrf_token(self) -> str | None:
        """Get current XSRF token"""
        if self._is_expired():
            return None
        return self._xsrf_token

    def _is_expired(self) -> bool:
        """Check if cookies are expired"""
        if not self._cookies or not self._expires_at:
            return True
        return time.time() >= self._expires_at

    def _is_valid_format(self, cookies: str) -> bool:
        """Basic cookie format validation"""
        return "SUB=" in cookies and "SUBP=" in cookies

    def _has_valid_cached_cookies(self) -> bool:
        """Check whether cached cookies are fresh and well-formed"""
        return (
            self._cookies is not None
            and not self._is_expired()
            and self._is_valid_format(self._cookies)
        )

    async def ensure_valid_cookies(self) -> str:
        """Ensure we have valid cookies, generate if needed"""
        if self._has_valid_cached_cookies():
            assert self._cookies  # for type checker
            return self._cookies

        if self._cookies and not self._is_valid_format(self._cookies):
            self._logger.warning("Cached cookies have invalid format")

        async with self._lock:
            if self._has_valid_cached_cookies():
                assert self._cookies
                return self._cookies

            await self._generate_cookies()

            if not self._cookies:
                raise AuthError("Failed to generate cookies")

            return self._cookies

    async def refresh(self) -> str:
        """Force refresh cookies regardless of cache state"""
        async with self._lock:
            await self._generate_cookies()
            if not self._cookies:
                raise AuthError("Failed to generate cookies")
            return self._cookies

    def snapshot(self) -> dict[str, float | str | None]:
        """Return current cookie/XSRF snapshot"""
        return {
            "cookies": self._cookies,
            "xsrf_token": self._xsrf_token,
            "expires_at": self._expires_at,
        }

    async def _generate_cookies(self) -> None:
        """Generate visitor cookies and fetch XSRF token"""
        try:
            sub, subp = await self._request_visitor_cookies()
            await self._fetch_xsrf_token(sub, subp)
        except Exception as e:
            self._logger.error(f"Cookie generation failed: {e}")
            raise AuthError(f"Failed to generate cookies: {e}")

    async def _request_visitor_cookies(self) -> tuple[str, str]:
        """Request visitor cookies from Weibo passport service

        Returns:
            Tuple of (SUB, SUBP) cookie values

        Raises:
            AuthError: When request fails
            ParseError: When cookie extraction fails
        """
        url = "https://passport.weibo.com/visitor/genvisitor2"
        data = {
            "cb": "visitor_gray_callback",
            "tid": "",
            "from": "weibo",
            "webdriver": "false",
        }
        headers = {
            "User-Agent": self._user_agent,
            "Referer": "https://passport.weibo.com/visitor/visitor",
        }

        self._logger.info("Generating visitor cookies...")

        try:
            response = await self._http.post_form_raw(url, data, headers)

            # Try to get cookies from response headers first
            sub = response.cookies.get("SUB")
            subp = response.cookies.get("SUBP")

            # Fallback: parse from JSONP response body
            if not (sub and subp):
                sub, subp = self._parse_visitor_cookies_from_jsonp(response.text)

            if not (sub and subp):
                raise ParseError("Cannot extract visitor cookies from response")

            self._logger.info("✅ Generated visitor cookies")
            return sub, subp

        except httpx.HTTPStatusError as e:
            raise AuthError(f"HTTP error {e.response.status_code}")
        except httpx.RequestError as e:
            raise AuthError(f"Request failed: {e}")

    def _parse_visitor_cookies_from_jsonp(
        self, jsonp_text: str
    ) -> tuple[str | None, str | None]:
        """Parse visitor cookies from JSONP response

        Args:
            jsonp_text: JSONP response text like 'callback({...})'

        Returns:
            Tuple of (SUB, SUBP) or (None, None) if parsing fails
        """
        try:
            match = re.search(r"\((.*)\)", jsonp_text)
            if not match:
                self._logger.debug("No JSONP pattern found in response text")
                return None, None

            json_data = json.loads(match.group(1))
            if json_data.get("retcode") != 20000000:
                self._logger.debug(
                    f"JSONP response has invalid retcode: {json_data.get('retcode')}"
                )
                return None, None

            data_obj = json_data.get("data", {})
            sub = data_obj.get("sub")
            subp = data_obj.get("subp")

            if not (sub and subp):
                self._logger.debug("JSONP response missing sub/subp fields")

            return sub, subp

        except json.JSONDecodeError as e:
            self._logger.debug(f"JSONP JSON parsing failed: {e}")
            return None, None
        except (KeyError, AttributeError) as e:
            self._logger.debug(f"JSONP data extraction failed: {e}")
            return None, None

    async def _fetch_xsrf_token(self, sub: str, subp: str) -> None:
        """Fetch XSRF token from homepage

        Args:
            sub: SUB cookie value
            subp: SUBP cookie value
        """
        self._logger.info("Fetching XSRF token...")

        try:
            response = await self._http.get_raw(
                url="https://weibo.com",
                headers={
                    "User-Agent": self._user_agent,
                    "Cookie": f"SUB={sub}; SUBP={subp}",
                },
                follow_redirects=True,
            )

            xsrf_token, extra_cookies = self._extract_cookie_bundle(response)
            self._set_cookies_with_xsrf(sub, subp, xsrf_token, extra_cookies)

        except Exception as e:
            self._logger.error(f"XSRF token fetch failed: {e}")
            self._set_cookies_with_xsrf(sub, subp, None)

    def _extract_cookie_bundle(
        self, response: httpx.Response
    ) -> tuple[str | None, dict[str, str]]:
        """Collect XSRF token and extra cookies from redirect chain"""
        cookies: dict[str, str] = {}
        for resp in [*response.history, response]:
            for cookie in resp.cookies.jar:
                cookies[cookie.name] = cookie.value

        xsrf_token = cookies.pop("XSRF-TOKEN", None)
        cookies.pop("SUB", None)
        cookies.pop("SUBP", None)
        return xsrf_token, cookies

    def _set_cookies_with_xsrf(
        self,
        sub: str,
        subp: str,
        xsrf_token: str | None,
        extra_cookies: dict[str, str] | None = None,
    ) -> None:
        """Set final cookies with optional XSRF token

        Args:
            sub: SUB cookie value
            subp: SUBP cookie value
            xsrf_token: XSRF-TOKEN value or None
        """
        cookie_parts: list[str] = []

        if xsrf_token:
            cookie_parts.append(f"XSRF-TOKEN={xsrf_token}")
            self._xsrf_token = xsrf_token
            self._logger.info(f"✅ Fetched XSRF token: {xsrf_token[:20]}...")
        else:
            self._xsrf_token = None
            self._logger.warning("⚠️ No XSRF token received, using basic cookies")

        if extra_cookies:
            for name, value in extra_cookies.items():
                cookie_parts.append(f"{name}={value}")

        cookie_parts.append(f"SUB={sub}")
        cookie_parts.append(f"SUBP={subp}")

        self._cookies = "; ".join(cookie_parts)

        self._expires_at = time.time() + self._ttl

    async def validate_cookies(self, cookies: str) -> bool:
        """Validate cookies by making test request"""
        if not self._is_valid_format(cookies):
            return False

        try:
            url = "https://weibo.com/ajax/profile/info?uid=1"
            headers = {
                "Cookie": cookies,
                "User-Agent": self._user_agent,
                "Referer": "https://weibo.com/",
            }

            response = await self._http.get_json(url, headers)
            return response.get("ok") == 1

        except Exception as e:
            self._logger.debug(f"Cookie validation failed: {e}")
            return False
