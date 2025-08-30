import requests

from app.core.custom_exception import OctoDataException, ErrorCode
from app.plugin.processor import PluginProcessor

class KrakenPriceSpot(PluginProcessor):
    """
    Kraken implementation of the PluginProcessor to fetch the current Bitcoin price.
    """

    BASE_URL = "https://api.kraken.com/0/public"
    PROVIDER_NAME = "Kraken"

    def get_bitcoin_price_external(self, params: dict) -> dict:
        """
        Fetch the current Bitcoin price from the Kraken API.

        Args:
            params (dict): The parameters for the API request, including the target currency.

        Returns:
            dict: Response from Kraken API containing price information

        Raises:
            OctoDataException: If the API request fails or returns invalid data
        """

        try:

            # Kraken's pair for BTC/USD is XXBTZUSD
            currency = params.get("currency", "USD").upper()
            pair = "XXBTZ" + currency
            url = f"{self.BASE_URL}/Ticker"
            params = {"pair": pair}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
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
                        http_status=response.status_code
                    )

            elif response.status_code == 401:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.UNAUTHORIZED_ACCESS,
                    tech_details=f"Unauthorized access to Kraken API. Response: {response.text}"
                )
            elif response.status_code == 400:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.INVALID_REQUEST,
                    tech_details=f"Invalid request to Kraken API. Response: {response.text}"
                )
            elif response.status_code == 429:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.QUOTA_EXCEEDED,
                    tech_details=f"API rate limit exceeded. Response: {response.text}"
                )
            else:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.UNKNOWN_NETWORK_ERROR,
                    tech_details=f"API returned status code {response.status_code}. Response: {response.text}",
                    http_status=response.status_code
                )

        except requests.exceptions.Timeout:
            raise OctoDataException.from_error(
                error_code=ErrorCode.CONNECTION_TIMEOUT,
                tech_details="Timeout while fetching data from Kraken API"
            )

        except requests.exceptions.ConnectionError:
            raise OctoDataException.from_error(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                tech_details="Connection error while fetching data from Kraken API"
            )

        except requests.exceptions.RequestException as e:
            raise OctoDataException.from_error(
                error_code=ErrorCode.UNKNOWN_NETWORK_ERROR,
                tech_details=str(e)
            )
        except ValueError as e:
            raise OctoDataException.from_error(
                error_code=ErrorCode.RESPONSE_PARSING_ERROR,
                tech_details=str(e)
            )

        except Exception as e:
            if isinstance(e, OctoDataException):
                raise e  # Re-raise custom exceptions

            raise OctoDataException.from_error(
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                tech_details=str(e)
            )

    def get_source_name(self) -> str:
        """
        Returns the name of the source for Bitcoin price data.

        Returns:
            str: The name of the source (Kraken)
        """
        return self.PROVIDER_NAME
