from abc import abstractmethod

from app.api.mixin.processor_by_name import ProcessorByNameMixin
from app.core.custom_exception import OctoDataException, ErrorCode
from .schema import BitcoinBalance, BitcoinBalanceAddress, BitcoinPrice, FiatAmount
from app.plugin.bitcoin.register import bitcoin_price_processors, bitcoin_balance_processors
from app.plugin.processor import PluginProcessor

class BitcoinService(ProcessorByNameMixin):

    def get_bitcoin_sources(self) -> list[str]:
        return [processor.get_source_name() for processor in bitcoin_price_processors]


    def get_bitcoin_price_list(self, currency: str, stop_when_found_first: bool = False) -> tuple[list[BitcoinPrice], list[dict]]:

        results = []
        exceptions = []
        for processor in bitcoin_price_processors:
            try:

                result = self._get_bitcoin_price(processor, currency)
                results.append(result)

                if stop_when_found_first and results:
                    break

            except (OctoDataException, Exception) as e:
                exceptions.append({
                    "source": processor.get_source_name(),
                    "error": str(e)
                })

        if results:
            return results, exceptions
        
        raise OctoDataException.from_error(
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            tech_details=f"Failed to fetch Bitcoin price from all sources: {exceptions}"
        )
        

    def get_bitcoin_price(self, source: str, currency: str) -> BitcoinPrice:

        processor = self.get_processor_by_source_name(bitcoin_price_processors, source)
        result = self._get_bitcoin_price(processor, currency)
        return result
        

    def _get_bitcoin_price(self, processor: PluginProcessor, currency: str) -> BitcoinPrice:
        result = processor.plugin_execute(params={"currency": currency})
        if result is not None and 'price' in result and 'currency' in result:
            return BitcoinPrice(price=result['price'],
                                currency=result['currency'][:3],
                                source=result.get('source', processor.get_source_name()))
        else:
            raise OctoDataException.from_error(
                error_code=ErrorCode.INVALID_RESPONSE,
                tech_details=f"API returned invalid data: {result}"
            )
        
    def get_bitcoin_price_first_available(self, currency: str) -> BitcoinPrice:
        results, exceptions = self.get_bitcoin_price_list(currency, stop_when_found_first=True)
        if results:
            return results[0]
        
        raise OctoDataException.from_error(
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            tech_details=f"Failed to fetch Bitcoin price from all sources: {exceptions}"
        )
        
    def _get_bitcoin_balance_first_available(self, address: str) -> BitcoinBalanceAddress:
        exceptions = []
        for processor in bitcoin_balance_processors:
            try:
                result = processor.plugin_execute(params={"address": address})
                if result is not None and 'address' in result and 'balance' in result:
                    return BitcoinBalanceAddress(
                        address=result['address'],
                        balance=result['balance'],
                        source=result.get('source', processor.get_source_name()),
                        fiat_equivalent=None  # Fiat equivalent can be calculated later if needed
                    )
            except (OctoDataException, Exception) as e:
                exceptions.append({
                    "source": processor.get_source_name(),
                    "error": str(e)
                })
        
        raise OctoDataException.from_error(
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            tech_details=f"Failed to fetch Bitcoin balance from all sources for address {address}: {exceptions}"
        )

    def get_bitcoin_balance(self, addresses: list[str], fiat_currency: str) -> tuple[list[BitcoinBalance], list[dict]]:
        
        bitcoin_addresses = []
        exceptions = []

        for addr in addresses:
            try:
                bitcoin_address_balance = self._get_bitcoin_balance_first_available(addr)
                bitcoin_addresses.append(bitcoin_address_balance)
            except Exception as e:
                exceptions.append({
                    "address": addr,
                    "error": str(e)
                })
                continue

        if not bitcoin_addresses:
            raise OctoDataException.from_error(
                error_code=ErrorCode.DATA_NOT_FOUND,
                tech_details=f"Failed to fetch Bitcoin balance for all provided addresses: {exceptions}"
            )

        bitcoin_price = self.get_bitcoin_price_first_available(fiat_currency)

        if not bitcoin_price:
            raise OctoDataException.from_error(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                tech_details=f"Failed to fetch Bitcoin price for fiat currency {fiat_currency}"
            )
        
        for addr_balance in bitcoin_addresses:
            addr_balance.fiat_equivalent = FiatAmount(amount=addr_balance.balance * bitcoin_price.price, currency=fiat_currency)

        return BitcoinBalance(total_balance=sum(addr.balance for addr in bitcoin_addresses),
                              total_fiat_equivalent=FiatAmount(amount=sum(addr.fiat_equivalent.amount for addr in bitcoin_addresses), currency=fiat_currency) if bitcoin_price else None,
                              current_price=bitcoin_price,
                              addresses=bitcoin_addresses), exceptions if len(bitcoin_addresses) < len(addresses) else None