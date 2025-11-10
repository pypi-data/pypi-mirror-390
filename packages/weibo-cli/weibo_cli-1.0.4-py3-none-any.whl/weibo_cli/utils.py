"""Utility helpers shared across the client."""

import json
import re
from datetime import datetime
from typing import Any, Union


def _validate_numeric_id(
    value: Union[str, int],
    *,
    field_name: str,
    min_length: int = 1,
    max_length: int = 32,
    allow_letters: bool = False,
) -> str:
    """Normalize and validate numeric IDs used by the API."""

    if value is None:
        raise ValueError(f"{field_name} cannot be empty")

    value_str = str(value).strip()
    if not value_str:
        raise ValueError(f"{field_name} cannot be empty")

    pattern = r"^[A-Za-z0-9]+$" if allow_letters else r"^\d+$"
    if not re.match(pattern, value_str):
        raise ValueError(f"Invalid {field_name} format: {value_str}")

    if len(value_str) < min_length or len(value_str) > max_length:
        raise ValueError(
            f"{field_name} length must be {min_length}-{max_length} characters: {value_str}"
        )

    return value_str


def validate_user_id(user_id: Union[str, int]) -> str:
    """Validate and normalize user IDs."""

    return _validate_numeric_id(
        user_id,
        field_name="User ID",
        min_length=1,
        max_length=20,
        allow_letters=False,
    )


def validate_post_id(post_id: Union[str, int]) -> str:
    """Validate and normalize post IDs.

    Post IDs can be longer than user IDs, so we allow up to 32 characters.
    """

    return _validate_numeric_id(
        post_id,
        field_name="Post ID",
        min_length=1,
        max_length=32,
        allow_letters=False,
    )


def dump_raw_json(data: Any) -> str | None:
    """Serialize raw API payloads to JSON strings for storage on models."""

    if data is None:
        return None

    if isinstance(data, str):
        return data

    try:
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    except TypeError:
        # Fallback for non-serializable data (e.g., datetime objects hidden in payloads)
        return str(data)


def parse_count_string(value: Union[str, int, float, None]) -> int:
    """Parse Chinese count strings like "2683.1万" into integers

    Args:
        value: Count value (string, int, float, or None)

    Returns:
        Integer count
    """
    if value is None:
        return 0

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        value = value.strip()
        if "万" in value:
            try:
                num = float(value.replace("万", ""))
                return int(num * 10000)
            except ValueError:
                pass
        elif "亿" in value:
            try:
                num = float(value.replace("亿", ""))
                return int(num * 100000000)
            except ValueError:
                pass

    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def parse_weibo_timestamp(timestamp_str: str) -> datetime:
    """Parse Weibo timestamp string to datetime

    Supports multiple Weibo timestamp formats.

    Args:
        timestamp_str: Timestamp string from Weibo API

    Returns:
        Parsed datetime object

    Raises:
        ValueError: If timestamp format is not recognized

    Examples:
        >>> parse_weibo_timestamp("Mon Jan 01 12:00:00 +0800 2024")
        datetime.datetime(2024, 1, 1, 12, 0, 0, ...)
        >>> parse_weibo_timestamp("2025-06-29 06:46:38+08:00")
        datetime.datetime(2025, 6, 29, 6, 46, 38, ...)
    """
    if not timestamp_str:
        raise ValueError("Timestamp string is empty")

    # Weibo timestamp formats
    formats = [
        "%a %b %d %H:%M:%S %z %Y",  # Mon Jan 01 12:00:00 +0800 2024
        "%Y-%m-%d %H:%M:%S%z",  # 2025-06-29 06:46:38+08:00
    ]

    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unrecognized timestamp format: {timestamp_str}")
