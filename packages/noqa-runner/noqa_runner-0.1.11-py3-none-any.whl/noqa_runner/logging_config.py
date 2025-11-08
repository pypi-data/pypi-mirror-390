"""Structured logging configuration for runner"""

from __future__ import annotations

import logging
import sys

import structlog


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure structured JSON logging with context support

    Can be called multiple times (e.g., to change log level).

    Sets up:
    - JSON formatting for all logs
    - Context variables support (test_id, etc.)
    - Disabled external library logs

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR)
    """
    # Disable logs from external libraries
    logging.getLogger("appium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)

    # Configure structlog
    structlog.configure(
        processors=[
            # Add log level
            structlog.stdlib.add_log_level,
            # Add timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            # Merge context variables (test_id, etc.)
            structlog.contextvars.merge_contextvars,
            # Stack trace formatting
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # Final JSON rendering
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging to work with structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get configured structlog logger

    Note: If configure_logging() hasn't been called yet, this will return
    a logger with default structlog configuration. Call configure_logging()
    early in your application startup.
    """
    return structlog.get_logger(name)
