"""
Basic tests for the new clean architecture
"""

from datetime import datetime

import pytest

from weibo_cli import (
    Comment,
    Image,
    Post,
    User,
    Video,
    WeiboClient,
    WeiboConfig,
    validate_post_id,
)
from weibo_cli.parsers import UserParser
from weibo_cli.utils import dump_raw_json
from weibo_cli.exceptions import WeiboError, AuthError, NetworkError, ParseError
from weibo_cli.utils import parse_weibo_timestamp


class TestBasicImports:
    """Test that all basic imports work"""

    def test_main_imports(self):
        """Test main component imports"""
        assert WeiboClient is not None
        assert WeiboConfig is not None

    def test_model_imports(self):
        """Test model imports"""
        assert User is not None
        assert Post is not None
        assert Comment is not None
        assert Image is not None
        assert Video is not None

    def test_exception_imports(self):
        """Test exception imports"""
        assert WeiboError is not None
        assert AuthError is not None
        assert NetworkError is not None
        assert ParseError is not None


class TestConfig:
    """Test configuration classes"""

    def test_default_config(self):
        """Test default configuration creation"""
        config = WeiboConfig()
        assert config.http.timeout == 10.0
        assert config.auth.cookie_ttl == 300.0
        assert config.api.base_url == "https://weibo.com"

    def test_fast_config(self):
        """Test fast configuration"""
        config = WeiboConfig.create_fast()
        assert config.http.timeout == 5.0
        assert config.http.max_retries == 1
        assert config.auth.cookie_ttl == 120.0

    def test_conservative_config(self):
        """Test conservative configuration"""
        config = WeiboConfig.create_conservative()
        assert config.http.timeout == 15.0
        assert config.http.max_retries == 5
        assert config.auth.cookie_ttl == 600.0


class TestModels:
    """Test basic model creation"""

    def test_user_creation(self):
        """Test User model creation"""
        user = User(
            id=123,
            screen_name="Test User",
            profile_image_url="https://example.com/avatar.jpg",
        )
        assert user.id == 123
        assert user.screen_name == "Test User"
        assert user.verified is False

    def test_image_creation(self):
        """Test Image model creation"""
        image = Image(
            id="img123",
            thumbnail_url="https://example.com/thumb.jpg",
            large_url="https://example.com/large.jpg",
            original_url="https://example.com/original.jpg",
        )
        assert image.id == "img123"
        assert image.width == 0  # default
        assert image.height == 0  # default

    def test_video_creation(self):
        """Test Video model creation"""
        video = Video(duration=120.5, play_count=1000)
        assert video.duration == 120.5
        assert video.play_count == 1000
        assert video.urls == {}  # default


class TestValidationUtils:
    """Test helper validation functions"""

    def test_validate_post_id_success(self):
        """Post ID should be normalized when valid"""

        assert validate_post_id("  5226761046462968  ") == "5226761046462968"

    def test_validate_post_id_invalid_format(self):
        """Non-numeric post IDs should raise ValueError"""

        with pytest.raises(ValueError, match="Invalid Post ID format"):
            validate_post_id("invalid")


class TestRawPayloadStorage:
    """Ensure raw payloads are persisted as JSON strings"""

    def test_dump_raw_json_dict(self):
        """Dict payload is serialized to compact JSON"""

        raw = dump_raw_json({"a": 1, "b": "测试"})
        assert raw == '{"a":1,"b":"测试"}'

    def test_user_parser_raw_string_snapshot(self):
        """UserParser stores JSON string in raw field"""

        parser = UserParser()
        data = {
            "id": 1,
            "screen_name": "Tester",
            "profile_image_url": "https://example.com/avatar.jpg",
            "followers_count": 5,
            "friends_count": 3,
        }

        user = parser.parse(data)
        assert isinstance(user.raw, str)
        assert '"screen_name":"Tester"' in user.raw


class TestTimestampParsing:
    """Test timestamp parsing utility"""

    def test_parse_weibo_format1(self):
        """Test parsing Weibo format 1: 'Mon Jan 01 12:00:00 +0800 2024'"""
        timestamp_str = "Mon Jan 01 12:00:00 +0800 2024"
        result = parse_weibo_timestamp(timestamp_str)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 12

    def test_parse_weibo_format2(self):
        """Test parsing Weibo format 2: '2025-06-29 06:46:38+08:00'"""
        timestamp_str = "2025-06-29 06:46:38+08:00"
        result = parse_weibo_timestamp(timestamp_str)
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 6
        assert result.day == 29
        assert result.hour == 6

    def test_parse_empty_string(self):
        """Test parsing empty string raises ValueError"""
        with pytest.raises(ValueError, match="Timestamp string is empty"):
            parse_weibo_timestamp("")

    def test_parse_invalid_format(self):
        """Test parsing invalid format raises ValueError"""
        with pytest.raises(ValueError, match="Unrecognized timestamp format"):
            parse_weibo_timestamp("2024-01-01")

    def test_parse_none(self):
        """Test parsing None raises ValueError (treated as empty)"""
        with pytest.raises(ValueError, match="Timestamp string is empty"):
            parse_weibo_timestamp(None)


@pytest.mark.asyncio
class TestClientBasics:
    """Test basic client functionality"""

    async def test_client_context_manager(self):
        """Test client can be used as context manager"""
        async with WeiboClient() as client:
            assert client is not None
            assert hasattr(client, "get_user")
            assert hasattr(client, "get_user_posts")
            assert hasattr(client, "get_post")
            assert hasattr(client, "get_post_comments")

    async def test_client_with_config(self):
        """Test client creation with custom config"""
        config = WeiboConfig.create_fast()
        async with WeiboClient(config=config) as client:
            assert client._config.http.timeout == 5.0
            assert client._config.http.max_retries == 1

    async def test_client_with_rate_limits(self):
        """Client should accept concurrency and rate limit options"""
        async with WeiboClient(
            max_concurrent_requests=2,
            requests_per_interval=5,
            rate_interval_seconds=0.01,
        ) as client:
            assert client._request_gate is not None
