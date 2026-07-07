"""Minimal in-memory rate limiter.

This is intentionally simple: a fixed-window counter per key, kept in
process memory. It's enough to blunt naive brute-force attempts against
/auth/login in development and small single-instance deployments.

It is NOT sufficient for a multi-instance production deployment (each
process has its own counters). The seam is deliberately isolated here so
swapping this for a Redis-backed limiter (e.g. `slowapi` + Redis) later is
a one-file change - nothing calling `check_rate_limit` needs to change.
"""

import time
from collections import defaultdict

from app.core.exceptions import AppError
from fastapi import status


class RateLimitExceededError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "rate_limit_exceeded"

    def __init__(self, detail: str = "Too many requests. Please try again later."):
        super().__init__(detail)


_hits: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(key: str, max_requests: int, window_seconds: int) -> None:
    """Raises RateLimitExceededError if `key` has exceeded `max_requests`
    within the trailing `window_seconds`. Call this at the top of sensitive
    endpoints (login, register, refresh) keyed by e.g. client IP or email."""
    now = time.monotonic()
    window_start = now - window_seconds
    hits = [t for t in _hits[key] if t > window_start]
    hits.append(now)
    _hits[key] = hits
    if len(hits) > max_requests:
        raise RateLimitExceededError()
