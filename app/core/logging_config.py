import logging
import logging.config
from pythonjsonlogger import jsonlogger
from app.core.context import request_metadata_var
from app.core import config

class RequestIdAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        metadata = request_metadata_var.get()
        extra = kwargs.get("extra", {})
        extra.update({
            "request_id": getattr(metadata, "request_id", None) if metadata else None,
            "user_id": getattr(metadata, "user_id", None) if metadata else None,
            "path": getattr(metadata, "path", None) if metadata else None,
        })
        kwargs["extra"] = extra
        return msg, kwargs

class Logger: 

    @staticmethod
    def setup_logging():
        log_format = (
            "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(user_id)s"
        )

        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": log_format,   
                },
                "text": {
                    "()": "logging.Formatter",
                    "format": log_format,   
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                },
                "file": {
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "formatter": "json",
                    "filename": config.LOG_FILE_PATH,
                    "when": "midnight",
                    "interval": 1,
                    "encoding": "utf8",
                    "backupCount": config.LOG_RETENTION_DAYS,
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["console", "file"],
            },
        }

        logging.config.dictConfig(logging_config)

    @classmethod
    def get_logger(cls, name: str = "octo-data-gateway") -> logging.Logger:
        base_logger = logging.getLogger(name)
        adapter = RequestIdAdapter(base_logger, {})
        return adapter
