
from asyncio.log import logger

from app.database.models import User
from app.database import user_database
from app.core.custom_exception import EAGCustomException, ErrorCode
from app.rules.UserValidationMixin import UserValidationMixin
from datetime import datetime, timedelta

class UserService(UserValidationMixin):

    def add_user(self, user: User) -> User:
        """
        Add a new user to the system after validating the input data.
        """
        
        self.validate_user_name_already_exists(user.name)
        self.validate_user_email_already_exists(user.email)
        self.validate_scopes_not_empty_and_valid(user.scopes)

        return user_database.add_user(user)


    def get_all_users(self) -> list[User]:
        """
        Retrieve all users from the system.
        """
        return user_database.get_all_users()


    def get_user_by_id(self, user_id: str) -> User:
        """
        Retrieve a user by their ID.
        """
        user = user_database.get_user(user_id)
        if user is None:
            raise EAGCustomException.from_error(
                error_code=ErrorCode.DATA_NOT_FOUND,
                tech_details=f"User with ID {user_id} not found"
            )
        return user


    def delete_user(self, user_id: str) -> None:
        """
        Delete a user by their ID.
        """
        user = user_database.get_user(user_id)
        if user is None:
            raise EAGCustomException.from_error(
                error_code=ErrorCode.DATA_NOT_FOUND,
                tech_details=f"User with ID {user_id} not found"
            )
        user_database.delete_user(user_id)


    def update_user(self, user_id: str, user_update: User) -> User:
        
        existing_user = user_database.get_user(user_id)
        if existing_user is None:
            raise EAGCustomException.from_error(
                error_code=ErrorCode.DATA_NOT_FOUND,
                tech_details=f"User with ID {user_id} not found"
            )
        
        if user_update.name and user_update.name != existing_user.name:
            self.validate_user_name_already_exists(user_update.name)
            existing_user.name = user_update.name

        if user_update.email and user_update.email != existing_user.email:
            self.validate_user_email_already_exists(user_update.email)
            existing_user.email = user_update.email

        if user_update.description is not None:
            existing_user.description = user_update.description

        if user_update.api_key_expires_at is not None:
            existing_user.api_key_expires_at = user_update.api_key_expires_at

        if user_update.scopes:
            self.validate_scopes_not_empty_and_valid(user_update.scopes)
            existing_user.scopes = user_update.scopes
       
        return user_database.update_user(user_id, existing_user)

    def renew_api_key(self, user_id: str, days_valid: int, expires_at: str) -> User:
        """
        Renew the API key for a user by their ID.
        """
        user = user_database.get_user(user_id)
        if user is None:
            raise EAGCustomException.from_error(
                error_code=ErrorCode.DATA_NOT_FOUND,
                tech_details=f"User with ID {user_id} not found"
            )
        
        if expires_at is not None:
            try:
                user.api_key_expires_at = datetime.strptime(expires_at, "%d/%m/%Y %H:%M:%S")
            except ValueError:
                raise EAGCustomException.from_error(
                    error_code=ErrorCode.INVALID_DATA,
                    tech_details=f"Invalid expires_at format: {expires_at}. Expected 'DD/MM/YYYY HH:MM:SS' format."
                )
        elif days_valid is not None:
            user.api_key_expires_at = datetime.now() + timedelta(days=days_valid)      

        return user_database.update_user(user_id, user)