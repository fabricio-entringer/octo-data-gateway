
from fastapi import Depends, HTTPException, status
from app.core.models import Metadata
from app.database import user_database
from app.database.models import Scopes
from ..log.logging_config import Logger
from app.core.context import request_metadata_var
from fastapi import Request

API_KEY_NAME = "X-API-KEY"

logger = Logger.get_logger()

async def get_api_user(scopes: list[Scopes], request: Request):
    """Make sure the API key is valid and return the associated user ID."""

    api_key = request.headers.get(API_KEY_NAME)
    path = request.url.path

    logger.info("Validating API key", extra={"path": path})
    metadata = request_metadata_var.get()
    metadata.path = path
    user = user_database.get_user_by_api_key(api_key)

    if user is None:
        logger.warning("Invalid API key. Http 401 Unauthorized", 
                       extra={"api_key": api_key, "http_status": status.HTTP_401_UNAUTHORIZED})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

    metadata.user_id = user.user_id

    if not any(scope in user.scopes for scope in scopes):
        logger.warning("Insufficient permissions. Http 403 Forbidden", 
                       extra={"http_status": status.HTTP_403_FORBIDDEN,
                              "user_scopes": user.scopes,
                              "required_scopes": scopes})
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. You do not have access to this resource.",
        )
    
    logger.info("API key validated successfully", 
                extra={"scopes": user.scopes,
                       "http_status": status.HTTP_200_OK})


def require_scopes(required_scopes: list[Scopes]):
    """
    Creates a dependency function that requires specific scopes.
    This is a dependency factory that returns a proper async dependency function.
    """
    async def _check_scopes(request: Request):
        await get_api_user(required_scopes, request)

    return _check_scopes