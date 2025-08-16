import requests
from typing import Dict

from app.api.bitcoin.service import BitcoinProcessor
from app.core.custom_exception import EAGCustomException, ErrorCode


class BinancePriceSpot(BitcoinProcessor):
    """
    Binance implementation of the BitcoinProcessor to fetch the current Bitcoin price.
    """
    
    BASE_URL = "https://api.binance.com/api/v3"
    PROVIDER_NAME = "Binance"

    def get_bitcoin_price_external(self, currency: str = "USDT") -> Dict:
        """
        Fetch the current Bitcoin price from the Binance API.
        
        Args:
            currency (str): The target currency (default: USDT)
            
        Returns:
            dict: Response from Binance API containing price information
            
        Raises:
            BitcoinException: If the API request fails or returns invalid data
        """
        try:
            if currency == "USD":
                # Binance uses USDT as the stablecoin equivalent to USD
                currency = "USDT"

            # Construct the symbol (BTC + currency pair)
            symbol = f"BTC{currency}"
            
            url = f"{self.BASE_URL}/ticker/price"
            params = {"symbol": symbol}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate the response structure
                if "symbol" in data and "price" in data:
                    return {
                        "symbol": data["symbol"],
                        "price": float(data["price"]),
                        "currency": currency,
                        "source": self.get_source_name(),  
                    }
                else:
                    raise EAGCustomException.from_error(
                        error_code=ErrorCode.INVALID_RESPONSE,
                        tech_details=f"Invalid response format from Binance API: {data}. The typical response should contain 'symbol' and 'price'.",
                        http_status=response.status_code
                    )
                
            elif response.status_code == 400:
                raise EAGCustomException.from_error(
                    error_code=ErrorCode.INVALID_REQUEST,
                    tech_details=f"Invalid currency pair BTC{currency}. Response: {response.text}"
                )
                 
            elif response.status_code == 429:
                raise EAGCustomException.from_error(
                    error_code=ErrorCode.QUOTA_EXCEEDED,
                    tech_details=f"API rate limit exceeded. Response: {response.text}"
                )
            else:
                raise EAGCustomException.from_error(error_code=ErrorCode.UNKNOWN_NETWORK_ERROR,
                    tech_details=f"API returned status code {response.status_code}. Response: {response.text}",
                    http_status=response.status_code
                )
            
        except requests.exceptions.Timeout:
            raise EAGCustomException.from_error(
                error_code=ErrorCode.CONNECTION_TIMEOUT,
                tech_details="Timeout while fetching data from Binance API"
            )
            
        except requests.exceptions.ConnectionError:
            raise EAGCustomException.from_error(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                tech_details="Connection error while fetching data from Binance API"
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
            str: The name of the source (Binance)
        """
        return self.PROVIDER_NAME
