import requests

from app.core.custom_exception import ErrorCode, OctoDataException

class RestBaseMixin:
    BASE_HEADERS = {
        'User-Agent': 'OctoDataGateway/1.0',
        'Accept': 'application/json',
    }

    def get(self, url, params=None, headers=None, timeout=10):
        
        try:
            final_headers = self.BASE_HEADERS.copy()
            if headers:
                final_headers.update(headers)
            response = requests.get(url, params=params, headers=final_headers, timeout=timeout)
            response.raise_for_status()

            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 401:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.UNAUTHORIZED_ACCESS,
                    tech_details=f"Unauthorized access to the API. Response: {response.text}"
                )
            elif response.status_code == 400:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.INVALID_REQUEST,
                    tech_details=f"Invalid parameters pair {params}. Response: {response.text}"
                )
            elif response.status_code == 429:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.QUOTA_EXCEEDED,
                    tech_details=f"API rate limit exceeded. Response: {response.text}"
                )
            else:
                raise OctoDataException.from_error(error_code=ErrorCode.UNKNOWN_NETWORK_ERROR,
                    tech_details=f"API returned status code {response.status_code}. Response: {response.text}",
                    http_status=response.status_code
                )
            
        except requests.exceptions.Timeout:
            raise OctoDataException.from_error(
                error_code=ErrorCode.CONNECTION_TIMEOUT,
                tech_details="Timeout while fetching data from Binance API"
            )
            
        except requests.exceptions.ConnectionError:
            raise OctoDataException.from_error(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                tech_details="Connection error while fetching data from Binance API"
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
        
