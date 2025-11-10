"""Parser unit tests backed by captured fixtures"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from weibo_cli.parsers import CommentParser, PostParser, UserParser

DATA_ROOT = Path(__file__).parent / "data"
RAW_DIR = DATA_ROOT / "raw_responses"
DETAIL_DIR = DATA_ROOT / "weibo_details"


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_user_parser_with_real_profile():
    parser = UserParser()
    payload = _load_json(RAW_DIR / "user_profile_1749127163_raw.json")
    user_data = payload["data"]["user"]

    user = parser.parse(user_data)

    assert user.id == 1749127163
    assert user.screen_name == "雷军"
    assert user.followers_count > 0
    assert user.raw is not None


def test_post_parser_with_timeline_payload():
    parser = PostParser()
    payload = _load_json(RAW_DIR / "user_timeline_1749127163_page1_raw.json")
    first_post = payload["data"]["list"][0]

    post = parser.parse(first_post)

    assert post.id == int(first_post["id"])
    assert post.user.screen_name
    assert post.reposts_count >= 0


def test_post_parser_detail_page_roundtrip():
    parser = PostParser()
    status = _load_json(DETAIL_DIR / "weibo_5182764446908977.json")
    render_payload = {"status": status}
    script = json.dumps(render_payload, ensure_ascii=False)
    html = f"<html><body><script>var $render_data = [{script}][0] || {{}};</script></body></html>"

    post = parser.parse_detail_page(html)

    assert post.id == status["id"]
    assert post.user.screen_name == status["user"]["screen_name"]
    assert post.text.startswith("小米人车家")


def test_comment_parser_with_sample_payload():
    parser = CommentParser()
    payload = _load_json(RAW_DIR / "weibo_comments_5182764446908977_page1_raw.json")
    comment_data = payload["data"]["data"][0]

    comment = parser.parse(comment_data)

    assert comment.id == int(comment_data["id"])
    assert comment.user.screen_name
    assert comment.text
