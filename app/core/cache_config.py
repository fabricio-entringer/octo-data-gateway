import os
from dataclasses import dataclass


@dataclass(frozen=True)
class CacheSettings:
    redis_url: str
    ttl_bitcoin_price: int
    ttl_bitcoin_prices: int
    ttl_bitcoin_balance: int
    ttl_bitcoin_sources: int
    ttl_email_validate: int
    ttl_iban_validate: int

    @classmethod
    def from_env(cls) -> "CacheSettings":
        return cls(
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            ttl_bitcoin_price=int(os.getenv("CACHE_TTL_BITCOIN_PRICE", "30")),
            ttl_bitcoin_prices=int(os.getenv("CACHE_TTL_BITCOIN_PRICES", "30")),
            ttl_bitcoin_balance=int(os.getenv("CACHE_TTL_BITCOIN_BALANCE", "300")),
            ttl_bitcoin_sources=int(os.getenv("CACHE_TTL_BITCOIN_SOURCES", "3600")),
            ttl_email_validate=int(os.getenv("CACHE_TTL_EMAIL_VALIDATE", "86400")),
            ttl_iban_validate=int(os.getenv("CACHE_TTL_IBAN_VALIDATE", "86400")),
        )


cache_settings = CacheSettings.from_env()
