"""
Structured Logger with JSON formatting.
"""
import json
import logging
import sys
import time
import traceback
from datetime import datetime
from typing import Optional


class StructuredLogger:
    """JSON-based structured logger with context fields."""

    def __init__(self, name: str, min_level: int = logging.INFO):
        self.name = name
        self.base_logger = logging.getLogger(name)
        self.base_logger.setLevel(min_level)
        self.context = {}

    def _format_message(self, level: str, event: str, **kwargs) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "logger": self.name,
            "event": event,
        }
        log_entry.update(self.context)
        log_entry.update(kwargs)
        return json.dumps(log_entry, default=str, ensure_ascii=False)

    def set_context(self, **kwargs):
        self.context.update(kwargs)

    def clear_context(self):
        self.context = {}

    def info(self, event: str, **kwargs):
        self.base_logger.info(self._format_message("INFO", event, **kwargs))

    def warning(self, event: str, **kwargs):
        self.base_logger.warning(self._format_message("WARNING", event, **kwargs))

    def error(self, event: str, error: Optional[Exception] = None, **kwargs):
        if error:
            kwargs["error_type"] = type(error).__name__
            kwargs["error_message"] = str(error)
            kwargs["traceback"] = traceback.format_exc()
        self.base_logger.error(self._format_message("ERROR", event, **kwargs))

    def debug(self, event: str, **kwargs):
        self.base_logger.debug(self._format_message("DEBUG", event, **kwargs))

    def timing(self, event: str, duration_ms: float, **kwargs):
        kwargs["duration_ms"] = round(duration_ms, 2)
        self.info(event, **kwargs)


class TimingContext:
    """Context manager for timing operations."""

    def __init__(self, logger: StructuredLogger, event: str, **kwargs):
        self.logger = logger
        self.event = event
        self.context = kwargs
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        if exc_type:
            self.logger.error(
                f"{self.event}_failed",
                error=exc_val,
                duration_ms=round(duration_ms, 2),
                **self.context,
            )
        else:
            self.logger.timing(self.event, duration_ms, **self.context)
        return False


def setup_structured_logging(name: str = "chatbot", level: int = logging.INFO) -> StructuredLogger:
    """Setup structured logging for application."""
    base_logger = logging.getLogger(name)
    base_logger.setLevel(level)
    base_logger.handlers = []

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    base_logger.addHandler(console_handler)
    return StructuredLogger(name, level)


class CompatibilityWrapper:
    """Compatibility wrapper for standard logging.Logger style usage."""

    def __init__(self, structured_logger: StructuredLogger):
        self.logger = structured_logger

    def info(self, msg: str, *args, **kwargs):
        formatted_msg = msg % args if args else msg
        self.logger.info("log_message", message=formatted_msg, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        formatted_msg = msg % args if args else msg
        self.logger.warning("log_message", message=formatted_msg, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        formatted_msg = msg % args if args else msg
        error = kwargs.pop("exc_info", None)
        self.logger.error("log_message", message=formatted_msg, error=error, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        formatted_msg = msg % args if args else msg
        self.logger.debug("log_message", message=formatted_msg, **kwargs)

