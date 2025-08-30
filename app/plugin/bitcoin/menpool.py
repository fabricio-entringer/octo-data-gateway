import requests
from app.core.custom_exception import OctoDataException, ErrorCode
from app.plugin.processor import PluginProcessor

class MempoolPriceSpot(PluginProcessor):
    """
    Mempool.space implementation of the PluginProcessor to fetch the current Bitcoin price.
    """

    BASE_URL = "https://mempool.space/api/v1"
    PROVIDER_NAME = "Mempool.space"

    def get_bitcoin_price_external(self, params: dict) -> dict:
        """
        Fetch the current Bitcoin price from the Mempool.space API.

        Args:
            params (dict): The parameters for the API request, including the target currency.

        Returns:
            dict: Response from Mempool.space API containing price information

        Raises:
            OctoDataException: If the API request fails or returns invalid data
        """
        
        try:
            currency = params.get("currency", "EUR").upper()
            url = f"{self.BASE_URL}/prices"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
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
                        http_status=response.status_code
                    )

            elif response.status_code == 401:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.UNAUTHORIZED_ACCESS,
                    tech_details=f"Unauthorized access to Mempool.space API. Response: {response.text}"
                )
            elif response.status_code == 400:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.INVALID_REQUEST,
                    tech_details=f"Invalid request to Mempool.space API. Response: {response.text}"
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
                tech_details="Timeout while fetching data from Mempool.space API"
            )

        except requests.exceptions.ConnectionError:
            raise OctoDataException.from_error(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                tech_details="Connection error while fetching data from Mempool.space API"
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
            str: The name of the source (Mempool.space)
        """
        return self.PROVIDER_NAME
        return self.PROVIDER_NAME
