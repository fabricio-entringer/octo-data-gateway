
from fastapi import Depends, HTTPException, status
from app.database import user_database
from app.database.models import Scopes
from ..log.logging_config import Logger
from app.core.context import request_metadata_var
from fastapi import Request
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME)

logger = Logger.get_logger()

async def get_api_user(scopes: list[Scopes], request: Request, api_key: str = Depends(api_key_header)):
    """Make sure the API key is valid and return the associated user ID."""

    api_key = request.headers.get(API_KEY_NAME)
    
    logger.info("Validating API key")
    metadata = request_metadata_var.get()
    user = user_database.get_user_by_api_key(api_key)

    if user is None:
        logger.warning("Invalid API key. Http 401 Unauthorized", extra={
            "api_key": api_key,
            "http_status": status.HTTP_401_UNAUTHORIZED
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

    metadata.user_id = user.user_id

    if user.api_key_expires_at and user.api_key_expires_at < metadata.timestamp_request_received:
        logger.warning("API key expired. Http 401 Unauthorized", extra={
            "api_key": api_key,
            "http_status": status.HTTP_401_UNAUTHORIZED
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key has expired. It has expired on {}, please request a new one.".format(user.api_key_expires_at),
        )

    if not any(scope in user.scopes for scope in scopes):
        logger.warning("Insufficient permissions. Http 403 Forbidden", extra={
            "required_scopes": [str(s) for s in scopes],
            "user_scopes": [str(s) for s in user.scopes],
            "http_status": status.HTTP_403_FORBIDDEN
        })
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. You do not have access to this resource.",
        )
    
    logger.info("API key validated successfully", extra={"scopes": [str(s) for s in user.scopes]})


def require_scopes(required_scopes: list[Scopes]):
    """
    Creates a dependency function that requires specific scopes.
    This is a dependency factory that returns a proper async dependency function.
    """
    async def _check_scopes(request: Request, api_key: str = Depends(api_key_header)):
        await get_api_user(required_scopes, request, api_key)

    return _check_scopes