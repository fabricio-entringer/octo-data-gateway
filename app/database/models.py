from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class Scopes(str, Enum):
    MASTER = "MASTER"
    BITCOIN = "BITCOIN"
    EXCHANGE_RATES = "EXCHANGE_RATES"

class User(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid4()), 
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
    api_key: str = Field(default_factory=lambda: str(uuid4()), 
        description="The API key for the user"
    )
    scopes: list[Scopes] = Field(default_factory=list, 
        description="The list of scopes for the user"
    )

