"""Business entities implemented with Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WeiboBaseModel(BaseModel):
    """Base model that stores the original payload for debugging."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    raw: str | None = Field(
        default=None,
        repr=False,
        description="Original payload returned by the API",
    )

    @field_validator("raw", mode="before")
    @classmethod
    def _ensure_str(cls, value: Any) -> str | None:
        if value is None or isinstance(value, str):
            return value
        return str(value)


class User(WeiboBaseModel):
    """Weibo user entity"""

    id: int
    screen_name: str
    profile_image_url: str
    followers_count: int = 0
    friends_count: int = 0
    location: str | None = None
    description: str | None = None
    verified: bool = False
    verified_reason: str | None = None


class Image(WeiboBaseModel):
    """Weibo image attachment"""

    id: str
    thumbnail_url: str
    large_url: str
    original_url: str
    width: int = 0
    height: int = 0


class Video(WeiboBaseModel):
    """Weibo video attachment"""

    duration: float = 0.0
    play_count: int = 0
    urls: dict[str, str] = Field(default_factory=dict)


class Post(WeiboBaseModel):
    """Weibo post entity"""

    id: int
    created_at: datetime
    text: str
    user: User
    text_raw: str | None = None
    region_name: str | None = None
    source: str | None = None
    reposts_count: int = 0
    comments_count: int = 0
    attitudes_count: int = 0
    images: list[Image] = Field(default_factory=list)
    video: Video | None = None


class Comment(WeiboBaseModel):
    """Weibo comment entity"""

    id: int
    created_at: datetime
    text: str
    user: User
    rootid: int = 0
    floor_number: int = 0
    like_count: int = 0
