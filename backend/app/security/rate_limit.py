"""Simple in-memory per-IP rate limiting for mutating endpoints."""

import threading
import time
from collections import defaultdict
from collections.abc import Callable

from fastapi import Depends, HTTPException, Request

from app.config import settings


class _RateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._hits: dict[str, list[float]] = defaultdict(list)

    def clear(self) -> None:
        with self._lock:
            self._hits.clear()

    def allow(self, key: str, limit: int, window_seconds: float) -> bool:
        now = time.monotonic()
        window_start = now - window_seconds

        with self._lock:
            bucket = self._hits[key]
            # Prune stale hits in-place.
            bucket[:] = [hit for hit in bucket if hit >= window_start]
            if len(bucket) >= limit:
                return False
            bucket.append(now)
            return True


rate_limiter = _RateLimiter()


def _error(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


def rate_limit_dependency(scope: str) -> Callable[..., None]:
    def _check(request: Request) -> None:
        if not settings.RATE_LIMIT_ENABLED:
            return

        client_host = request.client.host if request.client else "unknown"
        key = f"{scope}:{client_host}"
        if not rate_limiter.allow(
            key=key,
            limit=settings.RATE_LIMIT_PER_MINUTE,
            window_seconds=60.0,
        ):
            raise HTTPException(
                status_code=429,
                detail=_error(
                    code="rate_limited",
                    message="Too many requests. Please retry shortly.",
                ),
            )

    return _check


MutatingRateLimit = Depends(rate_limit_dependency("mutating"))
