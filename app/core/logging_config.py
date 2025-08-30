import logging
import logging.config
from fastapi import logger
from pythonjsonlogger import jsonlogger
from app.core.context import request_metadata_var

class RequestIdAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        metadata = request_metadata_var.get()
        extra = kwargs.get("extra", {})
        extra.update({"request_id": getattr(metadata, "request_id", None) if metadata else None})
        extra.update({"user_id": getattr(metadata, "user_id", None) if metadata else None})
        extra.update({"path": getattr(metadata, "path", None) if metadata else None})
        kwargs["extra"] = extra
        return msg, kwargs

class Logger: 

    @staticmethod
    def setup_logging():
        log_format = ("%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(user_id)s %(service_name)s")

        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": jsonlogger.JsonFormatter,
                    "fmt": log_format,
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        }

        logging.config.dictConfig(logging_config)
        logging.LoggerAdapter(logging.getLogger(), {"service_name": "external-data-gateway"})

    @classmethod
    def get_logger(cls, name: str = "external-data-gateway") -> logging.Logger:
        """
        Get a logger instance with the specified name.
        """
        adapter = RequestIdAdapter(logging.getLogger(name), {})

        return adapter