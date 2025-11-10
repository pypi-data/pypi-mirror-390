"""CookieManager focused unit tests"""

from __future__ import annotations

import asyncio
import time
from types import MethodType, SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from weibo_cli.core.auth import CookieManager


@pytest.fixture
def dummy_http():
    return SimpleNamespace(get_json=AsyncMock())


@pytest.mark.asyncio
async def test_snapshot_after_manual_set(dummy_http):
    manager = CookieManager(http_client=dummy_http, ttl=5.0)
    manager.set_cookies("SUB=foo; SUBP=bar")

    snapshot = manager.snapshot()

    assert "SUB=foo" in snapshot["cookies"]
    assert snapshot["expires_at"] is not None


@pytest.mark.asyncio
async def test_validate_cookies_short_circuit_on_format(dummy_http):
    manager = CookieManager(http_client=dummy_http)
    result = await manager.validate_cookies("invalid-cookie")
    assert result is False
    dummy_http.get_json.assert_not_called()


@pytest.mark.asyncio
async def test_validate_cookies_hits_http(dummy_http):
    dummy_http.get_json.return_value = {"ok": 1}
    manager = CookieManager(http_client=dummy_http)

    result = await manager.validate_cookies("SUB=foo; SUBP=bar")

    assert result is True
    dummy_http.get_json.assert_awaited()


@pytest.mark.asyncio
async def test_ensure_valid_cookies_only_generates_once(dummy_http):
    manager = CookieManager(http_client=dummy_http, ttl=0.1)
    manager._cookies = None
    manager._expires_at = time.time() - 10

    counter = {"calls": 0}

    async def fake_generate(self):
        counter["calls"] += 1
        self.set_cookies("SUB=foo; SUBP=bar")

    manager._generate_cookies = MethodType(fake_generate, manager)

    await asyncio.gather(*(manager.ensure_valid_cookies() for _ in range(5)))

    assert counter["calls"] == 1


@pytest.mark.asyncio
async def test_refresh_bypasses_cache(dummy_http):
    manager = CookieManager(http_client=dummy_http, ttl=5.0)
    manager.set_cookies("SUB=old; SUBP=old")

    async def fake_generate(self):
        self.set_cookies("SUB=new; SUBP=new")

    manager._generate_cookies = MethodType(fake_generate, manager)

    refreshed = await manager.refresh()

    assert "SUB=new" in refreshed
    assert manager.get_cookies().startswith("SUB=new")
