from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


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
    scopes: list[Scopes] = Field(default_factory=list, 
        description="The list of scopes for the user"
    )

    def __str__(self):
        return f"User({self.user_id}, {self.name})"

    def __repr__(self):
        return self.__str__()
