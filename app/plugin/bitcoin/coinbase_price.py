
from app.core.custom_exception import OctoDataException, ErrorCode
from app.plugin.processor import PluginProcessor
from app.plugin.rest_base_mixin import RestBaseMixin

class CoinbasePriceSpot(PluginProcessor, RestBaseMixin):
    """
    Coinbase implementation of the PluginProcessor to fetch the current Bitcoin price.
    """

    BASE_URL = "https://api.coinbase.com/v2"
    PROVIDER_NAME = "Coinbase"

    def plugin_execute(self, params: dict) -> dict:
        try:
            currency = params.get("currency", "USD").upper()
            url = f"{self.BASE_URL}/prices/BTC-{currency}/spot"

            data = self.get(url, params=params)
            # Expected format: {"data": {"base": "BTC", "currency": "USD", "amount": "xxxx.xx"}}
            if "data" in data and "amount" in data["data"]:
                return {
                    "symbol": "BTC" + currency,
                    "price": float(data["data"]["amount"]),
                    "currency": currency,
                    "source": self.get_source_name(),
                }
            else:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.INVALID_RESPONSE,
                    tech_details=f"Invalid response format from Coinbase API: {data}. The typical response should contain 'data' with 'amount'.",
                )

        except Exception as e:
            if isinstance(e, OctoDataException):
                raise e  # Re-raise custom exceptions

            raise OctoDataException.from_error(error_code=ErrorCode.INTERNAL_SERVER_ERROR, tech_details=str(e))

    def get_source_name(self) -> str:
        """
        Returns the name of the source for Bitcoin price data.

        Returns:
            str: The name of the source (Coinbase)
        """
        return self.PROVIDER_NAME
