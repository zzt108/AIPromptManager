"""Reusable structlog configuration for Python projects.

This module provides project-agnostic logging configuration using structlog.
It can be copied to any Python project for standardized structured logging.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.processors import JSONRenderer


def configure_logging(
    app_name: str,
    seq_url: str | None = None,
    log_level: str = "INFO",
) -> None:
    """Configure structlog for any Python project.

    Sets up structured logging with console output and optional SEQ integration.
    Falls back gracefully if SEQ is unavailable.

    Args:
        app_name: Application name for log context
        seq_url: Optional SEQ server URL (e.g., "http://localhost:5341")
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Example:
        >>> configure_logging("AssetManager", log_level="DEBUG")
        >>> logger = structlog.get_logger()
        >>> logger.info("app_started", version="1.0")
    """
    # Convert log level string to logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )

    # Processors for structlog
    processors: list[Any] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Console rendering with color (development)
    if sys.stdout.isatty():
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # JSON rendering for production/SEQ
        processors.append(JSONRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Bind app name to all loggers
    logger = structlog.get_logger()
    logger = logger.bind(app_name=app_name)

    # SEQ integration (optional)
    if seq_url:
        try:
            # Attempt SEQ connection (requires seqlog package)
            import seqlog  # type: ignore

            seqlog.log_to_seq(
                server_url=seq_url,
                level=numeric_level,
                auto_flush_timeout=10,
            )
            logger.info("seq_configured", seq_url=seq_url)
        except ImportError:
            logger.warning(
                "seq_unavailable",
                message="seqlog package not installed, SEQ integration disabled",
            )
        except Exception as e:
            logger.warning(
                "seq_connection_failed",
                seq_url=seq_url,
                error=str(e),
            )

    logger.info("logging_configured", log_level=log_level)
