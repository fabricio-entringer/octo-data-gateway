
from fastapi import Depends, HTTPException, status, Query
from app.database import user_database
from app.database.models import Scopes
from app.core.logging_config import Logger
from app.core.context import request_metadata_var
from fastapi import Request
from fastapi.security import APIKeyHeader
from typing import Optional

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

logger = Logger.get_logger()

async def _extract_api_key(request: Request, header_key: Optional[str] = Depends(api_key_header), query_key: Optional[str] = Query(None, alias="api_key")) -> str:
    """Extract API key from header or query parameter. Header takes precedence."""
    api_key = header_key or query_key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Provide via X-API-KEY header or ?api_key= query parameter",
        )
    return api_key

async def get_api_user(scopes: list[Scopes], request: Request, api_key: str = Depends(api_key_header)):
    """Make sure the API key is valid and return the associated user. For API routes (header-only)."""
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

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

    if user.is_valid is False:
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
    return user


async def get_api_user_admin(scopes: list[Scopes], request: Request, api_key: str = Depends(_extract_api_key)):
    """Make sure the API key is valid and return the associated user. For admin routes (header or query)."""

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

    if user.is_valid is False:
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
    return user


def require_scopes(required_scopes: list[Scopes]):
    """
    Creates a dependency function that requires specific scopes.
    For API routes - uses header-only authentication.
    """
    async def _check_scopes(request: Request, api_key: str = Depends(api_key_header)):
        await get_api_user(required_scopes, request, api_key)

    return _check_scopes


def require_scopes_admin(required_scopes: list[Scopes]):
    """
    Creates a dependency function that requires specific scopes for admin routes.
    Accepts API key from both X-API-KEY header OR ?api_key= query parameter.
    """
    async def _check_scopes_admin(request: Request, api_key: str = Depends(_extract_api_key)):
        await get_api_user_admin(required_scopes, request, api_key)

    return _check_scopes_admin