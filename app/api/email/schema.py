
from typing import Optional
from pydantic import BaseModel, Field

from app.core.models import Metadata


class Email(BaseModel):
    email: str = Field(..., 
        description="The email address",
        max_length=255,
        examples=["user@example.com"]
    )
    valid_format: bool = Field(..., 
        description="Indicates if the email format is valid"
    )
    valid_domain: bool = Field(..., 
        description="Indicates if the email domain is valid"
    )
    smtp_check: bool = Field(..., 
        description="Indicates if the SMTP check was successful"
    )

class EmailResponse(BaseModel):
    email: Optional[Email] = Field(None, description="The validated email information")
    metadata: Metadata = Field(..., description="Metadata about the API request and response")