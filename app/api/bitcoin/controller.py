from typing import Optional

from fastapi import APIRouter, Body, Depends, Query, Request
from fastapi.encoders import jsonable_encoder

from app.api.bitcoin.service import BitcoinService
from app.core.cache import CacheClient, get_cache
from app.core.cache_config import cache_settings
from app.core.models import ErrorDetail
from app.database.models import Scopes
from .schema import (
    BitcoinBalance,
    BitcoinBalanceRequest,
    BitcoinBalanceResponse,
    BitcoinPrice,
    BitcoinPriceListResponse,
    BitcoinPriceResponse,
)
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
async def get_bitcoin_price(
        currency: Optional[str] = Query(default="USD",
                                        max_length=3,
                                        description="Currency to get the Bitcoin price in (default: USD)"),
        source: str = Query(default="Binance",
                            description="Source to get the Bitcoin price from (default: Binance)"),
        accept_cache: Optional[bool] = Query(default=True,
                                             description="Whether to accept cached responses (default: True)"),
        cache: Optional[CacheClient] = Depends(get_cache),
) -> BitcoinPriceResponse:
    logger.info("Request received for Bitcoin price", extra={
        "currency": currency,
        "source": source,
        "accept_cache": accept_cache
    })
    metadata = request_metadata_var.get()

    if accept_cache and cache:
        key = CacheClient.build_key("bitcoin", "price", {"currency": currency, "source": source})
        cached = await cache.get(key)
        if cached:
            metadata.cached_source = True
            return BitcoinPriceResponse(
                bitcoin_price=BitcoinPrice(**cached),
                metadata=metadata.finish_successful_request()
            )

    try:
        bitcoin_price = service.get_bitcoin_price(source, currency)
        logger.info("Bitcoin price fetched successfully", extra={
            "bitcoin_price_data": bitcoin_price.model_dump() if hasattr(bitcoin_price, "model_dump") else str(bitcoin_price)
        })

        if cache and accept_cache:
            key = CacheClient.build_key("bitcoin", "price", {"currency": currency, "source": source})
            await cache.set(key, bitcoin_price.model_dump(mode="json"), cache_settings.ttl_bitcoin_price)

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
async def get_bitcoin_price_list(
        currency: Optional[str] = Query(default="USD",
                                        max_length=3,
                                        description="Currency to get the Bitcoin price in (default: USD)"),
        accept_cache: Optional[bool] = Query(default=True,
                                             description="Whether to accept cached responses (default: True)"),
        cache: Optional[CacheClient] = Depends(get_cache),
) -> BitcoinPriceListResponse:
    logger.info("Request received for Bitcoin prices", extra={
        "currency": currency,
        "accept_cache": accept_cache
    })
    metadata = request_metadata_var.get()

    if accept_cache and cache:
        key = CacheClient.build_key("bitcoin", "prices", {"currency": currency})
        cached = await cache.get(key)
        if cached:
            metadata.cached_source = True
            return JSONResponse(
                status_code=200,
                content=jsonable_encoder(BitcoinPriceListResponse(
                    bitcoin_price_list=[BitcoinPrice(**p) for p in cached],
                    metadata=metadata.finish_successful_request()
                ))
            )

    try:
        bitcoin_price_list, exceptions = service.get_bitcoin_price_list(currency)
        errors_info = None
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

        if cache and accept_cache and not exceptions:
            key = CacheClient.build_key("bitcoin", "prices", {"currency": currency})
            await cache.set(
                key,
                [p.model_dump(mode="json") for p in bitcoin_price_list],
                cache_settings.ttl_bitcoin_prices
            )

        return JSONResponse(
            status_code=206 if exceptions else 200,
            content=jsonable_encoder(BitcoinPriceListResponse(
                bitcoin_price_list=bitcoin_price_list,
                metadata=metadata.finish_successful_request(errors_info)
            ))
        )

    except OctoDataException as e:
        logger.error("OctoDataException caught in get_bitcoin_price_list", extra={"error": e.for_log()})
        return JSONResponse(
            status_code=e.http_status,
            content=jsonable_encoder(BitcoinPriceResponse(metadata=metadata.finish_failed_request(e)))
        )


@router.get("/sources",
            response_model=list[str],
            dependencies=[Depends(require_scopes([Scopes.BITCOIN]))]
            )
async def get_bitcoin_sources(
        cache: Optional[CacheClient] = Depends(get_cache),
) -> list[str]:
    """Get the list of available Bitcoin price sources."""
    if cache:
        key = CacheClient.build_key("bitcoin", "sources", {})
        cached = await cache.get(key)
        if cached:
            return cached

    sources = service.get_bitcoin_sources()

    if cache:
        key = CacheClient.build_key("bitcoin", "sources", {})
        await cache.set(key, sources, cache_settings.ttl_bitcoin_sources)

    return sources


@router.post("/balance",
             response_model=BitcoinBalanceResponse,
             dependencies=[Depends(require_scopes([Scopes.BITCOIN]))]
             )
async def get_bitcoin_balance(
        balance_request: BitcoinBalanceRequest = Body(...,
                                                      description="Request body for getting Bitcoin balance",
                                                      example={
                                                          "addresses": [
                                                              "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                                                              "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"
                                                          ],
                                                          "fiat_currency": "USD",
                                                          "accept_cache": True
                                                      }),
        cache: Optional[CacheClient] = Depends(get_cache),
) -> BitcoinBalanceResponse:
    logger.info("Request received for Bitcoin balance", extra={
        "addresses": balance_request.addresses,
        "fiat_currency": balance_request.fiat_currency,
        "accept_cache": balance_request.accept_cache
    })
    metadata = request_metadata_var.get()

    if balance_request.accept_cache and cache:
        key = CacheClient.build_key("bitcoin", "balance", {
            "addresses": balance_request.addresses,
            "fiat_currency": balance_request.fiat_currency,
        })
        cached = await cache.get(key)
        if cached:
            metadata.cached_source = True
            return JSONResponse(
                status_code=200,
                content=jsonable_encoder(BitcoinBalanceResponse(
                    balance=BitcoinBalance(**cached),
                    metadata=metadata.finish_successful_request()
                ))
            )

    try:
        balance_list, exceptions = service.get_bitcoin_balance(
            balance_request.addresses, balance_request.fiat_currency
        )
        errors_info = None
        if exceptions:
            errors_info = ErrorDetail(
                error_code=ErrorCode.PARTIAL_CONTENT.code,
                error_message="Partial content: some sources failed.",
                error_details=str(exceptions),
                category=ErrorCategory.SYSTEM
            )

        logger.info("Bitcoin balance fetched successfully", extra={
            "balance_data": balance_list,
            "exceptions": exceptions
        })

        if cache and balance_request.accept_cache and balance_list and not exceptions:
            key = CacheClient.build_key("bitcoin", "balance", {
                "addresses": balance_request.addresses,
                "fiat_currency": balance_request.fiat_currency,
            })
            await cache.set(key, balance_list.model_dump(mode="json"), cache_settings.ttl_bitcoin_balance)

        return JSONResponse(
            status_code=206 if exceptions else 200,
            content=jsonable_encoder(BitcoinBalanceResponse(
                balance=balance_list if balance_list else None,
                metadata=metadata.finish_successful_request(errors_info)
            ))
        )

    except OctoDataException as e:
        logger.error("OctoDataException caught in get_bitcoin_balance", extra={"error": e.for_log()})
        return JSONResponse(
            status_code=e.http_status,
            content=jsonable_encoder(BitcoinBalanceResponse(metadata=metadata.finish_failed_request(e)))
        )
