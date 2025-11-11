"""
Enhanced exception classes for OmniGen with comprehensive error handling.

All exceptions include proper error messages, context, and recovery hints.
"""

from typing import Optional, Dict, Any


class OmniGenError(Exception):
    """Base exception for all OmniGen errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        recovery_hint: Optional[str] = None
    ):
        """
        Initialize base exception.
        
        Args:
            message: Error message
            error_code: Error code for tracking
            context: Additional context dictionary
            recovery_hint: Hint for recovery
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.recovery_hint = recovery_hint
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging."""
        try:
            return {
                'error_type': self.__class__.__name__,
                'error_code': self.error_code,
                'message': self.message,
                'context': self.context,
                'recovery_hint': self.recovery_hint
            }
        except Exception as e:
            return {
                'error_type': 'SerializationError',
                'message': f'Failed to serialize exception: {e}'
            }


# Configuration Errors
class ConfigurationError(OmniGenError):
    """Configuration-related errors."""
    pass


class InvalidConfigError(ConfigurationError):
    """Invalid configuration value."""
    pass


class MissingConfigError(ConfigurationError):
    """Missing required configuration."""
    pass


# Provider Errors
class ProviderError(OmniGenError):
    """Base provider error."""
    pass


class AuthenticationError(ProviderError):
    """Authentication failed with provider."""
    pass


class APIError(ProviderError):
    """API call failed."""
    pass


class RateLimitError(ProviderError):
    """Rate limit exceeded."""
    pass


class TimeoutError(ProviderError):
    """Request timeout."""
    pass


class NetworkError(ProviderError):
    """Network connectivity issue."""
    pass


class ServerError(ProviderError):
    """Provider server error (5xx)."""
    pass


class ModelError(ProviderError):
    """Model not available or invalid."""
    pass


# Data Errors
class DataError(OmniGenError):
    """Base data error."""
    pass


class ValidationError(DataError):
    """Data validation failed."""
    pass


class MalformedDataError(DataError):
    """Data format is malformed."""
    pass


class EmptyContentError(DataError):
    """Content is empty or null."""
    pass


class ContentFilterError(DataError):
    """Content filtered (toxic/unsafe)."""
    pass


# Storage Errors
class StorageError(OmniGenError):
    """Storage operation failed."""
    pass


class FileWriteError(StorageError):
    """Failed to write file."""
    pass


class MongoDBError(StorageError):
    """MongoDB operation failed."""
    pass


# System Errors
class SystemError(OmniGenError):
    """System-level errors."""
    pass


class OutOfMemoryError(SystemError):
    """Out of memory."""
    pass


class DiskSpaceError(SystemError):
    """Insufficient disk space."""
    pass


# Runtime Errors
class CriticalError(OmniGenError):
    """Critical error requiring job abort."""
    pass


class RetryExhaustedError(OmniGenError):
    """Maximum retries exceeded."""
    pass


class CircuitBreakerError(OmniGenError):
    """Circuit breaker is open."""
    pass


# Transient errors (safe to retry)
TRANSIENT_ERRORS = (
    RateLimitError,
    TimeoutError,
    NetworkError,
    ServerError
)


# Fatal errors (abort immediately)
FATAL_ERRORS = (
    AuthenticationError,
    OutOfMemoryError,
    DiskSpaceError,
    CriticalError
)


# Data errors (fail fast, no retry)
DATA_ERRORS = (
    ValidationError,
    MalformedDataError,
    EmptyContentError,
    ContentFilterError
)


def is_transient_error(error: Exception) -> bool:
    """Check if error is transient and safe to retry."""
    try:
        return isinstance(error, TRANSIENT_ERRORS)
    except Exception:
        return False


def is_fatal_error(error: Exception) -> bool:
    """Check if error is fatal and requires abort."""
    try:
        return isinstance(error, FATAL_ERRORS)
    except Exception:
        return True  # Unknown errors treated as fatal


def is_data_error(error: Exception) -> bool:
    """Check if error is data-related (fail fast)."""
    try:
        return isinstance(error, DATA_ERRORS)
    except Exception:
        return False


class ShutdownException(OmniGenError):
    """
    Exception raised when shutdown is detected during processing.
    
    This is NOT a failure - it indicates the conversation was interrupted
    and should be resumed later with priority.
    """
    
    def __init__(self, message: str = "Shutdown detected - conversation will be resumed"):
        super().__init__(
            message=message,
            error_code="SHUTDOWN_INTERRUPTED",
            recovery_hint="This conversation will be automatically resumed on next run"
        )