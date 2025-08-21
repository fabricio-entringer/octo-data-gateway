
from fastapi import APIRouter, Body, Depends, Path, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.core.custom_exception import EAGCustomException
from app.core.security import require_scopes
from app.database.models import Scopes, User
from app.log.logging_config import Logger
from app.core.context import request_metadata_var
from app.api.admin import service
from app.api.admin.schema import UserResponse


router = APIRouter()
logger = Logger.get_logger()

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
                                     } 
                )) -> UserResponse:
    """
    Endpoint to add a new user.
    This is a placeholder implementation.
    """

    logger.info("Adding user", extra={"user_data": user.model_dump()})
    try:
        
        metadata = request_metadata_var.get()
        user = service.add_user(user)
        logger.info("User added successfully", extra={"user_data": user.model_dump()})
        return UserResponse(user_data=user, metadata=metadata.finish_successful_request())

    except EAGCustomException as e:
            logger.error("EAGCustomException caught in add_user", extra={"error": e.for_log()})
            return JSONResponse(
                status_code=e.http_status,
                content=jsonable_encoder(UserResponse(metadata=metadata.finish_failed_request(e)))
            )

    except Exception as e:
        logger.error("Unexpected error caught in add_user", extra={"error": str(e)})
        raise e


@router.get("/users/{user_id}", 
            status_code=200,
            dependencies=[Depends(require_scopes([Scopes.ADMIN, Scopes.MASTER]))])
async def get_user(user_id: str = Path(..., 
                                        description="The ID of the user to retrieve",
                                        example="123e4567-e89b-12d3-a456-426614174000")) -> UserResponse:
    """
    Endpoint to retrieve a user by ID.
    This is a placeholder implementation.
    """
    # Here you would typically retrieve the user from your database
    return {"message": "User retrieved successfully", "user_id": user_id}


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: str):
    """
    Endpoint to delete a user by ID.
    This is a placeholder implementation.
    """
    # Here you would typically delete the user from your database
    return {"message": "User deleted successfully", "user_id": user_id}

@router.put("/users/{user_id}", status_code=200)
async def update_user(user_id: str, new_data: dict):
    """
    Endpoint to update a user's information.
    This is a placeholder implementation.
    """
    # Here you would typically update the user in your database
    return {"message": "User updated successfully", "user_id": user_id, "new_data": new_data}


@router.get("/users", status_code=200)
async def list_users():
    """
    Endpoint to list all users.
    This is a placeholder implementation.
    """
    # Here you would typically retrieve all users from your database
    return {"message": "List of all users"}
