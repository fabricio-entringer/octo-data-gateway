
from app.core.custom_exception import OctoDataException, ErrorCode
from app.plugin.processor import PluginProcessor
from app.plugin.rest_base_mixin import RestBaseMixin

class KrakenPriceSpot(PluginProcessor, RestBaseMixin):
    """
    Kraken implementation of the PluginProcessor to fetch the current Bitcoin price.
    """

    BASE_URL = "https://api.kraken.com/0/public"
    PROVIDER_NAME = "Kraken"

    def plugin_execute(self, params: dict) -> dict:
        try:
            # Kraken's pair for BTC/USD is XXBTZUSD
            currency = params.get("currency", "USD").upper()
            pair = "XXBTZ" + currency
            url = f"{self.BASE_URL}/Ticker"
            params = {"pair": pair}

            data = self.get(url, params=params)
            # Expected format: {"result": {"XXBTZEUR": {"c": ["price", ...], ...}}, ...}
            result = data.get("result", {})
            ticker = result.get(pair, {})
            price_list = ticker.get("c", [])
            if price_list and len(price_list) > 0:
                return {
                    "symbol": "BTC" + currency,
                    "price": float(price_list[0]),
                    "currency": currency,
                    "source": self.get_source_name(),
                }
            else:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.INVALID_RESPONSE,
                    tech_details=f"Invalid response format from Kraken API: {data}. The typical response should contain 'result' with '{pair}' and 'c' (last trade closed price).",
                )

        except Exception as e:
            if isinstance(e, OctoDataException):
                raise e  # Re-raise custom exceptions

            raise OctoDataException.from_error(error_code=ErrorCode.INTERNAL_SERVER_ERROR, tech_details=str(e))


    def get_source_name(self) -> str:
        """
        Returns the name of the source for Bitcoin price data.

        Returns:
            str: The name of the source (Kraken)
        """
        return self.PROVIDER_NAME
