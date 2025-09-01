from abc import abstractmethod

from app.api.mixin.processor_by_name import ProcessorByNameMixin
from app.core.custom_exception import OctoDataException, ErrorCode
from app.plugin import processor
from .schema import BitcoinPrice
from app.plugin.bitcoin.register import bitcoin_processors
from app.plugin.processor import PluginProcessor

class BitcoinService(ProcessorByNameMixin):

    def get_bitcoin_sources(self) -> list[str]:
        return [processor.get_source_name() for processor in bitcoin_processors]


    def get_bitcoin_price_list(self, currency: str = "EUR") -> tuple[list[BitcoinPrice], list[dict]]:

        results = []
        exceptions = []
        for processor in bitcoin_processors:
            try:

                result = self._get_bitcoin_price(processor, currency)
                results.append(result)

            except OctoDataException as e:
                exceptions.append({
                    "source": processor.get_source_name(),
                    "error": str(e)
                })
            except Exception as e:
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
        

    def get_bitcoin_price(self, source: str, currency: str = "EUR") -> BitcoinPrice:

        processor = self.get_processor_by_source_name(bitcoin_processors, source)
        result = self._get_bitcoin_price(processor, currency)
        return result
        

    def _get_bitcoin_price(self, processor: PluginProcessor, currency: str = "EUR") -> BitcoinPrice:
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
    
    