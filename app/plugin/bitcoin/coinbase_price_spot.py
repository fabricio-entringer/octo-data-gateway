import requests
from typing import Dict

from app.api.bitcoin.service import BitcoinProcessor
from app.core.custom_exception import EAGCustomException, ErrorCode

class CoinbasePriceSpot(BitcoinProcessor):
    """
    Coinbase implementation of the BitcoinProcessor to fetch the current Bitcoin price.
    """

    BASE_URL = "https://api.coinbase.com/v2"
    PROVIDER_NAME = "Coinbase"

    def get_bitcoin_price_external(self, currency: str = "USD") -> Dict:
        """
        Fetch the current Bitcoin price from the Coinbase API.

        Args:
            currency (str): The target currency (default: USD)

        Returns:
            dict: Response from Coinbase API containing price information

        Raises:
            EAGCustomException: If the API request fails or returns invalid data
        """
        try:
            # if currency != "USD":
            #     raise EAGCustomException.from_error(
            #         error_code=ErrorCode.INVALID_REQUEST,
            #         tech_details=f"Coinbase only supports USD for spot price. Requested: {currency}"
            #     )

            url = f"{self.BASE_URL}/prices/BTC-{currency}/spot"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                # Expected format: {"data": {"base": "BTC", "currency": "USD", "amount": "xxxx.xx"}}
                if "data" in data and "amount" in data["data"]:
                    return {
                        "symbol": "BTC" + currency,
                        "price": float(data["data"]["amount"]),
                        "currency": currency,
                        "source": self.get_source_name(),
                    }
                else:
                    raise EAGCustomException.from_error(
                        error_code=ErrorCode.INVALID_RESPONSE,
                        tech_details=f"Invalid response format from Coinbase API: {data}. The typical response should contain 'data' with 'amount'.",
                        http_status=response.status_code
                    )

            elif response.status_code == 401:
                raise EAGCustomException.from_error(
                    error_code=ErrorCode.UNAUTHORIZED_ACCESS,
                    tech_details=f"Unauthorized access to Coinbase API. Response: {response.text}"
                )
            elif response.status_code == 400:
                raise EAGCustomException.from_error(
                    error_code=ErrorCode.INVALID_REQUEST,
                    tech_details=f"Invalid request to Coinbase API. Response: {response.text}"
                )
            elif response.status_code == 429:
                raise EAGCustomException.from_error(
                    error_code=ErrorCode.QUOTA_EXCEEDED,
                    tech_details=f"API rate limit exceeded. Response: {response.text}"
                )
            else:
                raise EAGCustomException.from_error(
                    error_code=ErrorCode.UNKNOWN_NETWORK_ERROR,
                    tech_details=f"API returned status code {response.status_code}. Response: {response.text}",
                    http_status=response.status_code
                )

        except requests.exceptions.Timeout:
            raise EAGCustomException.from_error(
                error_code=ErrorCode.CONNECTION_TIMEOUT,
                tech_details="Timeout while fetching data from Coinbase API"
            )

        except requests.exceptions.ConnectionError:
            raise EAGCustomException.from_error(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                tech_details="Connection error while fetching data from Coinbase API"
            )

        except requests.exceptions.RequestException as e:
            raise EAGCustomException.from_error(
                error_code=ErrorCode.UNKNOWN_NETWORK_ERROR,
                tech_details=str(e)
            )
        except ValueError as e:
            raise EAGCustomException.from_error(
                error_code=ErrorCode.RESPONSE_PARSING_ERROR,
                tech_details=str(e)
            )

        except Exception as e:
            if isinstance(e, EAGCustomException):
                raise e  # Re-raise custom exceptions

            raise EAGCustomException.from_error(
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                tech_details=str(e)
            )

    def get_source_name(self) -> str:
        """
        Returns the name of the source for Bitcoin price data.

        Returns:
            str: The name of the source (Coinbase)
        """
        return self.PROVIDER_NAME
