"""Integration tests for endpoint caching using fakeredis."""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.cache import CacheClient
from app.core.cache_config import CacheSettings


SETTINGS = CacheSettings(
    redis_url="redis://localhost:6379/0",
    ttl_bitcoin_price=30,
    ttl_bitcoin_prices=30,
    ttl_bitcoin_balance=300,
    ttl_bitcoin_sources=3600,
    ttl_email_validate=86400,
    ttl_iban_validate=86400,
)


class TestCacheClientWithFakeRedis:
    """Integration tests using fakeredis as the backend."""

    @pytest.mark.asyncio
    async def test_set_then_get_returns_same_value(self):
        try:
            import fakeredis.aioredis as fake_aioredis
        except ImportError:
            pytest.skip("fakeredis not available")

        client = CacheClient(SETTINGS)
        client._redis = fake_aioredis.FakeRedis(decode_responses=True)

        await client.set("test:key", {"price": 50000.0, "currency": "usd"}, 60)
        result = await client.get("test:key")

        assert result == {"price": 50000.0, "currency": "usd"}

    @pytest.mark.asyncio
    async def test_cache_miss_returns_none(self):
        try:
            import fakeredis.aioredis as fake_aioredis
        except ImportError:
            pytest.skip("fakeredis not available")

        client = CacheClient(SETTINGS)
        client._redis = fake_aioredis.FakeRedis(decode_responses=True)

        result = await client.get("nonexistent:key")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_removes_key(self):
        try:
            import fakeredis.aioredis as fake_aioredis
        except ImportError:
            pytest.skip("fakeredis not available")

        client = CacheClient(SETTINGS)
        client._redis = fake_aioredis.FakeRedis(decode_responses=True)

        await client.set("delete:me", {"data": 1}, 60)
        assert await client.get("delete:me") is not None

        await client.delete("delete:me")
        assert await client.get("delete:me") is None

    @pytest.mark.asyncio
    async def test_keys_are_independent(self):
        try:
            import fakeredis.aioredis as fake_aioredis
        except ImportError:
            pytest.skip("fakeredis not available")

        client = CacheClient(SETTINGS)
        client._redis = fake_aioredis.FakeRedis(decode_responses=True)

        await client.set("octo:bitcoin:price:currency=usd&source=binance", {"price": 50000.0}, 60)
        await client.set("octo:bitcoin:price:currency=eur&source=binance", {"price": 47000.0}, 60)

        usd = await client.get("octo:bitcoin:price:currency=usd&source=binance")
        eur = await client.get("octo:bitcoin:price:currency=eur&source=binance")

        assert usd["price"] == 50000.0
        assert eur["price"] == 47000.0

    @pytest.mark.asyncio
    async def test_list_values_are_cached(self):
        try:
            import fakeredis.aioredis as fake_aioredis
        except ImportError:
            pytest.skip("fakeredis not available")

        client = CacheClient(SETTINGS)
        client._redis = fake_aioredis.FakeRedis(decode_responses=True)

        prices = [
            {"price": 50000.0, "currency": "usd", "source": "binance"},
            {"price": 50100.0, "currency": "usd", "source": "coinbase"},
        ]
        await client.set("octo:bitcoin:prices:currency=usd", prices, 30)
        result = await client.get("octo:bitcoin:prices:currency=usd")

        assert len(result) == 2
        assert result[0]["source"] == "binance"
        assert result[1]["source"] == "coinbase"
