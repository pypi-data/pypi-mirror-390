"""
Utility functions

Small helper functions that don't belong anywhere else.
"""

import re
from datetime import datetime
from typing import Union


def validate_user_id(user_id: str) -> str:
    """Validate and normalize user ID

    Args:
        user_id: User ID to validate

    Returns:
        Normalized user ID string

    Raises:
        ValueError: If user ID format is invalid
    """
    if not user_id:
        raise ValueError("User ID cannot be empty")

    # Convert to string and strip whitespace
    user_id_str = str(user_id).strip()

    # Check if it's all digits
    if not re.match(r"^\d+$", user_id_str):
        raise ValueError(f"Invalid user ID format: {user_id_str}")

    # Check reasonable length (1-20 digits)
    if len(user_id_str) < 1 or len(user_id_str) > 20:
        raise ValueError(f"User ID length must be 1-20 digits: {user_id_str}")

    return user_id_str


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
