from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder

from app.api.bitcoin import service
from app.database.models import Scopes
from .schema import BitcoinPriceResponse
from app.core.security import require_scopes
from app.core.custom_exception import EAGCustomException
from app.log.logging_config import Logger
from app.core.context import request_metadata_var
from fastapi.responses import JSONResponse
    
router = APIRouter()
logger = Logger.get_logger()

@router.get("/price", 
            response_model=BitcoinPriceResponse,
            dependencies=[Depends(require_scopes([Scopes.BITCOIN]))]
)
async def get_bitcoin_price(currency: Optional[str] = Query(default="USD", 
                                                            max_length=3, 
                                                            description="Currency to get the Bitcoin price in (default: USD)"),
                            source: Optional[str] = Query(default=None,
                                                           description="Source to get the Bitcoin price from (default: binance)"),
                            accept_cache: Optional[bool] = Query(default=True,
                                                                  description="Whether to accept cached responses (default: True)"),
                            ) -> BitcoinPriceResponse:
        """
        Get the current Bitcoin price.
        """
        logger.info("Request received for Bitcoin price", extra={
            "currency": currency,
            "source": source,
            "accept_cache": accept_cache
        })
        try:
            
            metadata = request_metadata_var.get()
            logger.info("Calling service.extract_bitcoin_price", extra={"currency": currency, "source": source})
            bitcoin_price = service.extract_bitcoin_price(currency=currency)
            logger.info("Bitcoin price fetched successfully", extra={
                "bitcoin_price_data": bitcoin_price.model_dump() if hasattr(bitcoin_price, "model_dump") else str(bitcoin_price)
            })
            return BitcoinPriceResponse(
                bitcoin_price=bitcoin_price,
                metadata=metadata.finish_successful_request()
            )
        
        except EAGCustomException as e:
            logger.error("EAGCustomException caught in get_bitcoin_price", extra={"error": e.for_log()})
            return JSONResponse(
                status_code=e.http_status,
                content=jsonable_encoder(BitcoinPriceResponse(metadata=metadata.finish_failed_request(e)))
            )
    
