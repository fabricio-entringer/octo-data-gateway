from pydantic import BaseModel, Field
from typing import Optional

from app.core.models import Metadata

class Iban(BaseModel):
    iban: str = Field(..., example="GB82WEST12345698765432")
    is_valid: bool = Field(..., example=True)
    country_code: Optional[str] = Field(None, example="GB")
    country_name: Optional[str] = Field(None, example="United Kingdom")
    branch: Optional[str] = Field(None, example="123456")
    bban: Optional[str] = Field(None, example="WEST12345698765432")
    formatted_iban: Optional[str] = Field(None, example="GB82 WEST 1234 5698 7654 32")
    bank_name: Optional[str] = Field(None, example="Deutsche Bank")
    bank_short_name: Optional[str] = Field(None, example="Deutsche")
    account_number: Optional[str] = Field(None, example="0532013000")
    bank_code: Optional[str] = Field(None, example="20070000")
    checksum: Optional[str] = Field(None, example="16")
    account_type: Optional[str] = Field(None, example="CURRENT")
    iban_length: Optional[int] = Field(None, example=22)
    bic: Optional[str] = Field(None, example="DEUTDEFF")

    class Config:
        json_schema_extra = {
            "example": {
                "iban": "GB82WEST12345698765432",
                "is_valid": True,
                "country_code": "GB",
                "country_name": "United Kingdom",
                "branch": "123456",
                "bban": "WEST12345698765432",
                "formatted_iban": "GB82 WEST 1234 5698 7654 32",
                "bank_name": "Deutsche Bank",
                "bank_short_name": "Deutsche",
                "account_number": "0532013000",
                "bank_code": "20070000",
                "checksum": "16",
                "account_type": "CURRENT",
                "iban_length": 22,
                "bic": "DEUTDEFF"
            }
        }


class IbanResponse(BaseModel):
    iban: Optional[Iban] = Field(None, description="The validated IBAN details")
    metadata: Metadata = Field(..., description="Metadata about the request and response")