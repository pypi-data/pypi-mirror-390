"""
Cookie authentication manager

Simple cookie management with clear state.
No complex state machines, just basic validation and generation.
"""

import json
import logging
import re
import time

import httpx

from .client import HttpClient
from ..exceptions import AuthError, ParseError, NetworkError


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

    async def ensure_valid_cookies(self) -> str:
        """Ensure we have valid cookies, generate if needed"""
        # Return cached cookies if still valid
        if not self._is_expired() and self._cookies:
            if self._is_valid_format(self._cookies):
                return self._cookies
            else:
                self._logger.warning("Cached cookies have invalid format")

        # Generate new cookies and XSRF token
        await self._generate_cookies()

        if not self._cookies:
            raise AuthError("Failed to generate cookies")

        return self._cookies

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
                follow_redirects=False,
            )

            xsrf_token = response.cookies.get("XSRF-TOKEN")
            self._set_cookies_with_xsrf(sub, subp, xsrf_token)

        except Exception as e:
            self._logger.error(f"XSRF token fetch failed: {e}")
            self._set_cookies_with_xsrf(sub, subp, None)

    def _set_cookies_with_xsrf(
        self, sub: str, subp: str, xsrf_token: str | None
    ) -> None:
        """Set final cookies with optional XSRF token

        Args:
            sub: SUB cookie value
            subp: SUBP cookie value
            xsrf_token: XSRF-TOKEN value or None
        """
        if xsrf_token:
            self._cookies = f"XSRF-TOKEN={xsrf_token}; SUB={sub}; SUBP={subp}"
            self._xsrf_token = xsrf_token
            self._logger.info(f"✅ Fetched XSRF token: {xsrf_token[:20]}...")
        else:
            self._cookies = f"SUB={sub}; SUBP={subp}"
            self._xsrf_token = None
            self._logger.warning("⚠️ No XSRF token received, using basic cookies")

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
