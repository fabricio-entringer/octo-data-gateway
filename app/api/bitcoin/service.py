from abc import abstractmethod

from app.api.bitcoin.bitcoin_exception import BitcoinError, BitcoinException
from app.core.custom_exception import EAGCustomException
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
    Fetches the current Bitcoin price in the specified currency from a public API.
    Returns:
        float: The current price of Bitcoin in the specified currency.
    Raises:
        Exception: If the API request fails or the response is invalid.
    """
    
    try:
        print("Extracting Bitcoin price from registered processors...")
        result = bitcoin_processors[0].get_bitcoin_price_external(currency)

        print(f"Extracted Bitcoin price: {result}")

        if result is not None and 'price' in result and 'currency' in result:
            return BitcoinPrice(price=result['price'], 
                                currency=result['currency'][:3], 
                                source=result.get('source', 'unknown'))
        else:
            raise BitcoinException.from_error(BitcoinError.DATA_NOT_AVAILABLE,
                                              tech_details=f"API returned invalid data: {result}")
        
    except EAGCustomException as e:
        print(f"Error extracting Bitcoin price: {e}")
        raise BitcoinException.from_error(BitcoinError.DATA_NOT_AVAILABLE, tech_details=str(e))
    except Exception as e:
        print(f"Unexpected error extracting Bitcoin price: {e}")
        raise BitcoinException.from_error(BitcoinError.UNEXPECTED_ERROR, tech_details=str(e))


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