"""
Modern Weibo API Client

Simple, clean, focused API for Weibo data extraction.

Example:
    async with WeiboClient() as client:
        user = await client.get_user("123456")
        posts = await client.get_user_posts("123456")
        comments = await client.get_post_comments("456789")
"""

from .config import WeiboConfig
from .exceptions import AuthError, NetworkError, ParseError, WeiboError
from .models import Comment, Image, Post, User, Video
from .core.rate_limit import RateLimiter
from .utils import (
    parse_count_string,
    parse_weibo_timestamp,
    validate_post_id,
    validate_user_id,
)
from .weibo_client import WeiboClient

__version__ = "1.0.4"
__author__ = "Birkhoff"
__description__ = "Simple, focused Weibo API client"

__all__ = [
    # Main client
    "WeiboClient",
    # Configuration
    "WeiboConfig",
    # Data models
    "User",
    "Post",
    "Comment",
    "Image",
    "Video",
    "RateLimiter",
    # Exceptions
    "WeiboError",
    "AuthError",
    "NetworkError",
    "ParseError",
    # Utilities
    "validate_user_id",
    "validate_post_id",
    "parse_count_string",
    "parse_weibo_timestamp",
]
