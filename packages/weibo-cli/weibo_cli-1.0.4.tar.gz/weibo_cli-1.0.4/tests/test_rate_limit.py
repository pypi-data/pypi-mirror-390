"""Rate limiter unit tests"""

from __future__ import annotations

import asyncio
import time

import pytest

from weibo_cli.core.rate_limit import RateLimiter, RequestGate


@pytest.mark.asyncio
async def test_rate_limiter_enforces_interval():
    limiter = RateLimiter(max_requests=1, interval=0.2)

    start = time.perf_counter()
    await limiter.acquire()
    first_elapsed = time.perf_counter() - start
    assert first_elapsed < 0.05

    start_second = time.perf_counter()
    await limiter.acquire()
    second_elapsed = time.perf_counter() - start_second
    assert second_elapsed >= 0.18


@pytest.mark.asyncio
async def test_request_gate_limits_concurrency():
    gate = RequestGate(max_concurrency=2)
    active = 0
    peak = 0

    async def worker():
        nonlocal active, peak
        async with gate.slot():
            active += 1
            peak = max(peak, active)
            await asyncio.sleep(0.05)
            active -= 1

    await asyncio.gather(*(worker() for _ in range(5)))

    assert peak <= 2
