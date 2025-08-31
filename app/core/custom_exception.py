import json
from typing import Optional
from enum import Enum

class ErrorCategory(str, Enum):
    NETWORK = "NETWORK"
    AUTHENTICATION = "AUTHENTICATION"
    DATA_VALIDATION = "DATA_VALIDATION"
    RATE_LIMIT = "RATE_LIMIT"
    SYSTEM = "SYSTEM"
    SERVICE = "SERVICE"

    def __str__(self):
        return self.value
    def __repr__(self):
        return f"ErrorCategory.{self.value}"

class ErrorCode(Enum):
    # Data-related errors
    INVALID_DATA = ("EAG-DAT-001", "The data provided is invalid.", ErrorCategory.DATA_VALIDATION, 400)
    RESPONSE_PARSING_ERROR = ("EAG-DAT-002", "Error occurred while parsing the response.", ErrorCategory.DATA_VALIDATION, 400)
    INVALID_RESPONSE = ("EAG-DAT-003", "The API response is invalid.", ErrorCategory.DATA_VALIDATION, 502)
    DATA_NOT_FOUND = ("EAG-DAT-004", "The requested data was not found.", ErrorCategory.DATA_VALIDATION, 404)
    # General errors
    INTERNAL_SERVER_ERROR = ("EAG-SYS-001", "An internal server error occurred.", ErrorCategory.SYSTEM, 500)
    # Network errors
    UNKNOWN_NETWORK_ERROR = ("EAG-NET-001", "An unknown network error occurred.", ErrorCategory.NETWORK, 502)
    CONNECTION_TIMEOUT = ("EAG-NET-003", "Connection timeout while fetching data. Please try again.", ErrorCategory.NETWORK, 504)
    NETWORK_ERROR = ("EAG-NET-004", "General network error occurred while accessing external service.", ErrorCategory.NETWORK, 502)
    # Service errors
    QUOTA_EXCEEDED = ("EAG-RATE-001", "The provider API rate limit has been exceeded.", ErrorCategory.RATE_LIMIT, 429)
    # Invalid request errors
    INVALID_REQUEST = ("EAG-REQ-001", "The request made is invalid.", ErrorCategory.DATA_VALIDATION, 400)
    MISSING_PARAMETER = ("EAG-REQ-002", "A required parameter is missing.", ErrorCategory.DATA_VALIDATION, 400)
    # Service errors
    SERVICE_UNAVAILABLE = ("EAG-SYS-002", "The service is currently unavailable.", ErrorCategory.SYSTEM, 503)
    # Authentication errors
    UNAUTHORIZED_ACCESS = ("EAG-AUTH-001", "Unauthorized access to the resource.", ErrorCategory.AUTHENTICATION, 401)
    FORBIDDEN_ACCESS = ("EAG-AUTH-002", "Forbidden access to the resource.", ErrorCategory.AUTHENTICATION, 403)
    RESOURCE_NOT_FOUND = ("EAG-AUTH-003", "The requested resource was not found.", ErrorCategory.AUTHENTICATION, 404)
    # Partial success
    PARTIAL_CONTENT = ("EAG-SYS-003", "Partial content: some sources failed.", ErrorCategory.SYSTEM, 206)


    @property
    def code(self):
        return self.value[0]

    @property
    def message(self):
        return self.value[1]

    @property
    def category(self):
        return self.value[2]
    
    @property
    def http_status(self):
        return self.value[3]
    
    def __str__(self):
        return self.code
    
    def __repr__(self):
        return f"ErrorCode.{self.code}"

class OctoDataException(Exception):
    code: str
    error_message: str
    tech_details: Optional[str]
    category: ErrorCategory
    http_status: int

    def __init__(self, code: str, error_message: str, tech_details: Optional[str], category: ErrorCategory, http_status: int):
        self.code = code
        self.error_message = error_message
        self.tech_details = tech_details
        self.category = category
        self.http_status = http_status
    
    @classmethod
    def from_error(cls, error_code: ErrorCode, tech_details: Optional[str] = None, http_status: int = None):
        return cls(
            code=error_code.code,
            error_message=error_code.message,
            tech_details=tech_details,
            category=error_code.category,
            http_status=http_status if http_status is not None else error_code.http_status
        )
    
    def __str__(self):
        tech_details_formatted = self.tech_details.replace('"', '"') if self.tech_details else 'N/A'
        return (
            f"[{self.code}] - {self.error_message}, "
            f"Category: {self.category}, "
            f"HTTP Status: {self.http_status}, "
            f"Technical Details: {tech_details_formatted}"
        )
    
    def __repr__(self):
        tech_details_formatted = self.tech_details.replace('"', '"') if self.tech_details else 'N/A'
        return f"OctoDataException(code={self.code}, message={self.error_message}, tech_details={tech_details_formatted}, category={self.category}, http_status={self.http_status})"
    
    def for_log(self):
        return json.loads(json.dumps(self.__dict__))

