import pytest
from unittest.mock import MagicMock
from app.plugin.email.email_validator_lib import EmailValidatorLibPlugin
from app.core.custom_exception import OctoDataException, ErrorCode

# Constants for test data
VALID_EMAILS = [
    "user@example.com",
    "test.email+tag@gmail.com",
    "user@subdomain.example.org",
    "user@valid-domain.com",
    "user.name@domain.co.uk",
    "user_name@domain.com",
    "user-name@domain.com",
    "user123@domain123.com",
    "user@xn--d1acufc.xn--p1ai",  # punycode for internationalized domain
    "üñîçøðé@domain.com",  # unicode local part
    "user@domain.travel",
    "user@domain.museum",
    "user@domain.info",
    "user@domain.io",
    "user@domain.ai",
    "user@domain.email",
    "user@domain.one",
    "user@domain.global",
    "user@domain.xyz",
    "user@domain.c",
    "user@domain.toolongtld",
    "user@domain.co2m",
]

INVALID_EMAILS = [
    "invalid-email",
    "@example.com",
    "user@",
    "user@@example.com",
    "user example.com",
    "user@.com",
    "user@domain..com",
    "user@domain,com",
    "user@domain@domain.com",
    "user@domain",
    "user@-domain.com",
    "user@domain-.com",
    ".user@domain.com",
    "user@localhost",
    "user.@domain.com",
    "user..name@domain.com",
    "user@domain..com",
    "user@.domain.com",
    "user@domain.com.",
    "user@domain#com",
    "user@domain!com",
    "user@domain$.com",
    "user@domain%.com",
    "user@domain^com",
    "user@domain&com",
    "user@domain*com",
    "user@domain(com",
    "user@domain)com",
    "user@domain=com",
    "user@domain+com",
    "user@domain,com",
    "user@domain;com",
    "user@domain:com",
    "user@domain/com",
    "user@domain\\com",
    "user@domain[com",
    "user@domain]com",
    "user@domain{com",
    "user@domain}com",
    "user@domain|com",
    "user@domain<.com",
    "user@domain>.com",
    "user@domain?com",
    "user@domain,com",
    "user@domain..com",
    "user@.domain.com",
    "user@domain.com.",
]

class FakeSMTP:
    """Mock SMTP class for testing."""
    def __init__(self):
        self.connected = False

    def connect(self, host):
        self.connected = True

    def helo(self, host):
        pass

    def mail(self, sender):
        pass

    def rcpt(self, email):
        return (250, "OK")

    def quit(self):
        pass

@pytest.fixture
def plugin():
    """Fixture to provide an instance of EmailValidatorLibPlugin."""
    return EmailValidatorLibPlugin()

@pytest.fixture
def fake_smtp():
    """Fixture to provide a fake SMTP instance."""
    return FakeSMTP()

def test_get_source_name(plugin):
    """Test that get_source_name returns the correct source name."""
    assert plugin.get_source_name() == "python_email_validator"

@pytest.mark.parametrize("email", VALID_EMAILS)
def test_validate_email_format_valid(plugin, email):
    """Test valid email format validation."""
    assert plugin._validate_email_format(email) is True

@pytest.mark.parametrize("email", INVALID_EMAILS)
def test_validate_email_format_invalid(plugin, email):
    """Test invalid email format validation raises exception."""
    with pytest.raises(OctoDataException):
        plugin._validate_email_format(email)

def test_validate_email_domain_valid(plugin, mocker):
    """Test valid domain validation with MX records."""
    mock_mx = MagicMock()
    mock_mx.exchange = "smtp.gmail.com"
    mocker.patch("dns.resolver.resolve", return_value=[mock_mx])
    assert plugin._validate_email_domain("gmail.com") is True

def test_validate_email_domain_invalid(plugin, mocker):
    """Test invalid domain validation without MX records."""
    mocker.patch("dns.resolver.resolve", side_effect=Exception("No MX records"))
    assert plugin._validate_email_domain("invalid-domain.com") is False

def test_validate_email_smtp_success(plugin, mocker, fake_smtp):
    """Test successful SMTP validation."""
    mock_mx = MagicMock()
    mock_mx.exchange = "smtp.gmail.com"
    mocker.patch("dns.resolver.resolve", return_value=[mock_mx])
    mocker.patch("smtplib.SMTP", return_value=fake_smtp)
    assert plugin._validate_email_smtp("test@gmail.com") is True

def test_validate_email_smtp_failure(plugin, mocker):
    """Test SMTP validation failure."""
    mocker.patch("dns.resolver.resolve", side_effect=Exception("No MX records"))
    assert plugin._validate_email_smtp("test@gmail.com") is False

def test_plugin_execute_valid_email(plugin, mocker):
    """Test plugin_execute with a valid email."""
    # Mock domain and SMTP checks to avoid real network calls
    mocker.patch.object(plugin, "_validate_email_domain", return_value=True)
    mocker.patch.object(plugin, "_validate_email_smtp", return_value=True)
    params = {"email": "test@gmail.com"}
    result = plugin.plugin_execute(params)
    assert result["email"] == "test@gmail.com"
    assert result["valid_format"] is True
    assert result["valid_domain"] is True
    assert result["smtp_check"] is True

def test_plugin_execute_missing_email(plugin):
    """Test plugin_execute with missing email parameter."""
    params = {}
    with pytest.raises(OctoDataException) as exc:
        plugin.plugin_execute(params)
    assert exc.value.code == ErrorCode.MISSING_PARAMETER.code

def test_plugin_execute_invalid_format(plugin):
    """Test plugin_execute with invalid email format."""
    params = {"email": "invalid-email"}
    with pytest.raises(OctoDataException):
        plugin.plugin_execute(params)

# Additional edge cases
def test_validate_email_domain_no_mx_records(plugin, mocker):
    """Test domain validation when no MX records are found."""
    mocker.patch("dns.resolver.resolve", return_value=[])
    assert plugin._validate_email_domain("example.com") is False

def test_validate_email_smtp_connection_error(plugin, mocker):
    """Test SMTP validation with connection error."""
    mock_mx = MagicMock()
    mock_mx.exchange = "smtp.gmail.com"
    mocker.patch("dns.resolver.resolve", return_value=[mock_mx])
    mocker.patch("smtplib.SMTP", side_effect=Exception("Connection failed"))
    assert plugin._validate_email_smtp("test@gmail.com") is False
