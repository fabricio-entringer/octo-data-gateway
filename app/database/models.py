from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Scopes(str, Enum):
    MASTER = "MASTER"
    ADMIN = "ADMIN"
    BITCOIN = "BITCOIN"
    EXCHANGE_RATES = "EXCHANGE_RATES"

class User(BaseModel):
    user_id: Optional[str] = Field(None, 
        description="The unique identifier for the user"
    )
    name: str = Field(..., 
        description="The name of the user"
    )
    description: Optional[str] = Field(None, 
        description="The description of the user"
    )
    email: Optional[str] = Field(None, 
        description="The email address of the user"
    )
    api_key: Optional[str] = Field(None, 
        description="The API key for the user"
    )
    api_key_expires_at: Optional[datetime] = Field(None, 
        description="The expiration date and time of the API key. Null means it never expires",
        example="2023-10-01T12:00:00Z"
    )
    scopes: list[str] = Field(default_factory=list, 
        description="The list of scopes for the user",
        example=["ADMIN", "BITCOIN"]
    )
    created_at: Optional[datetime] = Field(None, 
        description="The timestamp when the user was created",
        example="2023-10-01T12:00:00Z"
    )
    updated_at: Optional[datetime] = Field(None, 
        description="The timestamp when the user was last updated",
        example="2023-10-01T12:00:00Z"
    )

    def __str__(self):
        return f"User({self.user_id}, {self.name})"

    def __repr__(self):
        return self.__str__()
    
    @property
    def is_master(self) -> bool:
        return Scopes.MASTER in self.scopes

    @property
    def is_admin(self) -> bool:
        return Scopes.ADMIN in self.scopes

    @property
    def has_scope(self, scope: Scopes) -> bool:
        return scope in self.scopes

    @property
    def is_valid(self) -> bool:
        if self.api_key_expires_at is None:
            return True
        return self.api_key_expires_at > datetime.now()
    
    
class UserUsage(BaseModel):
    user_id: str = Field(..., description="The unique identifier for the user")
    timestamp: datetime = Field(..., description="The timestamp of the usage event")
    request_id: str = Field(..., description="The unique identifier for the request")
    endpoint: str = Field(..., description="The API endpoint accessed")
    method: str = Field(..., description="The HTTP method used")
    status_code: int = Field(..., description="The HTTP status code returned")
    response_time_ms: float = Field(..., description="The response time in milliseconds")
    is_success: bool = Field(..., description="Whether the request was successful or not")
