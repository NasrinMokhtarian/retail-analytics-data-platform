import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JsonFormatter(logging.Formatter):
    """
    Simple JSON formatter for structured logs.

    This keeps logs readable by humans and also easier to search/filter later.
    """

    RESERVED_ATTRS = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "message",
        "asctime",
        "taskName"
    }

    def format(self, record: logging.LogRecord) -> str:
        log_record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        extra_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in self.RESERVED_ATTRS
        }

        log_record.update(extra_fields)

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record, default=str)


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure application logging.

    Logs are written to stdout in JSON format.
    """

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())



"""
expected log output example:
    {
  "timestamp": "2026-05-17T10:30:00+00:00",
  "level": "INFO",
  "logger": "retail_analytics.ingestion.inspect_raw_files",
  "message": "CSV file inspected successfully",
  "file_name": "olist_orders_dataset.csv",
  "row_count": 99441,
  "column_count": 8
    }
"""