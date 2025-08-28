
from pydantic import Field
from typing import Optional, List

from app.core.models import Metadata, ReprMixin
from app.database.models import User


class UserResponse(ReprMixin):
    user_data: Optional[User] = Field(None, description="The user data")
    metadata: Metadata = Field(..., description="Metadata about the API request and response")

class UserListResponse(ReprMixin):
    users: List[User] = Field(default_factory=list, description="The user data")
    metadata: Metadata = Field(..., description="Metadata about the API request and response")    