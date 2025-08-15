from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.api.bitcoin import service
from app.database.models import Scopes
from .schema import BitcoinPriceResponse
from app.core.models import Metadata
from app.core.security import require_scopes
from app.core.custom_exception import EAGCustomException  # Add this import
    
router = APIRouter()


@router.get("/price", response_model=BitcoinPriceResponse)
async def get_bitcoin_price(currency: Optional[str] = Query(default="USD", 
                                                            max_length=3, 
                                                            description="Currency to get the Bitcoin price in (default: USD)"),
                            source: Optional[str] = Query(default=None,
                                                           description="Source to get the Bitcoin price from (default: binance)"),
                            accept_cache: Optional[bool] = Query(default=True,
                                                                  description="Whether to accept cached responses (default: True)"),
                            metadata: Metadata = Depends(require_scopes([Scopes.BITCOIN]))) -> BitcoinPriceResponse:
    """
    Get the current Bitcoin price.
    """        
    try:
        
        bitcoin_price = service.extract_bitcoin_price()

    except EAGCustomException as e:
        return BitcoinPriceResponse(
            bitcoin_price=None,
            metadata=metadata.finish_failed_request(e)
        )

    return BitcoinPriceResponse(
        bitcoin_price=bitcoin_price,
        metadata=metadata.finish_successful_request()
    )
