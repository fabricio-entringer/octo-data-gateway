
from abc import abstractmethod


class PluginProcessor:
    """ A class to handle plugin-related operations
    """

    @abstractmethod
    def plugin_execute(self, params: dict) -> dict:
        """ 
        Abstract method to be implemented by subclasses to execute plugin logic.
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """"
        Abstract method to return the name of the plugin source.
        """
        
        pass    