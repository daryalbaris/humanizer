"""
AI Humanizer System - Custom Exception Classes
==============================================

Defines custom exceptions for the AI Humanizer System following the
error handling strategy documented in docs/error-handling-strategy.md.

Exception Hierarchy:
    HumanizerError (base)
    ├── ValidationError (input validation failures)
    ├── ProcessingError (tool execution failures)
    ├── ConfigError (configuration loading/parsing failures)
    ├── FileNotFoundError (file system errors)
    └── APIError (external API failures - Claude, Originality.ai)

Usage Example:
    from src.utils.exceptions import ValidationError

    if not text:
        raise ValidationError(
            message="Input text cannot be empty",
            component="term_protector",
            details={"text_length": 0}
        )

All exceptions support structured error reporting with:
- message: Human-readable error description
- component: Which tool/module raised the error
- details: Additional context (dict) for debugging
- original_error: Original exception (if wrapping another exception)

Author: BMAD Development Team
Date: 2025-10-30
Version: 1.0
"""

from typing import Dict, Any, Optional


class HumanizerError(Exception):
    """Base exception for all AI Humanizer System errors.

    All custom exceptions inherit from this class to enable
    catch-all error handling when needed.

    Args:
        message: Human-readable error description
        component: Name of the tool/module that raised the error
        details: Additional context for debugging (optional)
        original_error: Original exception if wrapping (optional)

    Attributes:
        message (str): Error message
        component (str): Component name
        details (Dict[str, Any]): Additional error context
        original_error (Optional[Exception]): Wrapped exception
    """

    def __init__(
        self,
        message: str,
        component: str = "unknown",
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize HumanizerError with structured error information."""
        self.message = message
        self.component = component
        self.details = details or {}
        self.original_error = original_error

        # Construct full error message
        full_message = f"[{component}] {message}"
        if details:
            full_message += f" | Details: {details}"
        if original_error:
            full_message += f" | Caused by: {type(original_error).__name__}: {str(original_error)}"

        super().__init__(full_message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization.

        Returns:
            Dictionary with error details suitable for JSON output

        Example:
            {
                "error_type": "ValidationError",
                "message": "Input text cannot be empty",
                "component": "term_protector",
                "details": {"text_length": 0},
                "original_error": "ValueError: empty string"
            }
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "component": self.component,
            "details": self.details,
            "original_error": str(self.original_error) if self.original_error else None
        }


class ValidationError(HumanizerError):
    """Raised when input validation fails.

    Used for:
    - Empty or malformed input text
    - Invalid JSON structure
    - Missing required parameters
    - Out-of-range values (e.g., aggression_level > 5)
    - Type mismatches (expecting str, got int)

    Examples:
        - Empty text provided to paraphrasing tool
        - Glossary JSON missing "tier1" field
        - Invalid aggression level (6, but max is 5)
        - Composition sum ≠ 100% in alloy specification
    """

    def __init__(
        self,
        message: str,
        component: str = "validator",
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize ValidationError."""
        super().__init__(
            message=message,
            component=component,
            details=details,
            original_error=original_error
        )


class ProcessingError(HumanizerError):
    """Raised when a tool fails during execution.

    Used for:
    - spaCy NLP pipeline failures
    - Transformer model loading errors
    - BERTScore computation failures
    - Perplexity calculation errors
    - Unexpected runtime errors

    Examples:
        - spaCy model not installed (en_core_web_trf)
        - Out of memory during BERTScore computation
        - CUDA error (GPU not available)
        - Regex pattern compilation failure
    """

    def __init__(
        self,
        message: str,
        component: str = "processor",
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize ProcessingError."""
        super().__init__(
            message=message,
            component=component,
            details=details,
            original_error=original_error
        )


class ConfigError(HumanizerError):
    """Raised when configuration loading or parsing fails.

    Used for:
    - config.yaml file not found
    - Invalid YAML syntax
    - Missing required configuration fields
    - Environment variable not set
    - Configuration value type mismatch

    Examples:
        - config.yaml missing "humanizer.max_iterations" field
        - ORIGINALITY_API_KEY environment variable not set
        - Invalid YAML (indentation error)
        - aggression_levels.gentle = "one" (expecting int)
    """

    def __init__(
        self,
        message: str,
        component: str = "config_loader",
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize ConfigError."""
        super().__init__(
            message=message,
            component=component,
            details=details,
            original_error=original_error
        )


class FileNotFoundError(HumanizerError):
    """Raised when a required file cannot be found.

    Note: Named HumanizerFileNotFoundError to avoid conflict with built-in.

    Used for:
    - Glossary file not found
    - Reference text file missing
    - Checkpoint file not found (resume operation)
    - Pattern database file missing
    - Input paper file not found

    Examples:
        - data/glossary.json not found
        - .humanizer/checkpoints/iteration_3.json missing
        - Reference text path invalid
    """

    def __init__(
        self,
        message: str,
        component: str = "file_system",
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize FileNotFoundError."""
        super().__init__(
            message=message,
            component=component,
            details=details,
            original_error=original_error
        )


class APIError(HumanizerError):
    """Raised when external API calls fail.

    Used for:
    - Claude API timeout or rate limiting
    - Originality.ai API authentication failure
    - Network connectivity issues
    - API response parsing errors
    - Quota exceeded errors

    Examples:
        - Claude API: 429 Too Many Requests (rate limited)
        - Originality.ai: Invalid API key
        - Network timeout after 60 seconds
        - API returned non-JSON response
    """

    def __init__(
        self,
        message: str,
        component: str = "api_client",
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize APIError."""
        super().__init__(
            message=message,
            component=component,
            details=details,
            original_error=original_error
        )


# Convenience function for error handling
def handle_exception(
    exception: Exception,
    component: str,
    context: Optional[Dict[str, Any]] = None
) -> HumanizerError:
    """Convert generic exceptions to HumanizerError instances.

    This function wraps generic Python exceptions in our custom
    exception types for consistent error handling.

    Args:
        exception: The original exception that was raised
        component: Name of the component where error occurred
        context: Additional context information

    Returns:
        HumanizerError: Wrapped exception with structured information

    Example:
        try:
            result = some_risky_operation()
        except Exception as e:
            raise handle_exception(
                exception=e,
                component="term_protector",
                context={"operation": "spacy_processing"}
            )
    """
    # Determine error type based on exception type
    if isinstance(exception, (ValueError, TypeError, KeyError)):
        return ValidationError(
            message=str(exception),
            component=component,
            details=context,
            original_error=exception
        )
    elif isinstance(exception, FileNotFoundError):
        return FileNotFoundError(
            message=str(exception),
            component=component,
            details=context,
            original_error=exception
        )
    elif isinstance(exception, (IOError, OSError)):
        return ProcessingError(
            message=str(exception),
            component=component,
            details=context,
            original_error=exception
        )
    else:
        # Generic processing error for unknown exception types
        return ProcessingError(
            message=str(exception),
            component=component,
            details=context,
            original_error=exception
        )
