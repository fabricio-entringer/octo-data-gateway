

from fastapi import APIRouter, Path
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.core.security import require_scopes
from app.database.models import Scopes
from .schema import EmailResponse
from app.log.logging_config import Logger  
from app.core.context import request_metadata_var
from app.core.custom_exception import EAGCustomException, ErrorCode
from app.api.email.service import EmailService 


router = APIRouter()
logger = Logger.get_logger()

email_service = EmailService()

@router.get("/validate/{email}", 
            status_code=200,
            response_model=EmailResponse,
            dependencies=[Depends(require_scopes([Scopes.EMAIL]))]
)
async def validate_email(email: str = Path(..., 
                        description="The email address to validate",
                        example="user@example.com")) -> EmailResponse:
    """
    Validate the given email address.

    - **email**: The email address to validate.
    """
    try:
        logger.info("Request received for email validation", extra={"email": email})
        metadata = request_metadata_var.get()

        email = await email_service.validate_email(email=email)
        is_partial = email.smtp_check is False or email.valid_domain is False or email.valid_format is False

        return JSONResponse(
                    status_code=206 if is_partial else 200,
                    content=jsonable_encoder(EmailResponse(
                        email=email,
                        metadata=metadata.finish_successful_request()
                    )))
        
    except EAGCustomException as e:
        logger.error("EAGCustomException caught in validate_email", extra={"error": e.for_log()})
        return JSONResponse(
            status_code=e.http_status,
            content=jsonable_encoder(EmailResponse(metadata=metadata.finish_failed_request(e)))
        )