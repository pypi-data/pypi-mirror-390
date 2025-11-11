"""
Enhanced rate limiter with enforcement.

Provides thread-safe rate limiting with token bucket algorithm
and per-provider rate management.
"""

import time
import threading
from collections import deque
from typing import Optional, Dict, Union
from omnigen.utils.logger import setup_logger

logger = setup_logger()


# Default rate limits by provider and model (RPM = Requests Per Minute)
DEFAULT_RATE_LIMITS = {
    # OpenAI - Tier 1 defaults (https://platform.openai.com/docs/guides/rate-limits)
    'openai': {
        'gpt-4o': 500,
        'gpt-4o-mini': 500,
        'gpt-4-turbo': 500,
        'gpt-4-turbo-preview': 500,
        'gpt-4': 500,
        'gpt-3.5-turbo': 3500,
        'gpt-3.5-turbo-16k': 3500,
        'o1-preview': 500,
        'o1-mini': 500,
        '_default': 500  # Fallback for unknown OpenAI models
    },
    
    # Anthropic - Standard tier
    'anthropic': {
        'claude-3-5-sonnet-20241022': 50,
        'claude-3-5-sonnet': 50,
        'claude-3-opus-20240229': 50,
        'claude-3-opus': 50,
        'claude-3-sonnet-20240229': 50,
        'claude-3-sonnet': 50,
        'claude-3-haiku-20240307': 50,
        'claude-3-haiku': 50,
        '_default': 50
    },
    
    # OpenRouter - Aggregated limits
    'openrouter': {
        '_default': 200
    },
    
    # Ultrasafe - Custom provider
    'ultrasafe': {
        '_default': 100
    },
    
    # Global fallback for unknown providers
    '_default': 60
}


def get_default_rate_limit(provider: str, model: Optional[str] = None) -> int:
    """
    Get default rate limit for provider and model combination.
    
    Args:
        provider: Provider name (e.g., 'openai', 'anthropic')
        model: Model name (e.g., 'gpt-4o-mini', 'claude-3-haiku')
        
    Returns:
        Default RPM limit for the provider/model combination
        
    Examples:
        >>> get_default_rate_limit('openai', 'gpt-4o-mini')
        500
        >>> get_default_rate_limit('anthropic', 'claude-3-haiku')
        50
        >>> get_default_rate_limit('openai')
        500
        >>> get_default_rate_limit('unknown')
        60
    """
    try:
        provider_limits = DEFAULT_RATE_LIMITS.get(provider, {})
        
        # Try model-specific limit first
        if model and model in provider_limits:
            return provider_limits[model]
        
        # Try provider default
        if '_default' in provider_limits:
            return provider_limits['_default']
        
        # Global fallback
        return DEFAULT_RATE_LIMITS['_default']
        
    except Exception as e:
        logger.error(f"Error getting default rate limit: {e}", exc_info=True)
        return 60  # Safe fallback


