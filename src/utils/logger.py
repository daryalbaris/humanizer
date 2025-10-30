"""
AI Humanizer System - Structured Logging Infrastructure
=======================================================

Implements structured JSON logging for all components following the
logging strategy in docs/coding-standards.md.

Features:
- JSON-formatted logs for machine parsing
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Automatic component identification
- Performance timing decorators
- Log file rotation (prevents disk space issues)
- Console output for development
- Structured metadata (timestamp, component, level, message, data)

Usage Example:
    from src.utils.logger import get_logger

    logger = get_logger(__name__)  # __name__ = "src.tools.term_protector"

    logger.info("Processing text", extra={
        "text_length": 8000,
        "protected_terms": 15
    })

    # Output (JSON):
    # {"timestamp": "2025-10-30T10:15:30.123Z", "level": "INFO",
    #  "component": "term_protector", "message": "Processing text",
    #  "data": {"text_length": 8000, "protected_terms": 15}}

Log Levels:
    DEBUG: Detailed diagnostic information (e.g., placeholder mappings)
    INFO: General progress information (e.g., "Processing completed")
    WARNING: Warnings that don't stop execution (e.g., "Glossary term not found")
    ERROR: Errors that affect current operation (e.g., "Validation failed")
    CRITICAL: System-level failures (e.g., "Configuration file missing")

Author: BMAD Development Team
Date: 2025-10-30
Version: 1.0
"""

import logging
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
from logging.handlers import RotatingFileHandler
import functools
import time


# Global logging configuration
LOG_DIR = Path(".humanizer/logs")
LOG_FILE = LOG_DIR / "humanizer.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keep 5 old log files


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format.

    Each log entry is a JSON object with fields:
    - timestamp: ISO 8601 timestamp
    - level: Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - component: Component/module name
    - message: Log message
    - data: Additional structured data (optional)
    - error: Error details if exception (optional)

    Example output:
        {
            "timestamp": "2025-10-30T10:15:30.123456",
            "level": "INFO",
            "component": "term_protector",
            "message": "Protected 15 terms",
            "data": {"text_length": 8000, "processing_time_ms": 234}
        }
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string.

        Args:
            record: LogRecord instance from logging module

        Returns:
            JSON string representing the log entry
        """
        # Extract component name from logger name
        # "src.tools.term_protector" → "term_protector"
        component = record.name.split(".")[-1] if "." in record.name else record.name

        # Build base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "component": component,
            "message": record.getMessage(),
        }

        # Add structured data if present (passed via extra={} in logging call)
        if hasattr(record, "data"):
            log_entry["data"] = record.data

        # Add exception information if present
        if record.exc_info:
            log_entry["error"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }

        return json.dumps(log_entry)


class HumanizerLogger:
    """Wrapper around Python's logging.Logger with convenience methods.

    Provides structured logging with automatic metadata inclusion and
    performance timing capabilities.

    Attributes:
        logger (logging.Logger): Underlying Python logger instance
        component (str): Component name for this logger
    """

    def __init__(self, logger: logging.Logger):
        """Initialize HumanizerLogger.

        Args:
            logger: Configured Python logger instance
        """
        self.logger = logger
        # Extract component name
        self.component = logger.name.split(".")[-1] if "." in logger.name else logger.name

    def debug(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log DEBUG level message with structured data.

        Args:
            message: Log message
            data: Additional structured data (optional)
        """
        self.logger.debug(message, extra={"data": data} if data else {})

    def info(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log INFO level message with structured data.

        Args:
            message: Log message
            data: Additional structured data (optional)
        """
        self.logger.info(message, extra={"data": data} if data else {})

    def warning(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log WARNING level message with structured data.

        Args:
            message: Log message
            data: Additional structured data (optional)
        """
        self.logger.warning(message, extra={"data": data} if data else {})

    def error(self, message: str, data: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log ERROR level message with structured data.

        Args:
            message: Log message
            data: Additional structured data (optional)
            exc_info: Include exception traceback if True
        """
        self.logger.error(message, extra={"data": data} if data else {}, exc_info=exc_info)

    def critical(self, message: str, data: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log CRITICAL level message with structured data.

        Args:
            message: Log message
            data: Additional structured data (optional)
            exc_info: Include exception traceback if True
        """
        self.logger.critical(message, extra={"data": data} if data else {}, exc_info=exc_info)

    def exception(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log exception with full traceback at ERROR level.

        Args:
            message: Log message
            data: Additional structured data (optional)
        """
        self.logger.exception(message, extra={"data": data} if data else {})


def setup_logging(
    level: str = "INFO",
    console: bool = True,
    file: bool = True,
    log_file: Optional[Path] = None
) -> None:
    """Configure global logging settings for the application.

    This should be called once at application startup (orchestrator initialization).

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console: Enable console output if True
        file: Enable file output if True
        log_file: Custom log file path (uses default if None)

    Example:
        # Development mode (verbose console output)
        setup_logging(level="DEBUG", console=True, file=False)

        # Production mode (file logging only)
        setup_logging(level="INFO", console=False, file=True)
    """
    # Create log directory if it doesn't exist
    log_path = log_file or LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers (avoid duplicate logging)
    root_logger.handlers.clear()

    # JSON formatter for structured logs
    json_formatter = JSONFormatter()

    # Console handler (human-readable for development)
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))

        # Use simple format for console (not JSON for readability)
        console_formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File handler (JSON format with rotation)
    if file:
        file_handler = RotatingFileHandler(
            filename=log_path,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> HumanizerLogger:
    """Get a logger instance for a component.

    Args:
        name: Component name (typically __name__ from the calling module)

    Returns:
        HumanizerLogger instance configured for the component

    Example:
        logger = get_logger(__name__)  # __name__ = "src.tools.term_protector"
        logger.info("Processing started")
    """
    # Get Python's standard logger
    python_logger = logging.getLogger(name)

    # Wrap in our custom logger
    return HumanizerLogger(python_logger)


def log_performance(func):
    """Decorator to automatically log function execution time.

    Usage:
        @log_performance
        def expensive_operation(data):
            # ... processing ...
            return result

    Logs:
        INFO: "expensive_operation completed" with execution_time_ms in data
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.time() - start_time) * 1000

            logger.info(
                f"{func.__name__} completed",
                data={
                    "execution_time_ms": round(elapsed_ms, 2),
                    "function": func.__name__
                }
            )

            return result

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000

            logger.error(
                f"{func.__name__} failed",
                data={
                    "execution_time_ms": round(elapsed_ms, 2),
                    "function": func.__name__,
                    "error": str(e)
                },
                exc_info=True
            )
            raise

    return wrapper


# Initialize logging on module import (can be reconfigured later)
# Default: INFO level, console output only (file logging disabled until orchestrator starts)
if not logging.getLogger().handlers:
    setup_logging(level="INFO", console=True, file=False)
