
from asyncio.log import logger
from app.database.models import User
from app.database import user_database
from app.core.custom_exception import EAGCustomException, ErrorCode


def add_user(user: User) -> User:
    """
    Add a new user to the system.
    """
    if user_database.get_user_by_name(user.name) is not None:
        raise EAGCustomException.from_error(
                        error_code=ErrorCode.INVALID_DATA,
                        tech_details=f"User with name {user.name} already exists"
                    )

    if user_database.get_user_by_email(user.email) is not None:
        raise EAGCustomException.from_error(
            error_code=ErrorCode.INVALID_DATA,
            tech_details=f"User with email {user.email} already exists"
        )

    return user_database.add_user(user)
