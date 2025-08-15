
from enum import Enum
from sys import exception
from app.core.custom_exception import EAGCustomException, ErrorCategory


class BitcoinError(Enum):
    INVALID_ADDRESS = ("EAG_BTC_001", "Invalid Bitcoin address format.")
    DATA_NOT_AVAILABLE = ("EAG_BTC_002", "Bitcoin price data is not available.")
    NETWORK_ERROR = ("EAG_BTC_003", "Failed to connect to Bitcoin API.")
    RATE_LIMIT_EXCEEDED = ("EAG_BTC_004", "Bitcoin API rate limit exceeded.")
    INVALID_CURRENCY = ("EAG_BTC_005", "Unsupported currency for Bitcoin price.")
    UNEXPECTED_ERROR = ("EAG_BTC_999", "An unexpected error occurred while processing Bitcoin data.")

    @property
    def code(self):
        return self.value[0]

    @property
    def message(self):
        return self.value[1]


class BitcoinException(EAGCustomException):
    category: ErrorCategory = ErrorCategory.SERVICE
    http_status: int = 500
    retryable: bool = True

    def __init__(self, error: BitcoinError, tech_details: str = None):
        super().__init__(
            code=error.code,
            error_message=error.message,
            tech_details=tech_details,
            category=self.category,
            http_status=self.http_status,
            retryable=self.retryable
        )

    @classmethod
    def from_error(cls, error: BitcoinError, tech_details: str = None):
        return cls(error=error, tech_details=tech_details)
