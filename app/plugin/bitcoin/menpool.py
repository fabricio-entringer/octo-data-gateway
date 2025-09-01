
from app.core.custom_exception import OctoDataException, ErrorCode
from app.plugin.processor import PluginProcessor
from app.plugin.rest_base_mixin import RestBaseMixin

class MempoolPriceSpot(PluginProcessor, RestBaseMixin):
    """
    Mempool.space implementation of the PluginProcessor to fetch the current Bitcoin price.
    """

    BASE_URL = "https://mempool.space/api/v1"
    PROVIDER_NAME = "Mempool.space"

    def plugin_execute(self, params: dict) -> dict:
        try:
            currency = params.get("currency", "EUR").upper()
            url = f"{self.BASE_URL}/prices"
            
            data = self.get(url, params=params)
            # Expected format: {"USD": price, "EUR": price, ...}
            if currency in data:
                return {
                    "symbol": f"BTC{currency}",
                    "price": float(data[currency]),
                    "currency": currency,
                    "source": self.get_source_name(),
                }
            else:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.INVALID_RESPONSE,
                    tech_details=f"Currency '{currency}' not found in Mempool.space API response: {data}.",
                )

        except Exception as e:
            if isinstance(e, OctoDataException):
                raise e  # Re-raise custom exceptions

            raise OctoDataException.from_error(error_code=ErrorCode.INTERNAL_SERVER_ERROR, tech_details=str(e))
        

    def get_source_name(self) -> str:
        """
        Returns the name of the source for Bitcoin price data.

        Returns:
            str: The name of the source (Mempool.space)
        """
        return self.PROVIDER_NAME
        return self.PROVIDER_NAME
