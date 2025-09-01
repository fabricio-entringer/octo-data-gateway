from app.core.custom_exception import OctoDataException, ErrorCode
from app.plugin.processor import PluginProcessor
from app.plugin.rest_base_mixin import RestBaseMixin

class BlockchainPriceSpot(PluginProcessor, RestBaseMixin):
    """
    Blockchain.info implementation of the PluginProcessor to fetch the current Bitcoin price.
    """

    BASE_URL = "https://blockchain.info"
    PROVIDER_NAME = "Blockchain.info"

    def plugin_execute(self, params: dict) -> dict:
        try:
            currency = params.get("currency", "USD").upper()
            url = f"{self.BASE_URL}/ticker"
            
            data = self.get(url, params=params)
            # Expected format: {"USD": {"last": price, ...}, "EUR": {...}, ...}
            if currency in data and "last" in data[currency]:
                return {
                    "symbol": f"BTC{currency}",
                    "price": float(data[currency]["last"]),
                    "currency": currency,
                    "source": self.get_source_name(),
                }
            else:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.INVALID_RESPONSE,
                    tech_details=f"Invalid response format from Blockchain.info API: {data}. The typical response should contain '{currency}' with 'last'.",
                )

        except Exception as e:
            if isinstance(e, OctoDataException):
                raise e  # Re-raise custom exceptions

            raise OctoDataException.from_error(error_code=ErrorCode.INTERNAL_SERVER_ERROR, tech_details=str(e))
        

    def get_source_name(self) -> str:
        """
        Returns the name of the source for Bitcoin price data.

        Returns:
            str: The name of the source (Blockchain.info)
        """
        return self.PROVIDER_NAME
