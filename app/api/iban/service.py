

from app.api.iban.schema import Iban


class IbanService:
    def validate_iban(self, iban: str) -> Iban:

        return Iban(
            iban="GB82WEST12345698765432",
            valid=True,
            country="GB",
            branch="123456",
            bban="WEST12345698765432",  
            formatted_iban="GB82 WEST 1234 5698 7654 32",
            bank_name="Deutsche Bank",
            account_number="0532013000",
            bank_code="20070000",
            checksum="16"
        )
        