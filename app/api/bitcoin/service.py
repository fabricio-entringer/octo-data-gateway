from abc import abstractmethod

from app.core.custom_exception import EAGCustomException, ErrorCode
from .schema import BitcoinPrice

class BitcoinProcessor:
    """
    A class to handle Bitcoin-related operations, such as fetching the current price.
    """

    @abstractmethod
    def get_bitcoin_price_external(currency: str) -> dict:
        """
        Abstract method to be implemented by subclasses to fetch the current Bitcoin price.
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """
        Abstract method to return the name of the source for Bitcoin price data.
        """
        pass


bitcoin_processors = []


def extract_bitcoin_price(currency: str = "EUR") -> BitcoinPrice:
    """
    Attempts to fetch the current Bitcoin price in the specified currency using all registered processors.
    Returns:
        BitcoinPrice: The current price of Bitcoin in the specified currency.
    Raises:
        BitcoinException: If all processors fail or return invalid data.
    Notes:
        - Tries each processor in order until one succeeds.
        - If all fail, raises a BitcoinException with details from all sources.
        - Errors from each processor are collected for diagnostics.
    """
    
    exceptions = []
    for processor in bitcoin_processors:
        try:
            result = processor.get_bitcoin_price_external(currency)

            if result is not None and 'price' in result and 'currency' in result:
                return BitcoinPrice(price=result['price'], 
                                    currency=result['currency'][:3], 
                                    source=result.get('source', 'unknown'))
            else:
                exceptions.append({
                    "source": processor.get_source_name(),
                    "error": EAGCustomException.from_error(
                        error_code=ErrorCode.INVALID_RESPONSE,
                        tech_details=f"API returned invalid data: {result}",
                        http_status=502
                    )
                })
                
        except EAGCustomException as e:
            exceptions.append({
                "source": processor.get_source_name(),
                "error": str(e)
            })

        except Exception as e:
            exceptions.append({
                "source": processor.get_source_name(),
                "error": str(e)
            })

        raise EAGCustomException.from_error(
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            tech_details=f"Failed to fetch Bitcoin price from all sources: {exceptions}"
        )
    


# Register plugins when module is imported
def _register_plugins():
    """Register all available Bitcoin plugins."""
    try:
        from app.plugin.bitcoin.router import register_bitcoin_processor
        register_bitcoin_processor(bitcoin_processors)
    except ImportError as e:
        print(f"Warning: Could not register Bitcoin plugins: {e}")


# Auto-register plugins
_register_plugins()