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


class TestBuildKey:

    def test_simple_params(self):
        key = CacheClient.build_key("bitcoin", "price", {"currency": "USD", "source": "Binance"})
        assert key == "octo:bitcoin:price:currency=usd&source=binance"

    def test_params_are_sorted(self):
        key1 = CacheClient.build_key("bitcoin", "price", {"source": "Binance", "currency": "USD"})
        key2 = CacheClient.build_key("bitcoin", "price", {"currency": "USD", "source": "Binance"})
        assert key1 == key2

    def test_list_param_is_sorted(self):
        key1 = CacheClient.build_key("bitcoin", "balance", {"addresses": ["addr_b", "addr_a"]})
        key2 = CacheClient.build_key("bitcoin", "balance", {"addresses": ["addr_a", "addr_b"]})
        assert key1 == key2

    def test_empty_params(self):
        key = CacheClient.build_key("bitcoin", "sources", {})
        assert key == "octo:bitcoin:sources:"

    def test_values_are_lowercased(self):
        key = CacheClient.build_key("bitcoin", "price", {"currency": "EUR"})
        assert "currency=eur" in key


class TestCacheClient:

    @pytest.mark.asyncio
    async def test_get_returns_none_when_not_connected(self):
        client = CacheClient(SETTINGS)
        result = await client.get("some:key")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_is_noop_when_not_connected(self):
        client = CacheClient(SETTINGS)
        await client.set("some:key", {"value": 1}, 60)  # should not raise

    @pytest.mark.asyncio
    async def test_delete_is_noop_when_not_connected(self):
        client = CacheClient(SETTINGS)
        await client.delete("some:key")  # should not raise

    @pytest.mark.asyncio
    async def test_is_connected_false_when_not_connected(self):
        client = CacheClient(SETTINGS)
        assert client.is_connected is False

    @pytest.mark.asyncio
    async def test_connect_sets_connected_on_success(self):
        client = CacheClient(SETTINGS)
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock()
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            await client.connect()
        assert client.is_connected is True

    @pytest.mark.asyncio
    async def test_connect_handles_redis_unavailable(self):
        client = CacheClient(SETTINGS)
        with patch("redis.asyncio.from_url", side_effect=Exception("Connection refused")):
            await client.connect()  # should not raise
        assert client.is_connected is False

    @pytest.mark.asyncio
    async def test_get_returns_deserialized_value(self):
        client = CacheClient(SETTINGS)
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock()
        mock_redis.get = AsyncMock(return_value='{"price": 50000.0}')
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            await client.connect()
        result = await client.get("test:key")
        assert result == {"price": 50000.0}

    @pytest.mark.asyncio
    async def test_get_returns_none_on_cache_miss(self):
        client = CacheClient(SETTINGS)
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            await client.connect()
        result = await client.get("missing:key")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_returns_none_on_redis_error(self):
        client = CacheClient(SETTINGS)
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock()
        mock_redis.get = AsyncMock(side_effect=Exception("Redis error"))
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            await client.connect()
        result = await client.get("test:key")  # should not raise
        assert result is None

    @pytest.mark.asyncio
    async def test_set_calls_setex_with_ttl(self):
        client = CacheClient(SETTINGS)
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock()
        mock_redis.setex = AsyncMock()
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            await client.connect()
        await client.set("test:key", {"price": 50000.0}, 30)
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "test:key"
        assert call_args[0][1] == 30

    @pytest.mark.asyncio
    async def test_set_handles_redis_error_gracefully(self):
        client = CacheClient(SETTINGS)
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock()
        mock_redis.setex = AsyncMock(side_effect=Exception("Redis error"))
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            await client.connect()
        await client.set("test:key", {"price": 50000.0}, 30)  # should not raise

    @pytest.mark.asyncio
    async def test_disconnect_closes_connection(self):
        client = CacheClient(SETTINGS)
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock()
        mock_redis.aclose = AsyncMock()
        with patch("redis.asyncio.from_url", return_value=mock_redis):
            await client.connect()
        assert client.is_connected is True
        await client.disconnect()
        assert client.is_connected is False
        mock_redis.aclose.assert_called_once()
