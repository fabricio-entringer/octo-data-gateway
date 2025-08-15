from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.models import Metadata
from app.database import user_database
from app.database.models import Scopes

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME)


async def get_api_user(scopes: list[Scopes], api_key: str = Depends(api_key_header)) -> Metadata:
    """Make sure the API key is valid and return the associated user ID."""

    metadata = Metadata()

    user = user_database.get_user_by_api_key(api_key)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    
    if not any(scope in user.scopes for scope in scopes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. You do not have access to this resource.",
        )

    metadata.user_id = user.user_id

    return metadata


def require_scopes(required_scopes: list[Scopes]):
    """
    Creates a dependency function that requires specific scopes.
    This is a dependency factory that returns a proper async dependency function.
    """
    async def _check_scopes(api_key: str = Depends(api_key_header)) -> Metadata:
        return await get_api_user(required_scopes, api_key)
    
    return _check_scopes