import requests
from typing import Dict

from app.api.bitcoin.service import BitcoinProcessor
from app.api.bitcoin.bitcoin_exception import BitcoinError, BitcoinException


class BinancePriceSpot(BitcoinProcessor):
    """
    Binance implementation of the BitcoinProcessor to fetch the current Bitcoin price.
    """
    
    BASE_URL = "https://api.binance.com/api/v3"
    
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
            
            # Make the API call to Binance
            url = f"{self.BASE_URL}/ticker/price"
            params = {"symbol": symbol}
            
            print(f"Fetching Bitcoin price from Binance for symbol: {symbol}")
            response = requests.get(url, params=params, timeout=10)
            print(f"Response status code: {response.status_code}")


            # Check if the request was successful
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
                    raise BitcoinException.from_error(
                        BitcoinError.DATA_NOT_AVAILABLE,
                        tech_details=f"Invalid response format from Binance API: {data}"
                    )
                    
            elif response.status_code == 400:
                # Handle invalid symbol or bad request
                raise BitcoinException.from_error(
                    BitcoinError.INVALID_CURRENCY,
                    tech_details=f"Invalid currency pair BTC{currency}. Response: {response.text}"
                )
                
            elif response.status_code == 429:
                # Handle rate limiting
                raise BitcoinException.from_error(
                    BitcoinError.RATE_LIMIT_EXCEEDED,
                    tech_details=f"Binance API rate limit exceeded. Response: {response.text}"
                )
                
            else:
                # Handle other HTTP errors
                raise BitcoinException.from_error(
                    BitcoinError.NETWORK_ERROR,
                    tech_details=f"Binance API returned status code {response.status_code}. Response: {response.text}"
                )
                
        except requests.exceptions.Timeout:
            raise BitcoinException.from_error(
                BitcoinError.NETWORK_ERROR,
                tech_details="Timeout occurred while connecting to Binance API"
            )
            
        except requests.exceptions.ConnectionError:
            raise BitcoinException.from_error(
                BitcoinError.NETWORK_ERROR,
                tech_details="Failed to connect to Binance API"
            )
            
        except requests.exceptions.RequestException as e:
            raise BitcoinException.from_error(
                BitcoinError.NETWORK_ERROR,
                tech_details=f"Request error occurred: {str(e)}"
            )
            
        except ValueError as e:
            # Handle JSON parsing errors
            raise BitcoinException.from_error(
                BitcoinError.DATA_NOT_AVAILABLE,
                tech_details=f"Failed to parse JSON response from Binance API: {str(e)}"
            )
            
        except Exception as e:
            # Handle any other unexpected errors
            raise BitcoinException.from_error(
                BitcoinError.DATA_NOT_AVAILABLE,
                tech_details=f"Unexpected error occurred: {str(e)}"
            )


    def get_source_name(self) -> str:
        """
        Returns the name of the source for Bitcoin price data.
        
        Returns:
            str: The name of the source (Binance)
        """
        return "Binance"
