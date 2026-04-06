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
        self._ttl_overrides: dict[str, int] = {}

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

    def get_ttl_config(self) -> dict[str, int]:
        base = {
            "bitcoin_price": self._settings.ttl_bitcoin_price,
            "bitcoin_prices": self._settings.ttl_bitcoin_prices,
            "bitcoin_balance": self._settings.ttl_bitcoin_balance,
            "bitcoin_sources": self._settings.ttl_bitcoin_sources,
            "email_validate": self._settings.ttl_email_validate,
            "iban_validate": self._settings.ttl_iban_validate,
        }
        base.update(self._ttl_overrides)
        return base

    def get_ttl(self, endpoint: str) -> int:
        if endpoint in self._ttl_overrides:
            return self._ttl_overrides[endpoint]
        attr = f"ttl_{endpoint}"
        return getattr(self._settings, attr, 60)

    def set_ttl(self, endpoint: str, ttl_seconds: int) -> None:
        self._ttl_overrides[endpoint] = ttl_seconds

    async def flush(self, endpoint: Optional[str] = None) -> int:
        if not self._redis:
            return 0
        try:
            if endpoint:
                pattern = f"octo:{endpoint}:*"
                keys = []
                async for key in self._redis.scan_iter(match=pattern):
                    keys.append(key)
                if not keys:
                    pattern = f"octo:*:{endpoint}:*"
                    async for key in self._redis.scan_iter(match=pattern):
                        keys.append(key)
                if keys:
                    return await self._redis.delete(*keys)
                return 0
            else:
                return await self._redis.flushdb()
        except Exception as e:
            logger.warning("Redis flush failed", extra={"error": str(e)})
            return 0

    async def get_cache_stats(self) -> dict:
        result = {"total_keys": 0, "memory_used": "N/A", "connected": self.is_connected, "endpoint_counts": {}}
        if not self._redis:
            return result
        try:
            db_size = await self._redis.dbsize()
            result["total_keys"] = db_size
            info = await self._redis.info("memory")
            result["memory_used"] = info.get("used_memory_human", "N/A")
            result["memory_used_bytes"] = info.get("used_memory", 0)

            prefixes = ["bitcoin", "email", "iban"]
            for prefix in prefixes:
                count = 0
                async for _ in self._redis.scan_iter(match=f"octo:{prefix}:*"):
                    count += 1
                if count > 0:
                    result["endpoint_counts"][prefix] = count
        except Exception as e:
            logger.warning("Redis stats failed", extra={"error": str(e)})
        return result

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
