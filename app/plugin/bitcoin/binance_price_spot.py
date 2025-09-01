
from app.core.custom_exception import OctoDataException, ErrorCode
from app.plugin.processor import PluginProcessor
from app.plugin.rest_base_mixin import RestBaseMixin


class BinancePriceSpot(PluginProcessor, RestBaseMixin):
    """
    Binance implementation of the PluginProcessor to fetch the current Bitcoin price.
    """
    
    BASE_URL = "https://api.binance.com/api/v3"
    PROVIDER_NAME = "Binance"

    def plugin_execute(self, params: dict) -> dict:
        try:
            currency = params.get("currency", "USD").upper()
            if currency == "USD":
                # Binance uses USDT as the stablecoin equivalent to USD
                currency = "USDT"

            # Construct the symbol (BTC + currency pair)
            symbol = f"BTC{currency}"
            
            url = f"{self.BASE_URL}/ticker/price"
            params = {"symbol": symbol}
        
            data = self.get(url, params=params)
            if "symbol" in data and "price" in data:
                return {
                    "symbol": data["symbol"],
                    "price": float(data["price"]),
                    "currency": currency,
                    "source": self.get_source_name(),  
                }
            else:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.INVALID_RESPONSE,
                    tech_details=f"Invalid response format from Binance API: {data}. The typical response should contain 'symbol' and 'price'."
                )

        
        except Exception as e:
            if isinstance(e, OctoDataException):
                raise e  # Re-raise custom exceptions
            
            raise OctoDataException.from_error(error_code=ErrorCode.INTERNAL_SERVER_ERROR, tech_details=str(e))


    def get_source_name(self) -> str:
        """
        Returns the name of the source for Bitcoin price data.
        
        Returns:
            str: The name of the source (Binance)
        """
        return self.PROVIDER_NAME
