from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder

from app.api.bitcoin.service import BitcoinService
from app.core.models import ErrorDetail
from app.database.models import Scopes
from .schema import BitcoinPriceListResponse, BitcoinPriceResponse
from app.core.security import require_scopes
from app.core.custom_exception import OctoDataException, ErrorCode, ErrorCategory
from app.core.logging_config import Logger
from app.core.context import request_metadata_var
from fastapi.responses import JSONResponse
    
router = APIRouter()
logger = Logger.get_logger()
service = BitcoinService()

@router.get("/price", 
            response_model=BitcoinPriceResponse,
            dependencies=[Depends(require_scopes([Scopes.BITCOIN]))]
)
async def get_bitcoin_price(currency: Optional[str] = Query(default="USD", 
                                                            max_length=3, 
                                                            description="Currency to get the Bitcoin price in (default: USD)"),
                            source: str = Query(default="Binance",
                                                           description="Source to get the Bitcoin price from (default: Binance)"),
                            accept_cache: Optional[bool] = Query(default=True,
                                                                  description="Whether to accept cached responses (default: True)"),
                            ) -> BitcoinPriceResponse:
        
        logger.info("Request received for Bitcoin price", extra={
            "currency": currency,
            "source": source,
            "accept_cache": accept_cache
        })
        metadata = request_metadata_var.get()
        try:
            
            bitcoin_price = service.get_bitcoin_price(source, currency)
            logger.info("Bitcoin price fetched successfully", extra={
                "bitcoin_price_data": bitcoin_price.model_dump() if hasattr(bitcoin_price, "model_dump") else str(bitcoin_price)
            })
            return BitcoinPriceResponse(
                bitcoin_price=bitcoin_price,
                metadata=metadata.finish_successful_request()
            )
        
        except OctoDataException as e:
            logger.error("OctoDataException caught in get_bitcoin_price", extra={"error": e.for_log()})
            return JSONResponse(
                status_code=e.http_status,
                content=jsonable_encoder(BitcoinPriceResponse(metadata=metadata.finish_failed_request(e)))
            )
    


@router.get("/prices", 
            response_model=BitcoinPriceListResponse,
            dependencies=[Depends(require_scopes([Scopes.BITCOIN]))]
)
async def get_bitcoin_price_list(currency: Optional[str] = Query(default="USD", 
                                                            max_length=3, 
                                                            description="Currency to get the Bitcoin price in (default: USD)"),
                                accept_cache: Optional[bool] = Query(default=True,
                                                                  description="Whether to accept cached responses (default: True)"),
                                ) -> BitcoinPriceListResponse:
        
        logger.info("Request received for Bitcoin price", extra={
            "currency": currency,
            "accept_cache": accept_cache
        })
        metadata = request_metadata_var.get()
        try:
            bitcoin_price_list, exceptions = service.get_bitcoin_price_list(currency)
            if exceptions:
                errors_info = ErrorDetail(
                    error_code=ErrorCode.PARTIAL_CONTENT.code,
                    error_message="Partial content: some sources failed.",
                    error_details=str(exceptions),
                    category=ErrorCategory.SYSTEM
                )
            
            logger.info("Bitcoin price list fetched successfully", extra={
                "bitcoin_price_data": bitcoin_price_list,
                "exceptions": exceptions
            })

            
            return JSONResponse(
                 status_code=206 if exceptions else 200,
                 content=jsonable_encoder(BitcoinPriceListResponse(
                     bitcoin_price_list=bitcoin_price_list,
                     metadata=metadata.finish_successful_request(errors_info if exceptions else None)
                 ))
            )
        
        except OctoDataException as e:
            logger.error("OctoDataException caught in get_bitcoin_price", extra={"error": e.for_log()})
            return JSONResponse(
                status_code=e.http_status,
                content=jsonable_encoder(BitcoinPriceResponse(metadata=metadata.finish_failed_request(e)))
            )


@router.get("/sources", 
            response_model=list[str],
            dependencies=[Depends(require_scopes([Scopes.BITCOIN]))]
)
async def get_bitcoin_sources() -> list[str]:
    """
    Get the list of available Bitcoin price sources.
    """
    return service.get_bitcoin_sources()