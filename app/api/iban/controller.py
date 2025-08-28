

from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.iban.schema import IbanResponse
from app.api.iban.service import IbanService
from app.core.custom_exception import EAGCustomException
from app.core.security import require_scopes
from app.database.models import Scopes
from app.log.logging_config import Logger


router = APIRouter()
iban_service = IbanService()
logger = Logger.get_logger()

@router.get("/validate", 
            response_model=IbanResponse,
            status_code=200,
            dependencies=[Depends(require_scopes([Scopes.IBAN]))]
)
async def validate_iban(iban: str = Query(..., 
                                         description="The IBAN to be validated",
                                         example="GB82WEST12345698765432")):
    """
    Validate an IBAN (International Bank Account Number).

    This endpoint checks the validity of the provided IBAN and returns detailed information
    about it, including country, bank details, and formatting.

    - **iban**: The IBAN to be validated.

    Returns a JSON object containing the validation result and associated metadata.
    """
    
    logger.info("Request received for IBAN validation", extra={"iban": iban})
    try:
        iban_details = iban_service.validate_iban(iban=iban)
        metadata = {"status": "success", "message": "IBAN validated successfully."}
        logger.info("IBAN validation successful", extra={"iban": iban, "details": jsonable_encoder(iban_details)})
        return IbanResponse(iban=iban_details, metadata=metadata)

    except EAGCustomException as e:
        logger.error("EAGCustomException caught in validate_iban", extra={"error": e.for_log()})
        return JSONResponse(
            status_code=e.http_status,
            content=jsonable_encoder(IbanResponse(metadata=metadata.finish_failed_request(e)))
        )