"""
Simple Weibo API client facade

Clean, focused interface that does what you need.
No dependency injection, no complex configuration.
Just works.
"""

import logging
from typing import Any, Callable, TypeVar

from .config import WeiboConfig
from .core.auth import CookieManager
from .core.client import HttpClient
from .core.retry import RetryStrategy
from .core.rate_limit import RateLimiter, RequestGate
from .exceptions import ParseError, WeiboError
from .models.entities import Comment, Post, User
from .parsers import CommentParser, PostParser, UserParser
from .utils import validate_post_id, validate_user_id

T = TypeVar("T")


class WeiboClient:
    """Simple Weibo API client

    Easy to use facade for Weibo API operations.
    Handles authentication, retries, and parsing automatically.

    Example:
        async with WeiboClient() as client:
            user = await client.get_user("123456")
            posts = await client.get_user_posts("123456")
    """

    def __init__(
        self,
        cookies: str | None = None,
        config: WeiboConfig | None = None,
        logger: logging.Logger | None = None,
        *,
        max_concurrent_requests: int | None = None,
        requests_per_interval: int | None = None,
        rate_interval_seconds: float = 1.0,
        rate_limiter: RateLimiter | None = None,
    ):
        self._config = config or WeiboConfig()
        self._logger = logger or logging.getLogger(__name__)

        limiter = rate_limiter
        if limiter is None and requests_per_interval:
            limiter = RateLimiter(
                max_requests=requests_per_interval, interval=rate_interval_seconds
            )

        request_gate: RequestGate | None = None
        if max_concurrent_requests or limiter:
            request_gate = RequestGate(
                max_concurrency=max_concurrent_requests,
                rate_limiter=limiter,
            )

        self._request_gate = request_gate

        # Initialize components
        self._http_client = HttpClient(
            timeout=self._config.http.timeout,
            max_connections=self._config.http.max_connections,
            max_keepalive_connections=self._config.http.max_keepalive_connections,
            logger=self._logger,
            gate=self._request_gate,
        )

        self._cookie_manager = CookieManager(
            http_client=self._http_client,
            ttl=self._config.auth.cookie_ttl,
            user_agent=self._config.api.user_agent,
            logger=self._logger,
        )

        self._retry_strategy = RetryStrategy(
            max_attempts=self._config.http.max_retries,
            base_delay=self._config.http.base_delay,
            max_delay=self._config.http.max_delay,
            logger=self._logger,
        )

        # Initialize parsers
        self._user_parser = UserParser(self._logger)
        self._post_parser = PostParser(self._logger)
        self._comment_parser = CommentParser(self._logger)

        # Set initial cookies if provided
        if cookies:
            self._cookie_manager.set_cookies(cookies)

    async def __aenter__(self) -> "WeiboClient":
        await self._http_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._http_client.__aexit__(exc_type, exc_val, exc_tb)

    async def _build_api_headers(
        self, referer: str = "https://weibo.com/", include_xsrf: bool = True
    ) -> dict[str, str]:
        """Build standard API request headers

        Args:
            referer: Referer URL (default: desktop site)
            include_xsrf: Whether to include XSRF token (default: True)

        Returns:
            Headers dict ready for API requests
        """
        cookies = await self._cookie_manager.ensure_valid_cookies()

        headers = {
            "Cookie": cookies,
            "User-Agent": self._config.api.user_agent,
            "Referer": referer,
        }

        if include_xsrf:
            xsrf_token = self._cookie_manager.get_xsrf_token()
            if xsrf_token:
                headers["X-XSRF-TOKEN"] = xsrf_token
                headers["x-xsrf-token"] = xsrf_token
                headers["X-Requested-With"] = "XMLHttpRequest"

        return headers

    async def get_cookies(self) -> str:
        """Return validated cookies string"""
        return await self._cookie_manager.ensure_valid_cookies()

    async def refresh_cookies(self) -> str:
        """Force refresh cookies"""
        return await self._cookie_manager.refresh()

    def set_cookies(self, cookies: str) -> None:
        """Manually set cookies for the client"""
        self._cookie_manager.set_cookies(cookies)

    def get_cached_cookies(self) -> str | None:
        """Return cached cookies without refreshing"""
        return self._cookie_manager.get_cookies()

    async def validate_cookies(self, cookies: str | None = None) -> bool:
        """Validate cookies via test request"""
        target = cookies or self._cookie_manager.get_cookies()
        if not target:
            return False
        return await self._cookie_manager.validate_cookies(target)

    async def get_cookie_snapshot(self) -> dict[str, float | str | None]:
        """Return cookie snapshot with minimal metadata"""
        await self._cookie_manager.ensure_valid_cookies()
        return self._cookie_manager.snapshot()

    async def get_user(self, user_id: str) -> User:
        """Get user profile

        Args:
            user_id: User ID to fetch

        Returns:
            User entity with profile information

        Raises:
            WeiboError: When request fails or data is invalid
        """
        # Validate user_id format
        user_id = validate_user_id(user_id)

        async def fetch_user() -> User:
            headers = await self._build_api_headers()
            url = f"{self._config.api.base_url}/ajax/profile/info?uid={user_id}"
            response = await self._http_client.get_json(url, headers)

            if response.get("ok") != 1:
                raise WeiboError(f"API returned error: {response}")

            user_data = response.get("data", {}).get("user", {})
            if not user_data:
                raise WeiboError("No user data in response")

            return self._user_parser.parse(user_data)

        return await self._retry_strategy.execute(fetch_user)

    async def get_user_posts(self, user_id: str, page: int = 1) -> list[Post]:
        """Get user's posts (timeline)

        Args:
            user_id: User ID to fetch posts for
            page: Page number (default 1)

        Returns:
            List of Post entities

        Raises:
            WeiboError: When request fails or data is invalid
        """
        # Validate user_id format
        user_id = validate_user_id(user_id)

        async def fetch_posts() -> list[Post]:
            headers = await self._build_api_headers()
            url = f"{self._config.api.base_url}/ajax/statuses/mymblog?uid={user_id}&page={page}"
            response = await self._http_client.get_json(url, headers)

            if response.get("ok") != 1:
                raise WeiboError(f"API returned error: {response}")

            posts_data = response.get("data", {}).get("list", [])
            return self._parse_entities(
                posts_data,
                self._post_parser.parse,
                summary_label="Posts",
                item_label="post",
            )

        return await self._retry_strategy.execute(fetch_posts)

    async def get_post(self, post_id: str) -> Post:
        """Get post details

        Args:
            post_id: Post ID to fetch

        Returns:
            Post entity with full details

        Raises:
            WeiboError: When request fails or data is invalid
        """

        post_id = validate_post_id(post_id)

        async def fetch_post() -> Post:
            # Mobile API: different referer, no XSRF token
            headers = await self._build_api_headers(
                referer="https://m.weibo.cn/", include_xsrf=False
            )
            url = f"{self._config.api.mobile_url}/detail/{post_id}"
            html_content = await self._http_client.get_text(url, headers)
            return self._post_parser.parse_detail_page(html_content)

        return await self._retry_strategy.execute(fetch_post)

    async def get_post_comments(self, post_id: str) -> list[Comment]:
        """Get post comments

        Args:
            post_id: Post ID to fetch comments for

        Returns:
            List of Comment entities

        Raises:
            WeiboError: When request fails or data is invalid
        """

        post_id = validate_post_id(post_id)

        async def fetch_comments() -> list[Comment]:
            # Mobile API: use mobile referer for consistency
            headers = await self._build_api_headers(referer="https://m.weibo.cn/")
            url = f"{self._config.api.mobile_url}/comments/hotflow?mid={post_id}"
            response = await self._http_client.get_json(url, headers)

            if response.get("ok") != 1:
                raise WeiboError(f"API returned error: {response}")

            comments_data = response.get("data", {}).get("data", [])
            return self._parse_entities(
                comments_data,
                self._comment_parser.parse,
                summary_label="Comments",
                item_label="comment",
            )

        return await self._retry_strategy.execute(fetch_comments)

    def _parse_entities(
        self,
        items: list[dict[str, Any]] | None,
        parse_func: Callable[[dict[str, Any]], T],
        *,
        summary_label: str,
        item_label: str,
    ) -> list[T]:
        if not items:
            self._logger.info(f"{summary_label} parsed: 0/0 (100.0% success)")
            return []

        parsed: list[T] = []
        total = len(items)
        failures = 0

        for item in items:
            try:
                parsed.append(parse_func(item))
            except ParseError as exc:
                failures += 1
                self._logger.warning(
                    f"Skipping {item_label} with invalid data: {exc}"
                )
            except (KeyError, ValueError, TypeError) as exc:
                failures += 1
                self._logger.warning(
                    f"Skipping {item_label} with malformed data: {exc}"
                )

        success_rate = (
            ((total - failures) / total * 100)
            if total > 0
            else 100.0
        )
        self._logger.info(
            f"{summary_label} parsed: {len(parsed)}/{total} ({success_rate:.1f}% success)"
        )
        return parsed
