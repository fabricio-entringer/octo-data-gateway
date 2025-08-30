from pydantic import BaseModel, computed_field
from pydantic import Field
from datetime import datetime
from typing import Optional, TypeVar
import uuid
import importlib.metadata

from .custom_exception import OctoDataException, ErrorCode

T = TypeVar("T", bound=BaseModel)

class ReprMixin(BaseModel):
    def __repr__(self):
        # Usa model_dump() para Pydantic v2, dict() para v1
        try:
            data = self.model_dump()
        except AttributeError:
            data = self.dict()
        return f"{self.__class__.__name__}({data})"

    def __str__(self):
        return self.__repr__()

class ErrorDetail(BaseModel):
    error_code: str = Field(..., 
        description="Error code representing the type of error.", 
        pattern=r"^EAG-[A-Z]{2,10}-\d{3}$",
        examples=["EAG-NET-001", "EAG-AUTH-002"]
    )
    error_message: str = Field(..., 
        description="Human-readable error message.",
        examples=["Network error occurred", "Authentication failed"]
    )
    error_details: str = Field(None, 
        description="Additional details about the error.",
        examples=["Timeout occurred while fetching data", "Invalid token provided"]
    )
    category: str = Field(..., 
        description="Category of the error (e.g., NETWORK, AUTHENTICATION).",
        examples=["NETWORK", "AUTHENTICATION"]
    )

class Metadata(BaseModel):
    user_id: str = Field(None, 
        description="Unique identifier for the user making the request.",
        examples=["user_123", "user_456"]
    )
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), 
        description="Unique identifier for the request.",
        examples=["123e4567-e89b-12d3-a456-426614174000", "f47ac10b-58cc-4372-a567-0e02b2c3d479"]
    )
    timestamp_request_received: datetime = Field(default_factory=datetime.now, 
        description="Timestamp when the request was received.",
        examples=["2023-01-01T12:00:00Z", "2023-01-01T12:00:00Z"]
    )
    timestamp_response_sent: datetime = Field(default_factory=datetime.now, 
        description="Timestamp when the response was sent.",
        examples=["2023-01-01T12:00:00Z", "2023-01-01T12:00:00Z"]
    )
    api_version: str = Field("v1", 
        description="Version of the API used for the request.",
        examples=["v1", "v2"]
    )
    error_info: ErrorDetail = Field(None, 
        description="Detailed error information if the request failed."
    )
    cached_source: bool = Field(False, 
        description="Indicates if the result came from cache."
    )
    path: Optional[str] = Field(None, 
        description="The path of the API endpoint being accessed.",
        examples=["/users", "/products"]
    )

    @computed_field
    @property
    def is_successful(self) -> bool:
        """
        Indicates if the request was successful based on the status code.
        """
        return self.error_info is None or self.error_info.error_code == ErrorCode.PARTIAL_CONTENT.code
    
    @computed_field
    @property
    def processing_time_ms(self) -> float:
        """
        Returns the processing time in milliseconds.
        """
        return (self.timestamp_response_sent - self.timestamp_request_received).total_seconds() * 1000
    
    @computed_field
    @property
    def app_version(self) -> str:
        """
        Returns the application version.
        """

        return importlib.metadata.version("external-data-gateway")
    
    def finish_successful_request(self, error_info: ErrorDetail = None):
        """
        Marks the request as successful and sets the response timestamp.
        """

        self.error_info = error_info
        self.timestamp_response_sent = datetime.now()
        return self
    
    def finish_failed_request(self, ex: OctoDataException):
        """
        Marks the request as failed and sets the error message.
        """

        self.error_info = ErrorDetail(
            error_code=ex.code,
            error_message=ex.error_message,
            error_details=ex.tech_details,
            category=ex.category.name
        )

        self.timestamp_response_sent = datetime.now()
        return self

    
