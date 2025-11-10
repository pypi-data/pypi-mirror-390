"""Simple async rate limiting and concurrency controls"""

from __future__ import annotations

import asyncio
from collections import deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
import time
from typing import AsyncIterator


class RateLimiter:
    """Bound the number of requests within a rolling interval"""

    def __init__(self, max_requests: int, interval: float = 1.0):
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if interval <= 0:
            raise ValueError("interval must be positive")

        self._max_requests = max_requests
        self._interval = interval
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        while True:
            async with self._lock:
                now = time.monotonic()
                self._evict_expired(now)

                if len(self._timestamps) < self._max_requests:
                    self._timestamps.append(now)
                    return

                wait_time = self._interval - (now - self._timestamps[0])

            await asyncio.sleep(max(wait_time, 0))

    def _evict_expired(self, now: float) -> None:
        boundary = now - self._interval
        while self._timestamps and self._timestamps[0] < boundary:
            self._timestamps.popleft()


@dataclass(slots=True)
class RequestGate:
    """Coordinate concurrency and rate limits for HTTP requests"""

    max_concurrency: int | None = None
    rate_limiter: RateLimiter | None = None

    _semaphore: asyncio.Semaphore | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        if self.max_concurrency is not None:
            if self.max_concurrency <= 0:
                raise ValueError("max_concurrency must be positive")
            self._semaphore = asyncio.Semaphore(self.max_concurrency)
        else:
            self._semaphore = None

    @property
    def enabled(self) -> bool:
        return bool(self._semaphore or self.rate_limiter)

    @asynccontextmanager
    async def slot(self) -> AsyncIterator[None]:
        if self.rate_limiter:
            await self.rate_limiter.acquire()

        if self._semaphore:
            await self._semaphore.acquire()

        try:
            yield
        finally:
            if self._semaphore:
                self._semaphore.release()
