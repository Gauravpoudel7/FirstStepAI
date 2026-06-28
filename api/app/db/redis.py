"""Async Redis client for rate limiting + future pubsub."""
from __future__ import annotations

import redis.asyncio as aioredis

from app.config import get_settings

settings = get_settings()

_redis: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    """Return a process-wide async Redis client (lazy-initialized)."""
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
    return _redis
