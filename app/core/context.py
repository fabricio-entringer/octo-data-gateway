# app/core/context.py
import contextvars
request_metadata_var = contextvars.ContextVar("request_metadata", default=None)