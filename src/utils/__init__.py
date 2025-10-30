"""
AI Humanizer System - Utility Functions
========================================

This package contains shared utility functions used across all components:
- Logging infrastructure (structured JSON logging)
- Exception classes (custom errors for the system)
- Configuration loading (YAML + environment variables)
- Common helper functions

All Python tools import from this package for consistent behavior.
"""

__version__ = "1.0.0"

# Import commonly used utilities for convenience
from .logger import get_logger, setup_logging
from .exceptions import (
    HumanizerError,
    ValidationError,
    ProcessingError,
    ConfigError,
    FileNotFoundError as HumanizerFileNotFoundError,
    APIError
)

__all__ = [
    "get_logger",
    "setup_logging",
    "HumanizerError",
    "ValidationError",
    "ProcessingError",
    "ConfigError",
    "HumanizerFileNotFoundError",
    "APIError",
]
