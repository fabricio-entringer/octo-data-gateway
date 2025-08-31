from app.plugin.plugins_register import register_processor
from app.plugin.email.email_validator_lib import EmailValidatorLibPlugin


email_processors = []
__resource_list = [EmailValidatorLibPlugin]


# Register plugins when module is imported
def _register_plugins():
    """Register all available Email plugins."""

    print("\033[94m📧 [Email] Starting registration of Email plugins...\033[0m")

    for processor in __resource_list:
        register_processor(email_processors, processor)

    print("\033[94m📧 [Email] All Email plugins have been registered!\033[0m")
    

# Auto-register plugins
_register_plugins()
