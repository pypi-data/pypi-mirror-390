"""
Clean configuration classes

No backward compatibility, just what we need.
"""

from dataclasses import dataclass, field
import re


@dataclass
class HttpConfig:
    """HTTP client configuration"""

    timeout: float = 10.0
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    max_connections: int = 20
    max_keepalive_connections: int = 5

    def __post_init__(self):
        """Validate business rules"""
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        if self.base_delay < 0:
            raise ValueError("base_delay cannot be negative")
        if self.max_delay < self.base_delay:
            raise ValueError("max_delay must be >= base_delay")


@dataclass
class AuthConfig:
    """Authentication configuration"""

    cookie_ttl: float = 300.0  # 5 minutes

    def __post_init__(self):
        """Validate business rules"""
        if self.cookie_ttl <= 0:
            raise ValueError("cookie_ttl must be positive")


@dataclass
class ApiConfig:
    """API endpoint configuration"""

    base_url: str = "https://weibo.com"
    mobile_url: str = "https://m.weibo.cn"
    visitor_url: str = "https://passport.weibo.com/visitor/genvisitor2"
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    # URL validation regex
    _URL_PATTERN = re.compile(r"^https?://")

    # User agent constraints
    MIN_UA_LENGTH = 10
    MAX_UA_LENGTH = 500

    def __post_init__(self):
        """Validate business rules"""
        # Validate URLs
        self._validate_url("base_url", self.base_url)
        self._validate_url("mobile_url", self.mobile_url)
        self._validate_url("visitor_url", self.visitor_url)

        # Validate user agent
        if not self.user_agent:
            raise ValueError("user_agent cannot be empty")
        if len(self.user_agent) < self.MIN_UA_LENGTH:
            raise ValueError(f"user_agent too short (min {self.MIN_UA_LENGTH} chars)")
        if len(self.user_agent) > self.MAX_UA_LENGTH:
            raise ValueError(f"user_agent too long (max {self.MAX_UA_LENGTH} chars)")

    def _validate_url(self, field_name: str, url: str) -> None:
        """Validate URL format

        Args:
            field_name: Field name for error message
            url: URL string to validate

        Raises:
            ValueError: If URL is invalid
        """
        if not url:
            raise ValueError(f"{field_name} cannot be empty")
        if not self._URL_PATTERN.match(url):
            raise ValueError(f"{field_name} must start with http:// or https://")


@dataclass
class WeiboConfig:
    """Main configuration container"""

    http: HttpConfig = field(default_factory=HttpConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    api: ApiConfig = field(default_factory=ApiConfig)

    @classmethod
    def create_fast(cls) -> "WeiboConfig":
        """Fast configuration for quick operations"""
        return cls(
            http=HttpConfig(timeout=5.0, max_retries=1, base_delay=0.5),
            auth=AuthConfig(cookie_ttl=120.0),  # 2 minutes
        )

    @classmethod
    def create_conservative(cls) -> "WeiboConfig":
        """Conservative configuration for reliability"""
        return cls(
            http=HttpConfig(timeout=15.0, max_retries=5, base_delay=2.0),
            auth=AuthConfig(cookie_ttl=600.0),  # 10 minutes
        )
