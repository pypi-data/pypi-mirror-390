"""
Centralized error handling with fail-fast strategy.

Philosophy:
- Better to skip than generate wrong data
- Save what we have before failing
- Clear error reporting
"""

import time
import random
from enum import Enum
from typing import Optional, Dict, Any
from omnigen.core.exceptions import (
    OmniGenError, ValidationError, RateLimitError, TimeoutError,
    NetworkError, ServerError, AuthenticationError, OutOfMemoryError,
    DiskSpaceError, CriticalError, is_transient_error, is_fatal_error, is_data_error
)
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class ErrorSeverity(Enum):
    """Error severity levels."""
    CRITICAL = "critical"  # System failure, abort job
    ERROR = "error"        # Data error, skip and continue
    WARNING = "warning"    # Recoverable issue, retry
    INFO = "info"          # Non-blocking issue


class ErrorType(Enum):
    """Error types with handling strategies."""
    
    # FAIL FAST - Skip immediately, no retry
    VALIDATION_ERROR = "validation_error"
    MALFORMED_DATA = "malformed_data"
    EMPTY_CONTENT = "empty_content"
    CONTENT_FILTER = "content_filter"
    
    # RETRY - Transient errors
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    SERVER_ERROR = "server_error"
    
    # FAIL PERMANENTLY - Non-retryable API errors
    AUTH_ERROR = "auth_error"
    INVALID_REQUEST = "invalid_request"
    MODEL_ERROR = "model_error"
    
    # SYSTEM ERRORS - Abort job
    OUT_OF_MEMORY = "out_of_memory"
    STORAGE_ERROR = "storage_error"
    UNKNOWN = "unknown"


