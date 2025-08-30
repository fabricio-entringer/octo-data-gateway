
from app.core.custom_exception import ErrorCode, OctoDataException
from app.plugin.processor import PluginProcessor

class ProcessorByNameMixin:
    """
    Mixin class to provide functionality for retrieving processors by their source name.
    """

    def get_processor_by_source_name(self, processor_list: list[PluginProcessor], source: str) -> PluginProcessor:
        print(processor_list)
        processor = next((p for p in processor_list if p.get_source_name().lower() == source.lower()), None)

        if processor is None:
            raise OctoDataException.from_error(
                error_code=ErrorCode.INVALID_REQUEST,
                tech_details=f"Source '{source}' not found among registered processors. Available sources: {[p.get_source_name() for p in processor_list]}"
            )
        
        return processor