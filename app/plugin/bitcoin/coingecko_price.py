
from app.core.custom_exception import OctoDataException, ErrorCode
from app.plugin.processor import PluginProcessor
from app.plugin.rest_base_mixin import RestBaseMixin

class CoinGeckoPriceSpot(PluginProcessor, RestBaseMixin):
    """
    CoinGecko implementation of the PluginProcessor to fetch the current Bitcoin price.
    """

    BASE_URL = "https://api.coingecko.com/api/v3"
    PROVIDER_NAME = "CoinGecko"

    def plugin_execute(self, params: dict) -> dict:
        try:
            currency = params.get("currency", "USD").upper()
            # CoinGecko expects lowercase currency codes
            currency_lower = currency.lower()
            url = f"{self.BASE_URL}/simple/price"
            params = {
                "ids": "bitcoin",
                "vs_currencies": currency_lower
            }

            data = self.get(url, params=params)
            # Expected format: {"bitcoin": {"usd": price}}
            if "bitcoin" in data and currency_lower in data["bitcoin"]:
                return {
                    "symbol": "BTC" + currency,
                    "price": float(data["bitcoin"][currency_lower]),
                    "currency": currency,
                    "source": self.get_source_name(),
                }
            else:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.INVALID_RESPONSE,
                    tech_details=f"Invalid response format from CoinGecko API: {data}. The typical response should contain 'bitcoin' with '{currency_lower}'.",
                )

        except Exception as e:
            if isinstance(e, OctoDataException):
                raise e  # Re-raise custom exceptions

            raise OctoDataException.from_error(error_code=ErrorCode.INTERNAL_SERVER_ERROR, tech_details=str(e))
        

    def get_source_name(self) -> str:
        """
        Returns the name of the source for Bitcoin price data.

        Returns:
            str: The name of the source (CoinGecko)
        """
        return self.PROVIDER_NAME
