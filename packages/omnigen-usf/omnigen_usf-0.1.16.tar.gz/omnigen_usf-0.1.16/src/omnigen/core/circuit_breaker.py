"""
Circuit breaker pattern for failing providers.

Prevents cascading failures by failing fast when provider is down.
"""

import time
import threading
from enum import Enum
from typing import Dict, Callable, Any
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreaker:
    """
    Circuit breaker for provider fault tolerance.
    
    Features:
    - Automatic failure detection
    - Fail-fast when provider down
    - Automatic recovery testing
    - Thread-safe operations
    - Comprehensive error handling
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
        name: str = "default"
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds before trying recovery
            success_threshold: Successes needed to close circuit
            name: Circuit breaker name
        """
        try:
            self.failure_threshold = max(1, failure_threshold)
            self.recovery_timeout = max(1, recovery_timeout)
            self.success_threshold = max(1, success_threshold)
            self.name = name
            
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.lock = threading.Lock()
            
            logger.info(f"CircuitBreaker '{name}' initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize CircuitBreaker: {e}", exc_info=True)
            # Set safe defaults
            self.failure_threshold = 5
            self.recovery_timeout = 60
            self.success_threshold = 2
            self.name = name or "default"
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        try:
            # Check if we should allow the call
            if not self._should_allow_request():
                from omnigen.core.exceptions import CircuitBreakerError
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is OPEN - provider unavailable"
                )
            
            # Execute function
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise
                
        except Exception as e:
            logger.error(f"Circuit breaker call failed: {e}", exc_info=True)
            raise
    
    def _should_allow_request(self) -> bool:
        """Check if request should be allowed."""
        try:
            with self.lock:
                if self.state == CircuitState.CLOSED:
                    return True
                
                if self.state == CircuitState.OPEN:
                    # Check if recovery timeout has passed
                    try:
                        if self.last_failure_time:
                            elapsed = time.time() - self.last_failure_time
                            if elapsed >= self.recovery_timeout:
                                logger.info(f"Circuit breaker '{self.name}' entering HALF_OPEN state")
                                self.state = CircuitState.HALF_OPEN
                                self.success_count = 0
                                return True
                    except Exception as e:
                        logger.warning(f"Error checking recovery timeout: {e}")
                    
                    return False
                
                if self.state == CircuitState.HALF_OPEN:
                    # Allow one request to test
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Error in _should_allow_request: {e}", exc_info=True)
            return True  # On error, allow request
    
    def _on_success(self):
        """Handle successful call."""
        try:
            with self.lock:
                if self.state == CircuitState.HALF_OPEN:
                    self.success_count += 1
                    if self.success_count >= self.success_threshold:
                        logger.info(f"Circuit breaker '{self.name}' closing (recovered)")
                        self.state = CircuitState.CLOSED
                        self.failure_count = 0
                        self.success_count = 0
                elif self.state == CircuitState.CLOSED:
                    # Reset failure count on success
                    self.failure_count = 0
        except Exception as e:
            logger.error(f"Error in _on_success: {e}", exc_info=True)
    
    def _on_failure(self):
        """Handle failed call."""
        try:
            with self.lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.state == CircuitState.HALF_OPEN:
                    logger.warning(f"Circuit breaker '{self.name}' opening (recovery failed)")
                    self.state = CircuitState.OPEN
                    self.success_count = 0
                elif self.state == CircuitState.CLOSED:
                    if self.failure_count >= self.failure_threshold:
                        logger.warning(
                            f"Circuit breaker '{self.name}' opening "
                            f"({self.failure_count} failures)"
                        )
                        self.state = CircuitState.OPEN
        except Exception as e:
            logger.error(f"Error in _on_failure: {e}", exc_info=True)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state."""
        try:
            with self.lock:
                return {
                    'name': self.name,
                    'state': self.state.value,
                    'failure_count': self.failure_count,
                    'success_count': self.success_count,
                    'last_failure_time': self.last_failure_time
                }
        except Exception as e:
            logger.error(f"Error getting state: {e}", exc_info=True)
            return {
                'name': self.name,
                'error': str(e)
            }
    
    def reset(self):
        """Reset circuit breaker to closed state."""
        try:
            with self.lock:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.last_failure_time = None
                logger.info(f"Circuit breaker '{self.name}' reset")
        except Exception as e:
            logger.error(f"Error resetting circuit breaker: {e}", exc_info=True)


class CircuitBreakerManager:
    """
    Manage multiple circuit breakers (one per provider).
    
    Features:
    - Per-provider circuit breakers
    - Thread-safe operations
    - Automatic recovery
    """
    
    def __init__(self):
        """Initialize circuit breaker manager."""
        try:
            self.breakers: Dict[str, CircuitBreaker] = {}
            self.lock = threading.Lock()
            logger.info("CircuitBreakerManager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize CircuitBreakerManager: {e}", exc_info=True)
            self.breakers = {}
            self.lock = threading.Lock()
    
    def get_breaker(
        self,
        provider_name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60
    ) -> CircuitBreaker:
        """Get or create circuit breaker for provider."""
        try:
            with self.lock:
                if provider_name not in self.breakers:
                    self.breakers[provider_name] = CircuitBreaker(
                        failure_threshold=failure_threshold,
                        recovery_timeout=recovery_timeout,
                        name=provider_name
                    )
                return self.breakers[provider_name]
        except Exception as e:
            logger.error(f"Error getting circuit breaker for {provider_name}: {e}", exc_info=True)
            # Try to create a default breaker as fallback
            try:
                logger.warning(f"Creating fallback circuit breaker for {provider_name}")
                return CircuitBreaker(name=provider_name)
            except Exception as fallback_error:
                logger.critical(f"Failed to create fallback circuit breaker: {fallback_error}")
                # Don't return broken object - raise error instead
                raise RuntimeError(f"Cannot create circuit breaker for {provider_name}: {e}") from e
    
    def call(
        self,
        provider_name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            provider_name: Provider name
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
        """
        try:
            breaker = self.get_breaker(provider_name)
            return breaker.call(func, *args, **kwargs)
        except Exception as e:
            logger.error(f"Circuit breaker call failed for {provider_name}: {e}", exc_info=True)
            raise
    
    def get_all_states(self) -> Dict[str, Dict]:
        """Get states of all circuit breakers."""
        try:
            with self.lock:
                return {
                    name: breaker.get_state()
                    for name, breaker in self.breakers.items()
                }
        except Exception as e:
            logger.error(f"Error getting all states: {e}", exc_info=True)
            return {}