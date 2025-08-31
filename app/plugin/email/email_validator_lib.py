from app.plugin.processor import PluginProcessor
import dns.resolver
import smtplib
import socket
from app.core.custom_exception import ErrorCode, OctoDataException
from email_validator import EmailSyntaxError, validate_email, EmailNotValidError


class EmailValidatorLibPlugin(PluginProcessor):
    
    def plugin_execute(self, params: dict) -> dict:
        email = params.get("email")
        if not email:
            raise OctoDataException.from_error(
                error_code=ErrorCode.MISSING_PARAMETER,
                tech_details="The 'email' parameter is required."
            )


        return self._validate_email_full(email)
    
    
    def get_source_name(self) -> str:
        return "python_email_validator"
    
    
    def _validate_email_full(self, email: str) -> dict:
            emailResult = {
                "email": email,
                "valid_format": False,
                "valid_domain": False,
                "smtp_check": False,
            }

            self._validate_email_format(email)
            emailResult["valid_format"] = True

            domain = email.split("@")[1]
            emailResult["valid_domain"] = self._validate_email_domain(domain)
            emailResult["smtp_check"] = self._validate_email_smtp(email)

            return emailResult


    def _validate_email_format(self, email: str) -> bool:
        try:
            validate_email(email, check_deliverability=False)
            return True
        except EmailSyntaxError as e:
            raise OctoDataException.from_error(error_code=ErrorCode.INVALID_DATA, 
                                                tech_details=str(e))
        except EmailNotValidError:
            return False
        

    def _validate_email_domain(self, domain: str) -> bool:
        try:
            mx_records = dns.resolver.resolve(domain, "MX")
            return len(mx_records) > 0
        
        except Exception:
            return False


    def _validate_email_smtp(self, email: str) -> bool:
        try:
            mx_records = dns.resolver.resolve(email.split("@")[1], "MX")
            mx_host = str(mx_records[0].exchange)
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_host)
            server.helo(socket.gethostname())
            server.mail("test@example.com")
            code, _ = server.rcpt(email)
            server.quit()
            return code == 250
                
        except Exception as e:
            return False