class ErrorHandler:
    """
    Centralized error handling with fail-fast strategy.
    
    Features:
    - Error classification
    - Smart retry logic
    - Fail-fast on bad data
    - Comprehensive error tracking
    - Thread-safe operations
    """
    
    def __init__(self, monitor: Optional[Any] = None):
        """
        Initialize error handler.
        
        Args:
            monitor: MongoDBMonitor instance for error logging
        """
        try:
            self.monitor = monitor
            self.error_counts = {
                'validation': 0,
                'rate_limit': 0,
                'timeout': 0,
                'api_error': 0,
                'system_error': 0
            }
            logger.info("ErrorHandler initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ErrorHandler: {e}", exc_info=True)
            self.monitor = None
            self.error_counts = {}
    
    def classify_error(self, exception: Exception) -> tuple:
        """
        Classify error and determine severity.
        
        Args:
            exception: Exception to classify
            
        Returns:
            (error_type, severity) tuple
        """
        try:
            error_str = str(exception).lower()
            error_class = exception.__class__.__name__
            
            # Validation errors - FAIL FAST
            if 'validation' in error_str or 'invalid' in error_class.lower():
                return ErrorType.VALIDATION_ERROR, ErrorSeverity.ERROR
            
            if 'empty' in error_str or 'null' in error_str:
                return ErrorType.EMPTY_CONTENT, ErrorSeverity.ERROR
            
            if 'malformed' in error_str or 'parse' in error_str:
                return ErrorType.MALFORMED_DATA, ErrorSeverity.ERROR
            
            # Rate limit - RETRY
            if 'rate limit' in error_str or '429' in error_str:
                return ErrorType.RATE_LIMIT, ErrorSeverity.WARNING
            
            # Timeout - RETRY
            if 'timeout' in error_str or 'timed out' in error_str:
                return ErrorType.TIMEOUT, ErrorSeverity.WARNING
            
            # Network - RETRY
            if 'network' in error_str or 'connection' in error_str:
                return ErrorType.NETWORK_ERROR, ErrorSeverity.WARNING
            
            # Server errors - RETRY
            if any(code in error_str for code in ['500', '502', '503', '504']):
                return ErrorType.SERVER_ERROR, ErrorSeverity.WARNING
            
            # Auth errors - FAIL PERMANENTLY
            if '401' in error_str or '403' in error_str or 'auth' in error_str:
                return ErrorType.AUTH_ERROR, ErrorSeverity.CRITICAL
            
            # Bad request - FAIL FAST
            if '400' in error_str:
                return ErrorType.INVALID_REQUEST, ErrorSeverity.ERROR
            
            # System errors - ABORT
            if 'memory' in error_str or 'oom' in error_str:
                return ErrorType.OUT_OF_MEMORY, ErrorSeverity.CRITICAL
            
            if 'storage' in error_str or 'disk' in error_str:
                return ErrorType.STORAGE_ERROR, ErrorSeverity.CRITICAL
            
            # Unknown
            return ErrorType.UNKNOWN, ErrorSeverity.ERROR
            
        except Exception as e:
            logger.error(f"Error classifying exception: {e}", exc_info=True)
            return ErrorType.UNKNOWN, ErrorSeverity.ERROR
    
    def should_retry(self, error_type: ErrorType, attempt: int, max_retries: int = 3) -> bool:
        """
        Determine if error should be retried.
        
        Args:
            error_type: Type of error
            attempt: Current attempt number (1-indexed)
            max_retries: Maximum retry attempts
            
        Returns:
            True if should retry, False otherwise
        """
        try:
            # Never retry these (fail-fast)
            no_retry_types = {
                ErrorType.VALIDATION_ERROR,
                ErrorType.MALFORMED_DATA,
                ErrorType.EMPTY_CONTENT,
                ErrorType.CONTENT_FILTER,
                ErrorType.AUTH_ERROR,
                ErrorType.INVALID_REQUEST,
                ErrorType.OUT_OF_MEMORY,
                ErrorType.STORAGE_ERROR
            }
            
            if error_type in no_retry_types:
                return False
            
            # Retry transient errors
            retry_types = {
                ErrorType.RATE_LIMIT,
                ErrorType.TIMEOUT,
                ErrorType.NETWORK_ERROR,
                ErrorType.SERVER_ERROR
            }
            
            if error_type in retry_types:
                return attempt < max_retries
            
            # Unknown errors - retry once
            if error_type == ErrorType.UNKNOWN:
                return attempt < 2
            
            return False
            
        except Exception as e:
            logger.error(f"Error in should_retry: {e}", exc_info=True)
            return False  # Don't retry on error
    
    def get_wait_time(self, error_type: ErrorType, attempt: int) -> float:
        """
        Calculate wait time before retry with exponential backoff and jitter.
        
        Args:
            error_type: Type of error
            attempt: Current attempt number (1-indexed)
            
        Returns:
            Wait time in seconds
        """
        try:
            # Base wait times per error type
            base_wait = {
                ErrorType.RATE_LIMIT: 60,    # Wait 1 minute for rate limits
                ErrorType.TIMEOUT: 5,         # Wait 5 seconds for timeouts
                ErrorType.NETWORK_ERROR: 2,   # Wait 2 seconds for network
                ErrorType.SERVER_ERROR: 10    # Wait 10 seconds for server errors
            }.get(error_type, 5)
            
            # Exponential backoff
            wait = base_wait * (2 ** (attempt - 1))
            
            # Add jitter (10% random variation)
            jitter = random.uniform(0, wait * 0.1)
            
            # Cap at 5 minutes
            return min(wait + jitter, 300.0)
            
        except Exception as e:
            logger.error(f"Error calculating wait time: {e}", exc_info=True)
            return 5.0  # Default 5 seconds
    
    def handle_error(
        self,
        exception: Exception,
        conversation_data: Dict[str, Any],
        attempt: int = 1,
        max_retries: int = 3,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle error with fail-fast strategy.
        
        Args:
            exception: Exception that occurred
            conversation_data: Conversation being processed
            attempt: Current attempt number
            max_retries: Maximum retry attempts
            context: Additional context (worker_id, etc.)
            
        Returns:
            Dict with action and details
        """
        try:
            error_type, severity = self.classify_error(exception)
            
            # Determine action
            if severity == ErrorSeverity.CRITICAL:
                action = 'abort_job'
            elif self.should_retry(error_type, attempt, max_retries):
                action = 'retry'
            else:
                action = 'skip'
            
            # Update error counts
            try:
                if error_type == ErrorType.VALIDATION_ERROR:
                    self.error_counts['validation'] = self.error_counts.get('validation', 0) + 1
                elif error_type == ErrorType.RATE_LIMIT:
                    self.error_counts['rate_limit'] = self.error_counts.get('rate_limit', 0) + 1
                elif error_type == ErrorType.TIMEOUT:
                    self.error_counts['timeout'] = self.error_counts.get('timeout', 0) + 1
            except Exception as e:
                logger.warning(f"Failed to update error counts: {e}")
            
            # Log to monitor if available
            try:
                if self.monitor:
                    self.monitor.record_error(
                        error_type=error_type.value,
                        severity=severity.value,
                        message=str(exception),
                        conversation_data=conversation_data,
                        error_details={
                            'exception_class': exception.__class__.__name__,
                            'attempt': attempt,
                            'max_retries': max_retries,
                            **(context or {})
                        },
                        action_taken=action
                    )
            except Exception as e:
                logger.warning(f"Failed to record error to monitor: {e}")
            
            # Log locally
            try:
                if action == 'abort_job':
                    logger.critical(
                        f"CRITICAL ERROR - Aborting job: {exception} "
                        f"(type={error_type.value}, conversation_id={conversation_data.get('_position', 'unknown')})"
                    )
                elif action == 'skip':
                    logger.warning(
                        f"Skipping conversation {conversation_data.get('_position', 'unknown')}: "
                        f"{exception} (type={error_type.value})"
                    )
                elif action == 'retry':
                    wait_time = self.get_wait_time(error_type, attempt)
                    logger.info(
                        f"Retrying conversation {conversation_data.get('_position', 'unknown')} "
                        f"after {wait_time:.1f}s (attempt {attempt}/{max_retries}, error={error_type.value})"
                    )
            except Exception as e:
                logger.error(f"Failed to log error: {e}", exc_info=True)
            
            return {
                'action': action,
                'error_type': error_type,
                'severity': severity,
                'wait_time': self.get_wait_time(error_type, attempt) if action == 'retry' else 0,
                'message': str(exception)
            }
            
        except Exception as e:
            logger.critical(f"Critical error in handle_error: {e}", exc_info=True)
            # Return safe default - skip the conversation
            return {
                'action': 'skip',
                'error_type': ErrorType.UNKNOWN,
                'severity': ErrorSeverity.ERROR,
                'wait_time': 0,
                'message': f"Error handler failed: {e}"
            }
    
    def get_error_stats(self) -> Dict[str, int]:
        """Get error statistics."""
        try:
            return self.error_counts.copy()
        except Exception as e:
            logger.error(f"Error getting error stats: {e}", exc_info=True)
            return {}