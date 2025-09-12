from app.core.custom_exception import ErrorCode, OctoDataException
from app.plugin.processor import PluginProcessor
from app.plugin.rest_base_mixin import RestBaseMixin


class BlockCypherBalance(PluginProcessor, RestBaseMixin):
    """
    BlockCypher implementation of the PluginProcessor to fetch Bitcoin address balances.
    """
    
    BASE_URL = "https://api.blockcypher.com/v1/btc/main"
    PROVIDER_NAME = "BlockCypher"

    def plugin_execute(self, params: dict) -> dict:
        try:
            address = params.get("address")
            if not address or not isinstance(address, str):
                raise OctoDataException.from_error(
                    error_code=ErrorCode.INVALID_REQUEST,
                    tech_details="The 'address' parameter must be a non-empty string containing a Bitcoin address."
                )

            url = f"{self.BASE_URL}/addrs/{address}/balance"
            data = self.get(url)
            
            if "final_balance" in data:
                balance_btc = data["final_balance"] 
                return {
                    "address": address,
                    "balance": balance_btc,
                    "source": self.get_source_name(),
                }
            else:
                raise OctoDataException.from_error(
                    error_code=ErrorCode.INVALID_RESPONSE,
                    tech_details=f"Invalid response format from BlockCypher API for address {address}: {data}. The typical response should contain 'final_balance'."
                )
        
        except Exception as e:
            if isinstance(e, OctoDataException):
                raise e  # Re-raise custom exceptions
            


    def get_source_name(self) -> str:
        """
        Returns the name of the source for Bitcoin balance data.
        
        Returns:
            str: The name of the source (BlockCypher)
        """
        return self.PROVIDER_NAME