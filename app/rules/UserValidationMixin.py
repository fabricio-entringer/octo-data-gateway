from datetime import datetime
from app.core.custom_exception import EAGCustomException, ErrorCode
from app.database.models import User
from app.database import user_database
from app.database.models import Scopes


class UserValidationMixin:

    def validate_api_key_expired(self, user: User) -> None:
        """
        Validate if the user's API key is still valid based on the expiration date.
        Raises an EAGCustomException if the API key has expired.
        """
        if user.api_key_expires_at and user.api_key_expires_at < datetime.now():
            raise EAGCustomException.from_error(
                error_code=ErrorCode.FORBIDDEN_ACCESS,
                tech_details="User's API key has expired."
            )

    def validate_user_name_already_exists(self, name: str) -> None:
        """
        Validate if a user with the given name already exists.
        Raises an EAGCustomException if a user with the same name is found.
        """
        if user_database.get_user_by_name(name) is not None:
            raise EAGCustomException.from_error(
                error_code=ErrorCode.INVALID_DATA,
                tech_details=f"User with name {name} already exists."
            )

    def validate_user_email_already_exists(self, email: str) -> None:
        """
        Validate if a user with the given email already exists.
        Raises an EAGCustomException if a user with the same email is found.
        """
        if user_database.get_user_by_email(email) is not None:
            raise EAGCustomException.from_error(
                error_code=ErrorCode.INVALID_DATA,
                tech_details=f"User with email {email} already exists."
            )

    def validate_scopes_not_empty_and_valid(self, scopes: list[str]) -> None:
        """
        Validate that the scopes list is not empty and contains only valid scopes.
        Raises an EAGCustomException if the scopes list is empty or contains invalid scopes.
        """
        
        if not scopes:
            raise EAGCustomException.from_error(
                error_code=ErrorCode.INVALID_DATA,
                tech_details="Scopes list cannot be empty."
            )
        
        valid_scopes = {scope.value for scope in Scopes}
        invalid_scopes = [scope for scope in scopes if scope not in valid_scopes]
        
        if invalid_scopes:
            raise EAGCustomException.from_error(
                error_code=ErrorCode.INVALID_DATA,
                tech_details=f"Invalid scopes found: {', '.join(invalid_scopes)}. Valid scopes are: {', '.join(valid_scopes)}."
            )