class RateLimiter:
    """
    Thread-safe rate limiter with enforcement.
    
    Features:
    - Enforces RPM limits with blocking
    - Token bucket algorithm
    - Per-provider rate limiting
    - Comprehensive error handling
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: Optional[int] = None,
        provider_name: str = "default"
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size (default: rpm)
            provider_name: Provider identifier
        """
        try:
            self.rpm = max(1, requests_per_minute)  # Minimum 1 RPM
            self.burst_size = burst_size or requests_per_minute
            self.provider_name = provider_name
            
            # Token bucket
            self.tokens = float(self.burst_size)
            self.last_refill = time.time()
            
            # Request tracking
            self.request_times = deque()
            self.lock = threading.Lock()
            
            # Stats
            self.total_requests = 0
            self.blocked_count = 0
            
            logger.debug(f"RateLimiter initialized for {provider_name}: {self.rpm} RPM")
        except Exception as e:
            logger.error(f"Failed to initialize RateLimiter: {e}", exc_info=True)
            # Set safe defaults
            self.rpm = 60
            self.burst_size = 60
            self.provider_name = "default"
            self.tokens = 60.0
            self.last_refill = time.time()
            self.request_times = deque()
            self.lock = threading.Lock()
            self.total_requests = 0
            self.blocked_count = 0
    
    def acquire(self, timeout: Optional[float] = 60) -> bool:
        """
        Acquire permission to make a request (BLOCKING).
        
        Args:
            timeout: Maximum time to wait (seconds)
            
        Returns:
            True if acquired, False if timeout
        """
        try:
            start_time = time.time()
            
            while True:
                try:
                    with self.lock:
                        self._refill_tokens()
                        
                        # Check if we have tokens
                        if self.tokens >= 1.0:
                            self.tokens -= 1.0
                            self.total_requests += 1
                            return True
                except Exception as e:
                    logger.error(f"Error checking tokens: {e}", exc_info=True)
                    # On error, allow request but log
                    return True
                
                # Check timeout
                try:
                    if timeout and (time.time() - start_time) >= timeout:
                        logger.warning(f"Rate limit timeout after {timeout}s for {self.provider_name}")
                        self.blocked_count += 1
                        return False
                except Exception as e:
                    logger.error(f"Error checking timeout: {e}", exc_info=True)
                    return False
                
                # Wait before retry
                try:
                    wait_time = self._calculate_wait_time()
                    time.sleep(wait_time)
                except Exception as e:
                    logger.error(f"Error during wait: {e}", exc_info=True)
                    time.sleep(1.0)  # Default wait
                    
        except Exception as e:
            logger.error(f"Critical error in acquire: {e}", exc_info=True)
            # On critical error, allow request
            return True
    
    def _refill_tokens(self):
        """Refill tokens based on elapsed time."""
        try:
            now = time.time()
            elapsed = now - self.last_refill
            
            # Calculate tokens to add (rpm / 60 = tokens per second)
            tokens_per_second = self.rpm / 60.0
            tokens_to_add = elapsed * tokens_per_second
            
            if tokens_to_add >= 1:
                self.tokens = min(float(self.burst_size), self.tokens + tokens_to_add)
                self.last_refill = now
        except Exception as e:
            logger.error(f"Error refilling tokens: {e}", exc_info=True)
            # Reset to safe state
            try:
                self.tokens = float(self.burst_size)
                self.last_refill = time.time()
            except:
                pass
    
    def _calculate_wait_time(self) -> float:
        """Calculate optimal wait time."""
        try:
            with self.lock:
                # If no tokens, calculate time until next token
                tokens_per_second = self.rpm / 60.0
                time_per_token = 1.0 / tokens_per_second
                
                # Add small random jitter to prevent thundering herd
                import random
                jitter = random.uniform(0, time_per_token * 0.1)
                
                return time_per_token + jitter
        except Exception as e:
            logger.error(f"Error calculating wait time: {e}", exc_info=True)
            return 1.0  # Default 1 second wait
    
    def record_request(self):
        """Record a successful request."""
        try:
            with self.lock:
                self.request_times.append(time.time())
                self._cleanup_old_requests()
        except Exception as e:
            logger.error(f"Error recording request: {e}", exc_info=True)
    
    def get_current_rpm(self) -> int:
        """Get current requests per minute."""
        try:
            with self.lock:
                self._cleanup_old_requests()
                return len(self.request_times)
        except Exception as e:
            logger.error(f"Error getting current RPM: {e}", exc_info=True)
            return 0
    
    def get_rpm(self) -> int:
        """
        Get current requests per minute (alias for get_current_rpm).
        
        Returns:
            Current RPM count
        """
        return self.get_current_rpm()
    
    def _cleanup_old_requests(self):
        """Remove requests older than 1 minute."""
        try:
            cutoff = time.time() - 60
            while self.request_times and self.request_times[0] < cutoff:
                self.request_times.popleft()
        except Exception as e:
            logger.error(f"Error cleaning up requests: {e}", exc_info=True)
            # Clear all on error
            try:
                self.request_times.clear()
            except:
                pass
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        try:
            with self.lock:
                current_rpm = self.get_current_rpm()
                utilization = (current_rpm / self.rpm * 100) if self.rpm > 0 else 0
                
                return {
                    'provider': self.provider_name,
                    'rpm_limit': self.rpm,
                    'current_rpm': current_rpm,
                    'tokens_available': int(self.tokens),
                    'total_requests': self.total_requests,
                    'blocked_count': self.blocked_count,
                    'utilization': utilization
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return {
                'provider': self.provider_name,
                'error': str(e)
            }


class ConcurrencyLimiter:
    """
    Simple concurrency limiter using semaphore.
    Limits the number of concurrent API calls.
    
    This is simpler and more intuitive than RPM-based rate limiting.
    Use when you want to control concurrent calls rather than requests per minute.
    
    Features:
    - Thread-safe semaphore-based limiting
    - Acquire/release pattern for concurrent control
    - Statistics tracking
    - Configurable timeout on acquire
    
    Example:
        limiter = ConcurrencyLimiter(max_concurrent=50)
        if limiter.acquire(timeout=120):
            try:
                # Make API call
                response = api_call()
            finally:
                limiter.release()
    """
    
    def __init__(self, max_concurrent: int, name: str = "default"):
        """
        Initialize concurrency limiter.
        
        Args:
            max_concurrent: Maximum number of concurrent calls allowed
            name: Identifier for this limiter (e.g., 'openai_user_followup')
        """
        try:
            self.max_concurrent = max(1, max_concurrent)  # Minimum 1
            self.name = name
            self.semaphore = threading.Semaphore(self.max_concurrent)
            self.active_count = 0
            self.total_requests = 0
            self.lock = threading.Lock()
            
            logger.debug(f"ConcurrencyLimiter initialized for {name}: max {self.max_concurrent} concurrent calls")
        except Exception as e:
            logger.error(f"Failed to initialize ConcurrencyLimiter: {e}", exc_info=True)
            # Set safe defaults
            self.max_concurrent = 1
            self.name = name
            self.semaphore = threading.Semaphore(1)
            self.active_count = 0
            self.total_requests = 0
            self.lock = threading.Lock()
    
    def acquire(self, timeout: Optional[float] = 120) -> bool:
        """
        Acquire permission to make a request (blocking until slot available).
        
        Args:
            timeout: Maximum time to wait in seconds (default: 120)
            
        Returns:
            True if acquired, False if timeout
        """
        try:
            acquired = self.semaphore.acquire(timeout=timeout)
            if acquired:
                with self.lock:
                    self.active_count += 1
                    self.total_requests += 1
            else:
                logger.warning(f"Concurrency limit timeout after {timeout}s for {self.name}")
            return acquired
        except Exception as e:
            logger.error(f"Error acquiring concurrency slot: {e}", exc_info=True)
            # On error, allow request
            return True
    
    def release(self):
        """Release the semaphore slot after request completes."""
        try:
            self.semaphore.release()
            with self.lock:
                self.active_count -= 1
        except Exception as e:
            logger.error(f"Error releasing concurrency slot: {e}", exc_info=True)
    
    def get_current_rpm(self) -> int:
        """
        Get current RPM (returns 0 for concurrency limiters).
        
        Note: Concurrency limiters don't track RPM, they track concurrent calls.
        This method exists for compatibility with ProviderRateLimitManager.get_rpm().
        
        Returns:
            0 (concurrency limiters don't measure RPM)
        """
        return 0
    
    def record_request(self):
        """
        Record a request (no-op for concurrency limiters).
        
        Note: Concurrency limiters use semaphores and don't need explicit request recording.
        This method exists for compatibility with the RateLimiter interface.
        """
        pass
    
    def get_stats(self) -> dict:
        """Get current concurrency statistics."""
        try:
            with self.lock:
                return {
                    'max_concurrent': self.max_concurrent,
                    'active_calls': self.active_count,
                    'total_requests': self.total_requests,
                    'available_slots': self.max_concurrent - self.active_count
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return {
                'provider': self.name,
                'error': str(e)
            }


class ProviderRateLimitManager:
    """
    Manage rate limiters for multiple providers.
    
    Each provider gets its own rate limiter with specific limits.
    Supports per-provider, per-model, and shared key configurations.
    Thread-safe with comprehensive error handling.
    """
    
    def __init__(self):
        """Initialize rate limit manager."""
        try:
            self.limiters: Dict[str, Union[RateLimiter, ConcurrencyLimiter]] = {}
            self.lock = threading.Lock()
            logger.info("ProviderRateLimitManager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ProviderRateLimitManager: {e}", exc_info=True)
            self.limiters = {}
            self.lock = threading.Lock()
    
    def get_limiter(
        self,
        provider_name: str,
        provider_config: Optional[Dict] = None,
        role: Optional[str] = None
    ) -> Union[RateLimiter, ConcurrencyLimiter]:
        """
        Get or create rate limiter for provider.
        
        Supports two types of limiting:
        1. Concurrency-based (max_concurrent_calls) - simpler, limits concurrent requests
        2. RPM-based (rate_limit_rpm) - traditional rate limiting
        
        If both are specified, concurrency limiting takes precedence.
        
        Args:
            provider_name: Provider name (e.g., 'openai', 'anthropic')
            provider_config: Optional provider configuration dict with:
                - max_concurrent_calls: Maximum concurrent API calls (creates ConcurrencyLimiter)
                - rate_limit_rpm: Custom RPM limit (creates RateLimiter, overrides defaults)
                - rate_limit_shared_key: Shared key for pooling limits across roles
                - model: Model name for auto-detection
            role: Optional role name for independent rate limiters per role
            
        Returns:
            ConcurrencyLimiter or RateLimiter instance
            
        Examples:
            # Concurrency limiting (recommended for simplicity)
            limiter = manager.get_limiter('openai', {'max_concurrent_calls': 50}, 'user_followup')
            # → Creates: openai_user_followup with max 50 concurrent calls
            
            # RPM-based limiting
            limiter = manager.get_limiter('openai', {'rate_limit_rpm': 300}, 'user_followup')
            # → Creates: openai_user_followup with 300 RPM
            
            # Auto-detect from model
            limiter = manager.get_limiter('openai', {'model': 'gpt-4o-mini'}, 'user_followup')
            # → Creates: openai_gpt-4o-mini_user_followup with 500 RPM
            
            # Shared key
            limiter = manager.get_limiter('openai', {'rate_limit_shared_key': 'my_key'})
            # → Creates: my_key with auto-detected RPM (reused across roles)
        """
        try:
            with self.lock:
                # Determine rate limiter key
                limiter_key = self._get_limiter_key(provider_name, provider_config, role)
                
                # Return existing limiter if already created
                if limiter_key in self.limiters:
                    return self.limiters[limiter_key]
                
                # Check for concurrency limiting first (takes precedence)
                if provider_config and 'max_concurrent_calls' in provider_config:
                    max_concurrent = provider_config['max_concurrent_calls']
                    if max_concurrent and isinstance(max_concurrent, (int, float)) and max_concurrent > 0:
                        # Create concurrency limiter
                        self.limiters[limiter_key] = ConcurrencyLimiter(
                            max_concurrent=int(max_concurrent),
                            name=limiter_key
                        )
                        
                        model_info = f"model={provider_config.get('model')}" if 'model' in provider_config else "no model specified"
                        logger.info(
                            f"Created concurrency limiter: '{limiter_key}' with max {int(max_concurrent)} concurrent calls "
                            f"(provider={provider_name}, {model_info})"
                        )
                        
                        return self.limiters[limiter_key]
                
                # Fall back to RPM-based rate limiting
                rpm = self._get_rpm_limit(provider_name, provider_config)
                
                # Create new RPM-based limiter
                self.limiters[limiter_key] = RateLimiter(
                    requests_per_minute=rpm,
                    provider_name=limiter_key
                )
                
                model_info = f"model={provider_config.get('model')}" if provider_config and 'model' in provider_config else "no model specified"
                logger.info(
                    f"Created rate limiter: '{limiter_key}' with {rpm} RPM "
                    f"(provider={provider_name}, {model_info})"
                )
                
                return self.limiters[limiter_key]
                
        except Exception as e:
            logger.error(f"Error getting limiter for {provider_name}: {e}", exc_info=True)
            # Return a default limiter
            try:
                return RateLimiter(requests_per_minute=60, provider_name=provider_name)
            except:
                # Last resort - create minimal limiter
                limiter = object.__new__(RateLimiter)
                limiter.rpm = 60
                limiter.provider_name = provider_name
                return limiter
    
    def _get_limiter_key(
        self,
        provider_name: str,
        provider_config: Optional[Dict],
        role: Optional[str]
    ) -> str:
        """
        Generate unique rate limiter key.
        
        Priority:
        1. User-specified shared key (for sharing limits across roles)
        2. Provider + Model + Role (default - independent limits per role)
        3. Provider + Role (if no model specified)
        """
        try:
            # Check for shared key
            if provider_config and 'rate_limit_shared_key' in provider_config:
                shared_key = provider_config['rate_limit_shared_key']
                if shared_key:
                    return str(shared_key)
            
            # Build independent key: provider_model_role
            parts = [provider_name]
            
            if provider_config and 'model' in provider_config:
                # Sanitize model name for use in key
                model = str(provider_config['model']).replace('/', '_').replace(':', '_')
                parts.append(model)
            
            if role:
                parts.append(role)
            
            return '_'.join(parts)
            
        except Exception as e:
            logger.error(f"Error generating limiter key: {e}", exc_info=True)
            return f"{provider_name}_default"
    
    def _get_rpm_limit(self, provider_name: str, provider_config: Optional[Dict]) -> int:
        """
        Determine RPM limit from config or defaults.
        
        Priority:
        1. User-specified rate_limit_rpm in config
        2. Auto-detect from provider + model using DEFAULT_RATE_LIMITS
        3. Provider default
        4. Global default (60 RPM)
        """
        try:
            # User-specified custom RPM
            if provider_config and 'rate_limit_rpm' in provider_config:
                custom_rpm = provider_config['rate_limit_rpm']
                if custom_rpm and isinstance(custom_rpm, (int, float)) and custom_rpm > 0:
                    return int(custom_rpm)
            
            # Auto-detect from model
            model = provider_config.get('model') if provider_config else None
            rpm = get_default_rate_limit(provider_name, model)
            
            return rpm
            
        except Exception as e:
            logger.error(f"Error determining RPM limit: {e}", exc_info=True)
            return 60  # Safe fallback
    
    def acquire(self, provider_name: str, timeout: float = 60) -> bool:
        """Acquire permission for provider (backward compatibility)."""
        try:
            limiter = self.get_limiter(provider_name)
            return limiter.acquire(timeout=timeout)
        except Exception as e:
            logger.error(f"Error acquiring rate limit for {provider_name}: {e}", exc_info=True)
            # On error, allow request
            return True
    
    def record_request(self, provider_name: str):
        """Record successful request (backward compatibility)."""
        try:
            limiter = self.get_limiter(provider_name)
            limiter.record_request()
        except Exception as e:
            logger.error(f"Error recording request for {provider_name}: {e}", exc_info=True)
    
    def get_rpm(self) -> int:
        """
        Get aggregate current RPM across all providers.
        
        Returns:
            Total current requests per minute across all limiters
        """
        try:
            with self.lock:
                total_rpm = sum(
                    limiter.get_current_rpm()
                    for limiter in self.limiters.values()
                )
                return total_rpm
        except Exception as e:
            logger.error(f"Error getting aggregate RPM: {e}", exc_info=True)
            return 0
    
    def get_all_stats(self) -> Dict[str, dict]:
        """Get stats for all providers."""
        try:
            with self.lock:
                return {
                    name: limiter.get_stats()
                    for name, limiter in self.limiters.items()
                }
        except Exception as e:
            logger.error(f"Error getting all stats: {e}", exc_info=True)
            return {}