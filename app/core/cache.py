import json
import logging
from typing import Any, Optional

from fastapi import Request

from app.core.cache_config import CacheSettings, cache_settings

logger = logging.getLogger(__name__)


class CacheClient:
    def __init__(self, settings: CacheSettings):
        self._settings = settings
        self._redis: Any = None

    async def connect(self) -> None:
        try:
            import redis.asyncio as aioredis

            self._redis = aioredis.from_url(
                self._settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._redis.ping()
            logger.info("Redis connection established", extra={"url": self._settings.redis_url})
        except Exception as e:
            logger.warning(
                "Redis unavailable at startup, caching disabled",
                extra={"error": str(e)},
            )
            self._redis = None

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.aclose()
            self._redis = None
            logger.info("Redis connection closed")

    async def get(self, key: str) -> Optional[Any]:
        if not self._redis:
            return None
        try:
            value = await self._redis.get(key)
            if value is not None:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning("Redis get failed", extra={"key": key, "error": str(e)})
            return None

    async def set(self, key: str, value: Any, ttl: int) -> None:
        if not self._redis:
            return
        try:
            await self._redis.setex(key, ttl, json.dumps(value, default=str))
        except Exception as e:
            logger.warning("Redis set failed", extra={"key": key, "error": str(e)})

    async def delete(self, key: str) -> None:
        if not self._redis:
            return
        try:
            await self._redis.delete(key)
        except Exception as e:
            logger.warning("Redis delete failed", extra={"key": key, "error": str(e)})

    @property
    def is_connected(self) -> bool:
        return self._redis is not None

    @staticmethod
    def build_key(domain: str, operation: str, params: dict) -> str:
        parts = []
        for k, v in sorted(params.items()):
            if isinstance(v, list):
                normalized = ",".join(sorted(str(i).lower() for i in v))
            else:
                normalized = str(v).lower()
            parts.append(f"{k}={normalized}")
        return f"octo:{domain}:{operation}:{('&'.join(parts))}"


def get_cache_client() -> CacheClient:
    return CacheClient(cache_settings)


async def get_cache(request: Request) -> Optional[CacheClient]:
    return getattr(request.app.state, "cache", None)
