
from app.plugin.plugins_register import register_processor
from app.plugin.iban.schwifty import SchwiftyPlugin


iban_processors = []
__resource_list = [SchwiftyPlugin]


# Register plugins when module is imported
def _register_plugins():
    """Register all available Iban plugins."""

    print("\033[94m🏦 [IBAN] Starting registration of IBAN plugins...\033[0m")
    for processor in __resource_list:
        register_processor(iban_processors, processor)

    print("\033[94m🏦 [IBAN] All IBAN plugins have been registered!\033[0m")


# Auto-register plugins
_register_plugins()    
    