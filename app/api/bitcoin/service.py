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

def get_bitcoin_sources() -> list[str]:
    return [processor.get_source_name() for processor in bitcoin_processors]


def get_bitcoin_price_list(self, currency: str = "EUR") -> tuple[list[BitcoinPrice], list[dict]]:

    results = []
    exceptions = []
    for processor in bitcoin_processors:
        try:

            result = self._get_bitcoin_price(processor, currency)
            results.append(result)

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

    if results:
        return results, exceptions
    
    raise EAGCustomException.from_error(
        error_code=ErrorCode.SERVICE_UNAVAILABLE,
        tech_details=f"Failed to fetch Bitcoin price from all sources: {exceptions}"
    )
    

def get_bitcoin_price(self, source: str, currency: str = "EUR") -> BitcoinPrice:

    processor = self._get_processor_by_source_name(source)
    result = self._get_bitcoin_price(processor, currency)
    return result
    

def _get_bitcoin_price(processor: BitcoinProcessor, currency: str = "EUR") -> BitcoinPrice:
    result = processor.get_bitcoin_price_external(currency)
    if result is not None and 'price' in result and 'currency' in result:
        return BitcoinPrice(price=result['price'],
                            currency=result['currency'][:3],
                            source=result.get('source', processor.get_source_name()))
    else:
        raise EAGCustomException.from_error(
            error_code=ErrorCode.INVALID_RESPONSE,
            tech_details=f"API returned invalid data: {result}"
        )
    

def _get_processor_by_source_name(source: str) -> BitcoinProcessor:
    processor = next((p for p in bitcoin_processors if p.get_source_name().lower() == source.lower()), None)

    if processor is None:
        raise EAGCustomException.from_error(
            error_code=ErrorCode.INVALID_REQUEST,
            tech_details=f"Source '{source}' not found among registered processors. Available sources: {[p.get_source_name() for p in bitcoin_processors]}"
        )
    
    return processor
    


# Register plugins when module is imported
def _register_plugins():
    """Register all available Bitcoin plugins."""
    try:
        from app.plugin.bitcoin.router import register_all_processors
        register_all_processors(bitcoin_processors)
    except ImportError as e:
        print(f"Warning: Could not register Bitcoin plugins: {e}")


# Auto-register plugins
_register_plugins()