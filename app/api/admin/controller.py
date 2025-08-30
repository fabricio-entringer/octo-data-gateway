
from fastapi import APIRouter, Body, Depends, Path, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.core.custom_exception import OctoDataException
from app.core.security import require_scopes
from app.database.models import Scopes, User
from app.core.logging_config import Logger
from app.core.context import request_metadata_var
from app.api.admin.service import UserService
from app.api.admin.schema import UserResponse, UserListResponse


router = APIRouter()
logger = Logger.get_logger()
user_service = UserService()

@router.post("/users", 
             status_code=201,
             dependencies=[Depends(require_scopes([Scopes.ADMIN, Scopes.MASTER]))])
async def add_user(user: User = Body(..., 
                                     description="User data to be added",
                                     media_type="application/json",
                                     example={
                                        "name": "John Doe",
                                        "description": "A sample user",
                                        "email": "john.doe@example.com",
                                        "scopes": [Scopes.ADMIN, Scopes.BITCOIN],
                                        "api_key_expires_at": "2023-10-01T12:00:00Z"
                                     } 
                )) -> UserResponse:

    logger.info("Adding user", extra={"user_data": user.model_dump()})
    try:
        
        metadata = request_metadata_var.get()
        user = user_service.add_user(user)
        logger.info("User added successfully", extra={"user_data": user.model_dump()})
        return UserResponse(user_data=user, metadata=metadata.finish_successful_request())

    except OctoDataException as e:
            logger.error("OctoDataException caught in add_user", extra={"error": e.for_log()})
            return JSONResponse(
                status_code=e.http_status,
                content=jsonable_encoder(UserResponse(metadata=metadata.finish_failed_request(e)))
            )

    except Exception as e:
        logger.error("Unexpected error caught in add_user", extra={"error": str(e)})
        raise e


@router.get("/users/{user_id}", 
            status_code=200,
            response_model=UserResponse,
            dependencies=[Depends(require_scopes([Scopes.ADMIN, Scopes.MASTER]))])
async def get_user(user_id: str = Path(..., 
                                        description="The ID of the user to retrieve",
                                        example="123e4567-e89b-12d3-a456-426614174000")) -> UserResponse:

    logger.info("Retrieving user", extra={"user_id": user_id})
    try:
        metadata = request_metadata_var.get()
        user = user_service.get_user_by_id(user_id)
        logger.info("User retrieved successfully", extra={"user_data": user.model_dump()})
        return UserResponse(user_data=user, metadata=metadata.finish_successful_request())

    except OctoDataException as e:
        logger.error("OctoDataException caught in get_user", extra={"error": e.for_log()})
        return JSONResponse(
            status_code=e.http_status,
            content=jsonable_encoder(UserResponse(metadata=metadata.finish_failed_request(e)))
        )


@router.delete("/users/{user_id}", 
               status_code=202,
               response_model=UserResponse,
            dependencies=[Depends(require_scopes([Scopes.ADMIN, Scopes.MASTER]))])
async def delete_user(user_id: str = Path(..., 
                                          description="The ID of the user to delete",
                                          example="123e4567-e89b-12d3-a456-426614174000")):

    logger.info("Deleting user", extra={"user_id": user_id})
    try:
        metadata = request_metadata_var.get()
        user_service.delete_user(user_id)
        logger.info("User deleted successfully", extra={"user_id": user_id})
        return JSONResponse(
            status_code=202,
            content=jsonable_encoder(UserResponse(metadata=metadata.finish_successful_request()))
        )
    except OctoDataException as e:
            logger.error("OctoDataException caught in delete_user", extra={"error": e.for_log()})
            return JSONResponse(
                status_code=e.http_status,
                content=jsonable_encoder(UserResponse(metadata=metadata.finish_failed_request(e)))
            )


@router.put("/users/{user_id}", 
            status_code=200,
            response_model=UserResponse,
            dependencies=[Depends(require_scopes([Scopes.ADMIN, Scopes.MASTER]))])
async def update_user(user_id: str = Path(..., 
                                          description="The ID of the user to update",
                                          example="123e4567-e89b-12d3-a456-426614174000"), 
                        user: User = Body(..., 
                                            description="User data to be added",
                                            media_type="application/json",
                                            example={
                                                "name": "John Doe",
                                                "description": "A sample user",
                                                "email": "john.doe@example.com",
                                                "scopes": [Scopes.ADMIN, Scopes.BITCOIN],
                                                "api_key_expires_at": "2023-10-01T12:00:00Z"
                                            } )) -> UserResponse:
    
    logger.info("Updating user", extra={"user_id": user_id, "user_data": user.model_dump()})
    try:
        
        metadata = request_metadata_var.get()
        user = user_service.update_user(user_id, user)
        logger.info("User updated successfully", extra={"user_data": user.model_dump()})
        return UserResponse(user_data=user, metadata=metadata.finish_successful_request())
    
    except OctoDataException as e:
            logger.error("OctoDataException caught in update_user", extra={"error": e.for_log()})
            return JSONResponse(
                status_code=e.http_status,
                content=jsonable_encoder(UserResponse(metadata=metadata.finish_failed_request(e)))
            )

@router.get("/users",
            response_model=UserListResponse,
            dependencies=[Depends(require_scopes([Scopes.ADMIN, Scopes.MASTER]))],
            status_code=200)
async def list_users() -> UserListResponse:
    
    logger.info("Listing users")
    try:
        metadata = request_metadata_var.get()
        users = user_service.get_all_users()
        logger.info("Users retrieved successfully", extra={"user_count": len(users)})
        return UserListResponse(users=users, metadata=metadata.finish_successful_request())

    except Exception as e:
        logger.error("Unexpected error caught in list_users", extra={"error": str(e)})
        raise e
    
@router.post("/users/{user_id}/renew", 
             status_code=200,
             response_model=UserResponse,
             dependencies=[Depends(require_scopes([Scopes.ADMIN, Scopes.MASTER]))])
async def renew_api_key(user_id: str = Path(..., 
                                          description="The user ID for whom to renew the API key",
                                          example="123e4567-e89b-12d3-a456-426614174000"), 
                        days_valid: int = Body(30, 
                                            description="Number of days the new API key will be valid for",
                                            example=30),
                        expires_at: str = Body(None,
                                            description="Exact expiration date for the new API key in 'DD/MM/YYYY HH:MM:SS' format",
                                            example="31/12/2023 23:59:59")) -> UserResponse:
    
    logger.info("Renewing API key", extra={"user_id": user_id, "days_valid": days_valid, "expires_at": expires_at})
    try:
        metadata = request_metadata_var.get()
        user = user_service.renew_api_key(user_id, days_valid, expires_at)
        logger.info("API key renewed successfully", extra={"user_id": user_id})
        return UserResponse(user_data=user, metadata=metadata.finish_successful_request())
    
    except OctoDataException as e:
            logger.error("OctoDataException caught in renew_api_key", extra={"error": e.for_log()})
            return JSONResponse(
                status_code=e.http_status,
                content=jsonable_encoder({"metadata": metadata.finish_failed_request(e)})
            )
