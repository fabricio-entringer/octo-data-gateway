
from locale import currency
from app.api.mixin.processor_by_name import ProcessorByNameMixin
from app.core.custom_exception import ErrorCode, OctoDataException
from app.plugin.iban.register import iban_processors
from app.api.iban.schema import Iban
from app.plugin.processor import PluginProcessor


class IbanService(ProcessorByNameMixin):

    def get_iban_sources(self) -> list[str]:
        return [processor.get_source_name() for processor in iban_processors]

    def validate_iban(self, iban: str, source: str = "Schwifty") -> Iban:

        processor = self.get_processor_by_source_name(iban_processors, source)
        return self._validate_iban_and_format_data(processor, iban)


    def _validate_iban_and_format_data(self, processor: PluginProcessor, iban: str) -> Iban:
        result = processor.plugin_execute(params={"iban": iban})
        if result is not None and 'iban' in result:
            return Iban(
                iban=result.get('iban'),
                bic=result.get('bic'),
                is_valid=result.get('is_valid'),
                country_code=result.get('country_code'),
                country_name=result.get('country_name'),
                branch=result.get('branch'),
                bank_code=result.get('bank_code'),
                account_number=result.get('account_number'),
                account_type=result.get('account_type'),
                formatted_iban=result.get('formatted_iban'),
                iban_length=result.get('iban_length'),
                bank_name=result.get('bank_name'),
                bank_short_name=result.get('bank_short_name'),
                bban=result.get('bban'),
                checksum=result.get('checksum')
            )
        else:
            raise OctoDataException.from_error(
                error_code=ErrorCode.INVALID_RESPONSE,
                tech_details=f"API returned invalid data: {result}"
            )
        