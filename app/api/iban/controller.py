from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.iban.schema import Iban, IbanResponse
from app.api.iban.service import IbanService
from app.core.cache import CacheClient, get_cache
from app.core.cache_config import cache_settings
from app.core.custom_exception import OctoDataException
from app.core.security import require_scopes
from app.database.models import Scopes
from app.core.logging_config import Logger
from app.core.context import request_metadata_var


router = APIRouter()
iban_service = IbanService()
logger = Logger.get_logger()


@router.get("/validate",
            response_model=IbanResponse,
            status_code=200,
            dependencies=[Depends(require_scopes([Scopes.IBAN]))]
            )
async def validate_iban(
        iban: str = Query(...,
                          description="The IBAN to be validated",
                          example="GB82WEST12345698765432"),
        accept_cache: Optional[bool] = Query(default=True,
                                             description="Whether to accept cached responses (default: True)"),
        cache: Optional[CacheClient] = Depends(get_cache),
):
    """
    Validate an IBAN (International Bank Account Number).

    This endpoint checks the validity of the provided IBAN and returns detailed information
    about it, including country, bank details, and formatting.

    - **iban**: The IBAN to be validated.

    Returns a JSON object containing the validation result and associated metadata.
    """
    logger.info("Request received for IBAN validation", extra={"iban": iban})
    metadata = request_metadata_var.get()

    if accept_cache and cache:
        key = CacheClient.build_key("iban", "validate", {"iban": iban})
        cached = await cache.get(key)
        if cached:
            metadata.cached_source = True
            return IbanResponse(iban=Iban(**cached), metadata=metadata.finish_successful_request())

    try:
        iban_details = iban_service.validate_iban(iban=iban)
        logger.info("IBAN validation successful", extra={"iban": iban, "details": jsonable_encoder(iban_details)})

        if cache and accept_cache:
            key = CacheClient.build_key("iban", "validate", {"iban": iban})
            await cache.set(key, iban_details.model_dump(mode="json"), cache_settings.ttl_iban_validate)

        return IbanResponse(iban=iban_details, metadata=metadata.finish_successful_request())

    except OctoDataException as e:
        logger.error("OctoDataException caught in validate_iban", extra={"error": e.for_log()})
        return JSONResponse(
            status_code=e.http_status,
            content=jsonable_encoder(IbanResponse(metadata=metadata.finish_failed_request(e)))
        )
