
from typing import Optional
from enum import Enum

class ErrorCategory(str, Enum):
    NETWORK = "NETWORK"
    AUTHENTICATION = "AUTHENTICATION"
    DATA_VALIDATION = "DATA_VALIDATION"
    RATE_LIMIT = "RATE_LIMIT"
    SYSTEM = "SYSTEM"
    SERVICE = "SERVICE"

class EAGCustomException(Exception):
    code: str
    error_message: str
    tech_details: Optional[str]
    category: ErrorCategory
    http_status: int
    retryable: bool

    def __init__(self, code: str, error_message: str, tech_details: Optional[str], category: ErrorCategory, http_status: int, retryable: bool):
        self.code = code
        self.error_message = error_message
        self.tech_details = tech_details
        self.category = category
        self.http_status = http_status
        self.retryable = retryable

# Predefined exceptions
class NetworkException(EAGCustomException):
    def __init__(self, code: str, error_message: str, tech_details: str = None):
        super().__init__(
            code=code,
            error_message=error_message,
            tech_details=tech_details,
            category=ErrorCategory.NETWORK,
            http_status=502,
            retryable=True
        )

class AuthenticationException(EAGCustomException):
    def __init__(self, code: str, error_message: str, tech_details: str = None):
        super().__init__(
            code=code,
            error_message=error_message,
            tech_details=tech_details,
            category=ErrorCategory.AUTHENTICATION,
            http_status=401,
            retryable=False
        )

class RateLimitException(EAGCustomException):
    def __init__(self, code: str, error_message: str, tech_details: str = None):
        super().__init__(
            code=code,
            error_message=error_message,
            tech_details=tech_details,
            category=ErrorCategory.RATE_LIMIT,
            http_status=429,
            retryable=True
        )

class ServiceException(EAGCustomException):
    def __init__(self, code: str, error_message: str, tech_details: str = None):
        super().__init__(
            code=code,
            error_message=error_message,
            tech_details=tech_details,
            category=ErrorCategory.SERVICE,
            http_status=500,
            retryable=True
        )

# Specific exceptions
EXTERNAL_API_UNAVAILABLE = NetworkException(
    code="EAG_NET_001",
    error_message="External data service is temporarily unavailable. Please try again later."
)

CONNECTION_TIMEOUT = NetworkException(
    code="EAG_NET_002", 
    error_message="Connection timeout while fetching data. Please try again."
)

INVALID_API_KEY = AuthenticationException(
    code="EAG_AUTH_001",
    error_message="Invalid or missing API credentials."
)

QUOTA_EXCEEDED = RateLimitException(
    code="EAG_RATE_002",
    error_message="Daily quota exceeded. Please try again tomorrow or upgrade your plan."
)
