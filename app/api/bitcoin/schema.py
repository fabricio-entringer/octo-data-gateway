from typing import List, Optional
from pydantic import BaseModel, Field
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