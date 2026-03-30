from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.core.cache import CacheClient, get_cache
from app.core.cache_config import cache_settings
from app.core.security import require_scopes
from app.database.models import Scopes
from .schema import Email, EmailResponse
from app.core.logging_config import Logger
from app.core.context import request_metadata_var
from app.core.custom_exception import OctoDataException, ErrorCode
from app.api.email.service import EmailService


router = APIRouter()
logger = Logger.get_logger()

email_service = EmailService()


@router.get("/validate/{email}",
            status_code=200,
            response_model=EmailResponse,
            dependencies=[Depends(require_scopes([Scopes.EMAIL]))]
            )
async def validate_email(
        email: str = Path(...,
                          description="The email address to validate",
                          example="user@example.com"),
        accept_cache: Optional[bool] = Query(default=True,
                                             description="Whether to accept cached responses (default: True)"),
        cache: Optional[CacheClient] = Depends(get_cache),
) -> EmailResponse:
    """
    Validate the given email address.

    - **email**: The email address to validate.
    """
    try:
        logger.info("Request received for email validation", extra={"email": email})
        metadata = request_metadata_var.get()

        if accept_cache and cache:
            key = CacheClient.build_key("email", "validate", {"email": email})
            cached = await cache.get(key)
            if cached:
                metadata.cached_source = True
                return JSONResponse(
                    status_code=200,
                    content=jsonable_encoder(EmailResponse(
                        email=Email(**cached),
                        metadata=metadata.finish_successful_request()
                    ))
                )

        email_result = await email_service.validate_email(email=email)
        is_partial = email_result.smtp_check is False or email_result.valid_domain is False or email_result.valid_format is False

        if cache and accept_cache and not is_partial:
            key = CacheClient.build_key("email", "validate", {"email": email})
            await cache.set(key, email_result.model_dump(mode="json"), cache_settings.ttl_email_validate)

        return JSONResponse(
            status_code=206 if is_partial else 200,
            content=jsonable_encoder(EmailResponse(
                email=email_result,
                metadata=metadata.finish_successful_request()
            )))

    except OctoDataException as e:
        logger.error("OctoDataException caught in validate_email", extra={"error": e.for_log()})
        return JSONResponse(
            status_code=e.http_status,
            content=jsonable_encoder(EmailResponse(metadata=metadata.finish_failed_request(e)))
        )
