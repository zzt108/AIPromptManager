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

    # Shared processors (structure the data)
    shared_processors: list[Any] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Structlog config: Wrap for stdlib formatter
    structlog.configure(
        processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Define formatters based on environment
    # Force ConsoleRenderer for readable logs even if not TTY (e.g. running via batch wrapper)
    console_processor = structlog.dev.ConsoleRenderer(pad_event=5)

    console_formatter = structlog.stdlib.ProcessorFormatter(
        processor=console_processor,
        foreign_pre_chain=shared_processors,
    )

    # Configure standard library logging
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Bind app name to all loggers
    logger = structlog.get_logger()
    logger = logger.bind(app_name=app_name)

    # SEQ integration (optional) - Direct HTTP API
    if seq_url:
        try:
            import requests
            import json
            import threading
            import queue
            from datetime import datetime, timezone

            class SeqHttpHandler(logging.Handler):
                """Custom handler that sends logs directly to Seq via HTTP API."""
                
                def __init__(self, seq_url: str, batch_size: int = 10, flush_interval: float = 2.0):
                    super().__init__()
                    self.seq_url = seq_url.rstrip("/")
                    self.batch_size = batch_size
                    self.flush_interval = flush_interval
                    self.log_queue: queue.Queue = queue.Queue()
                    self.session = requests.Session()
                    self._stop_event = threading.Event()
                    self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
                    self._flush_thread.start()
                
                def emit(self, record):
                    try:
                        # Unwrap structlog dictionary
                        event_dict = None
                        if isinstance(record.msg, dict):
                            event_dict = record.msg
                        elif hasattr(record.msg, "items"):
                            try:
                                event_dict = dict(record.msg)
                            except:
                                pass
                        
                        if event_dict:
                            # Build CLEF payload
                            payload = {
                                "@t": event_dict.get("timestamp", datetime.now(timezone.utc).isoformat()),
                                "@mt": event_dict.get("event", "unknown_event"),
                                "@l": event_dict.get("level", "Information").capitalize(),
                            }
                            
                            # Add all properties (excluding internal ones)
                            exclude = {"event", "level", "timestamp", "logger"}
                            for k, v in event_dict.items():
                                if k not in exclude:
                                    # Serialize non-primitive types
                                    if not isinstance(v, (str, int, float, bool, type(None))):
                                        v = str(v)
                                    payload[k] = v
                        else:
                            # Standard log record
                            payload = {
                                "@t": datetime.now(timezone.utc).isoformat(),
                                "@mt": record.getMessage(),
                                "@l": record.levelname.capitalize(),
                                "logger": record.name,
                            }
                        
                        self.log_queue.put(payload)
                    except Exception:
                        pass  # Silent fail - don't break logging
                
                def _flush_loop(self):
                    """Background thread that flushes logs to Seq."""
                    while not self._stop_event.is_set():
                        self._flush_batch()
                        self._stop_event.wait(self.flush_interval)
                    # Final flush on shutdown
                    self._flush_batch()
                
                def _flush_batch(self):
                    """Send accumulated logs to Seq."""
                    batch = []
                    while len(batch) < self.batch_size:
                        try:
                            batch.append(self.log_queue.get_nowait())
                        except queue.Empty:
                            break
                    
                    if batch:
                        try:
                            # CLEF format: newline-delimited JSON
                            payload = "\n".join(json.dumps(item) for item in batch)
                            self.session.post(
                                f"{self.seq_url}/api/events/raw",
                                data=payload,
                                headers={"Content-Type": "application/vnd.serilog.clef"},
                                timeout=5,
                            )
                        except Exception:
                            pass  # Silent fail
                
                def close(self):
                    self._stop_event.set()
                    self._flush_thread.join(timeout=2)
                    super().close()

            seq_handler = SeqHttpHandler(seq_url, batch_size=1, flush_interval=0.5)
            logging.getLogger().addHandler(seq_handler)
            
            logger.info("seq_configured", seq_url=seq_url)
        except ImportError as e:
            logger.warning(
                "seq_unavailable",
                message="requests package not available",
                error=str(e),
            )
        except Exception as e:
            logger.warning(
                "seq_connection_failed",
                seq_url=seq_url,
                error=str(e),
            )

    # Setup Console Handler explicitly with the formatter
    # Add it AFTER Seq to ensure proper ordering and that Seq (via basicConfig) didn't block it
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    logger.info("logging_configured", log_level=log_level)
