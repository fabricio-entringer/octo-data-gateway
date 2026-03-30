import pytest
from app.core.cache_config import CacheSettings


class TestCacheSettings:

    def test_defaults(self):
        settings = CacheSettings.from_env()
        assert settings.redis_url == "redis://localhost:6379/0"
        assert settings.ttl_bitcoin_price == 30
        assert settings.ttl_bitcoin_prices == 30
        assert settings.ttl_bitcoin_balance == 300
        assert settings.ttl_bitcoin_sources == 3600
        assert settings.ttl_email_validate == 86400
        assert settings.ttl_iban_validate == 86400

    def test_env_overrides(self, monkeypatch):
        monkeypatch.setenv("REDIS_URL", "redis://myhost:6380/1")
        monkeypatch.setenv("CACHE_TTL_BITCOIN_PRICE", "60")
        monkeypatch.setenv("CACHE_TTL_BITCOIN_PRICES", "90")
        monkeypatch.setenv("CACHE_TTL_BITCOIN_BALANCE", "600")
        monkeypatch.setenv("CACHE_TTL_BITCOIN_SOURCES", "7200")
        monkeypatch.setenv("CACHE_TTL_EMAIL_VALIDATE", "3600")
        monkeypatch.setenv("CACHE_TTL_IBAN_VALIDATE", "43200")

        settings = CacheSettings.from_env()
        assert settings.redis_url == "redis://myhost:6380/1"
        assert settings.ttl_bitcoin_price == 60
        assert settings.ttl_bitcoin_prices == 90
        assert settings.ttl_bitcoin_balance == 600
        assert settings.ttl_bitcoin_sources == 7200
        assert settings.ttl_email_validate == 3600
        assert settings.ttl_iban_validate == 43200

    def test_is_frozen(self):
        settings = CacheSettings.from_env()
        with pytest.raises((AttributeError, TypeError)):
            settings.ttl_bitcoin_price = 999  # type: ignore
