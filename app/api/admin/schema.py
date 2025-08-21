
from pydantic import BaseModel, Field
from typing import Optional

from app.core.models import Metadata
from app.database.models import User


class UserResponse(BaseModel):
    user_data: Optional[User] = Field(None, description="The user data")
    metadata: Metadata = Field(..., description="Metadata about the API request and response")

class UserListResponse(BaseModel):
    users: list[User] = Field(default_factory=list, description="The user data")
    metadata: Metadata = Field(..., description="Metadata about the API request and response")    