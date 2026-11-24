"""
Logging configuration helpers.
"""
import json
import logging
import os
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from core.request_context import get_request_id

# Attributes present on every LogRecord by default — anything else set via
# logger.info(..., extra={...}) is treated as structured context.
_RESERVED_ATTRS = frozenset(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {"message"}


class RequestIDLogFilter(logging.Filter):
    """Attaches the current request's id (if any) to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JSONFormatter(logging.Formatter):
    """Formats every log record as a single-line JSON object.

    Compatible with the StructuredLogger output shape so log aggregators
    see a consistent schema regardless of which logger style the module uses.
    """

    def format(self, record: logging.LogRecord) -> str:
        entry: dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED_ATTRS and key not in entry:
                entry[key] = value
        if record.exc_info:
            entry["traceback"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str, ensure_ascii=True)


def setup_logger(name="chatbot", log_file="chatbot.log", level=logging.INFO):
    """Set up the root logger with JSON-formatted console + rotating file handlers.

    Configuring the root logger (rather than just "chatbot") ensures every
    module's `logging.getLogger(__name__)` — database, llm, utils, api, cache —
    propagates here and gets the same JSON formatting and request_id context.
    """
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers = []

    request_id_filter = RequestIDLogFilter()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(JSONFormatter())
    console_handler.addFilter(request_id_filter)
    logger.addHandler(console_handler)

    try:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        file_handler.addFilter(request_id_filter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create file handler: {e}")

    return logger

