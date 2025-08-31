
import asyncio
from app.api.email.schema import Email

from app.api.iban.schema import Iban
from app.api.mixin.processor_by_name import ProcessorByNameMixin
from app.core.custom_exception import OctoDataException, ErrorCode
from app.plugin.email.register import email_processors
from app.plugin.processor import PluginProcessor

class EmailService(ProcessorByNameMixin):

    async def validate_email(self, email: str, source: str= "python_email_validator") -> Email:
        return await asyncio.to_thread(self._validate_email_full, email, source)

    def _validate_email_full(self, email: str, source: str) -> Email:

        processor = self.get_processor_by_source_name(email_processors, source)
        return self._validate_email(processor, email)

    def _validate_email(self, processor: PluginProcessor, email: str) -> Email:
        result = processor.plugin_execute(params={"email": email})
        if result is not None and 'email' in result:
            return Email(
                email=result.get('email'),
                valid_format=result.get('valid_format'),
                valid_domain=result.get('valid_domain'),
                smtp_check=result.get('smtp_check')
            )
        else:
            raise OctoDataException.from_error(
                error_code=ErrorCode.INVALID_RESPONSE,
                tech_details=f"Email plugin '{processor.get_source_name()}' returned invalid data: {result}"
            )


    