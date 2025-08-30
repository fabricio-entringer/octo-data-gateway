
from app.plugin.plugins_register import register_processor
from app.plugin.iban.schwifty import SchwiftyPlugin


iban_processors = []
__resource_list = [SchwiftyPlugin]


# Register plugins when module is imported
def _register_plugins():
    """Register all available Iban plugins."""

    for processor in __resource_list:
        register_processor(iban_processors, processor)


# Auto-register plugins
_register_plugins()    
    