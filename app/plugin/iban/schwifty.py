
from app.plugin.processor import PluginProcessor
from schwifty import IBAN
from schwifty.exceptions import SchwiftyException

from app.core.custom_exception import ErrorCode, OctoDataException


class SchwiftyPlugin(PluginProcessor):
    def plugin_execute(self, params: dict) -> dict:
        
        iban_str = params.get("iban")
        if not iban_str:
            raise OctoDataException.from_error(
                error_code=ErrorCode.MISSING_PARAMETER,
                tech_details="The 'IBAN' parameter is required."
            )

        try:
            iban = IBAN(iban_str)
            bic = iban.bic
            country = iban.country
            return {
                "iban": str(iban),
                "bic": str(bic) if bic else None,
                "is_valid": iban.is_valid,
                "country_code": iban.country_code,
                "country_name": country.name if country else None,
                "branch": bic.branch_code if bic else None,
                "bank_code": iban.bank_code,
                "account_number": iban.account_code,
                "account_type": iban.account_type,
                "formatted_iban": iban.formatted,
                "iban_length": len(str(iban)),
                "bank_name": bic.bank_name if bic else None, 
                "bank_short_name": bic.bank_short_name if bic else None,
                "bban": str(iban.bban) if iban.bban else None,
                "checksum": iban.checksum_digits if iban.checksum_digits else None
            }
        except SchwiftyException as e:
            raise OctoDataException.from_error(
                error_code=ErrorCode.INVALID_DATA,
                tech_details=f"Invalid IBAN: {e}"
            )
        
        except Exception as e:
            raise OctoDataException.from_error(
                error_code=ErrorCode.INTERNAL_SERVER_ERROR,
                tech_details=f"An error occurred while processing the IBAN {iban_str}, Error: {e}"
            )


    def get_source_name(self) -> str:
        return "Schwifty"