from typing import List, Optional
from pydantic import Field
from app.core.models import Metadata, ReprMixin

class BitcoinPrice(ReprMixin):
    price: float = Field(..., 
        description="The current price of Bitcoin",
        ge=0,
    )
    currency: str = Field("USD", 
        description="The currency of the Bitcoin price",
        max_length=3,
        examples=["USD", "EUR", "GBP"]
    )
    source: Optional[str] = Field(..., 
        description="The source of the Bitcoin price data"
    )

class BitcoinPriceResponse(ReprMixin):
    bitcoin_price: Optional[BitcoinPrice] = Field(None, description="The current price of Bitcoin")
    metadata: Metadata = Field(..., description="Metadata about the API request and response")

class BitcoinPriceListResponse(ReprMixin):
    bitcoin_price_list: List[BitcoinPrice] = Field(default_factory=list, description="List of Bitcoin prices")
    metadata: Metadata = Field(..., description="Metadata about the API request and response")

class FiatAmount(ReprMixin):
    amount: float = Field(..., ge=0, description="The amount in fiat currency")
    currency: str = Field(..., max_length=3, description="The fiat currency code (e.g., USD, EUR)")

class BitcoinBalanceAddress(ReprMixin):
    address: str = Field(..., description="The Bitcoin address")
    balance: float = Field(..., ge=0, description="The balance of the Bitcoin address in BTC")
    fiat_equivalent: Optional[FiatAmount] = Field(None, description="The fiat equivalent of the Bitcoin address balance")
    source: Optional[str] = Field(None, description="The source of the balance data")

class BitcoinBalance(ReprMixin):
    total_balance: float = Field(..., ge=0, description="The total balance of all Bitcoin addresses in BTC")
    total_fiat_equivalent: Optional[FiatAmount] = Field(None, description="The total fiat equivalent of all Bitcoin addresses balance")
    current_price: Optional[BitcoinPrice] = Field(None, description="The current price of Bitcoin")
    addresses: List[BitcoinBalanceAddress] = Field(default_factory=list, description="List of Bitcoin addresses and their balances")

class BitcoinBalanceResponse(ReprMixin):
    balance: Optional[BitcoinBalance] = Field(None, description="The Bitcoin balance information")
    metadata: Metadata = Field(..., description="Metadata about the API request and response")

class BitcoinBalanceRequest(ReprMixin):
    addresses: List[str] = Field(..., description="List of Bitcoin addresses to get the balance for", min_items=1)
    fiat_currency: Optional[str] = Field("USD", max_length=3, description="Fiat currency for balance conversion (default: USD)")
    accept_cache: Optional[bool] = Field(True, description="Whether to accept cached responses (default: True)")