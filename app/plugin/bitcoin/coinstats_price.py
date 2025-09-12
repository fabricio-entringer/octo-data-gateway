
from app.core.custom_exception import OctoDataException, ErrorCode
from app.plugin.processor import PluginProcessor
from app.plugin.rest_base_mixin import RestBaseMixin

class CoinStatsPriceSpot(PluginProcessor, RestBaseMixin):
    """
    CoinStats implementation of the PluginProcessor to fetch the current Bitcoin price.
    """

    BASE_URL = "https://openapiv1.coinstats.app"
    PROVIDER_NAME = "CoinStats"

    def plugin_execute(self, params: dict) -> dict:
        try:
            currency = params.get("currency", "EUR").upper()
            url = f"{self.BASE_URL}/coins/bitcoin"
            params = {"currency": currency}

            data = self.get(url, params=params)
            # Expected format: {..., "price": ...}
            if isinstance(data, dict) and "price" in data:
                return {
                    "symbol": f"BTC{currency}",
                    "price": float(data["price"]),
                    "currency": currency,
                    "source": self.get_source_name(),
                }
            else:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.INVALID_RESPONSE,
                    tech_details=f"Invalid response format from CoinStats API: {data}. The typical response should contain 'coin' with 'price'.",
                )

        except Exception as e:
            if isinstance(e, OctoDataException):
                raise e  # Re-raise custom exceptions

            raise OctoDataException.from_error(error_code=ErrorCode.INTERNAL_SERVER_ERROR, tech_details=str(e))


    def get_source_name(self) -> str:
        """
        Returns the name of the source for Bitcoin price data.

        Returns:
            str: The name of the source (CoinStats)
        """
        return self.PROVIDER_NAME
