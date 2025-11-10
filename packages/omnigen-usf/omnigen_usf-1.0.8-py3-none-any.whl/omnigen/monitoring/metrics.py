"""
Production metrics collection and tracking.

Tracks request duration, success rates, token usage, and costs.
"""

import time
import threading
from collections import defaultdict, deque
from typing import Dict, Any, Optional, List
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class MetricsCollector:
    """
    Collects and aggregates production metrics.
    
    Tracks:
    - Request duration histograms
    - Success/failure rates per provider
    - Token usage and costs
    - Throughput (requests per second)
    - Error counts by type
    """
    
    def __init__(self, window_size: int = 300):
        """
        Initialize metrics collector.
        
        Args:
            window_size: Time window in seconds for rolling metrics
        """
        self.window_size = window_size
        self.lock = threading.Lock()
        
        # Request metrics
        self.request_durations = defaultdict(deque)  # provider -> deque of (timestamp, duration)
        self.request_counts = defaultdict(int)  # provider -> count
        self.success_counts = defaultdict(int)  # provider -> success count
        self.failure_counts = defaultdict(int)  # provider -> failure count
        
        # Token and cost tracking
        self.token_usage = defaultdict(int)  # provider -> total tokens
        self.estimated_costs = defaultdict(float)  # provider -> total cost
        
        # Error tracking
        self.error_counts = defaultdict(lambda: defaultdict(int))  # provider -> {error_type: count}
        
        # Conversation metrics
        self.conversations_generated = 0
        self.conversations_failed = 0
        self.conversations_partial = 0
        
        # Throughput tracking
        self.request_timestamps = deque()
        
        logger.info(f"MetricsCollector initialized with {window_size}s window")
    
    def record_request(
        self,
        provider: str,
        duration_ms: float,
        success: bool,
        tokens: int = 0,
        cost: float = 0.0,
        error_type: Optional[str] = None
    ):
        """
        Record a single request.
        
        Args:
            provider: Provider name
            duration_ms: Request duration in milliseconds
            success: Whether request succeeded
            tokens: Number of tokens used
            cost: Estimated cost in USD
            error_type: Error type if failed
        """
        try:
            with self.lock:
                timestamp = time.time()
                
                # Record duration
                self.request_durations[provider].append((timestamp, duration_ms))
                
                # Record counts
                self.request_counts[provider] += 1
                if success:
                    self.success_counts[provider] += 1
                else:
                    self.failure_counts[provider] += 1
                
                # Record tokens and cost
                if tokens > 0:
                    self.token_usage[provider] += tokens
                if cost > 0:
                    self.estimated_costs[provider] += cost
                
                # Record error
                if error_type:
                    self.error_counts[provider][error_type] += 1
                
                # Record timestamp for throughput
                self.request_timestamps.append(timestamp)
                
                # Cleanup old data
                self._cleanup_old_data()
        except Exception as e:
            logger.error(f"Error recording request metric: {e}")
    
    def record_conversation(
        self,
        status: str,
        duration_ms: float = 0,
        tokens: int = 0
    ):
        """
        Record conversation generation result.
        
        Args:
            status: 'completed', 'failed', or 'partial'
            duration_ms: Generation duration in milliseconds
            tokens: Total tokens used
        """
        try:
            with self.lock:
                if status == 'completed':
                    self.conversations_generated += 1
                elif status == 'failed':
                    self.conversations_failed += 1
                elif status == 'partial':
                    self.conversations_partial += 1
        except Exception as e:
            logger.error(f"Error recording conversation metric: {e}")
    
    def _cleanup_old_data(self):
        """Remove metrics older than window_size."""
        try:
            cutoff = time.time() - self.window_size
            
            # Cleanup request durations
            for provider in list(self.request_durations.keys()):
                durations = self.request_durations[provider]
                while durations and durations[0][0] < cutoff:
                    durations.popleft()
            
            # Cleanup request timestamps
            while self.request_timestamps and self.request_timestamps[0] < cutoff:
                self.request_timestamps.popleft()
        except Exception as e:
            logger.error(f"Error cleaning up metrics: {e}")
    
    def get_provider_metrics(self, provider: str) -> Dict[str, Any]:
        """Get metrics for specific provider."""
        try:
            with self.lock:
                self._cleanup_old_data()
                
                # Calculate duration statistics
                durations = [d[1] for d in self.request_durations[provider]]
                
                if durations:
                    avg_duration = sum(durations) / len(durations)
                    min_duration = min(durations)
                    max_duration = max(durations)
                    
                    # Calculate percentiles
                    sorted_durations = sorted(durations)
                    p50 = sorted_durations[len(sorted_durations) // 2]
                    p95 = sorted_durations[int(len(sorted_durations) * 0.95)]
                    p99 = sorted_durations[int(len(sorted_durations) * 0.99)]
                else:
                    avg_duration = min_duration = max_duration = 0
                    p50 = p95 = p99 = 0
                
                # Calculate success rate
                total = self.request_counts[provider]
                success = self.success_counts[provider]
                success_rate = (success / total * 100) if total > 0 else 0
                
                return {
                    'provider': provider,
                    'requests': {
                        'total': total,
                        'success': success,
                        'failed': self.failure_counts[provider],
                        'success_rate': round(success_rate, 2)
                    },
                    'duration_ms': {
                        'avg': round(avg_duration, 2),
                        'min': round(min_duration, 2),
                        'max': round(max_duration, 2),
                        'p50': round(p50, 2),
                        'p95': round(p95, 2),
                        'p99': round(p99, 2)
                    },
                    'tokens': {
                        'total': self.token_usage[provider],
                        'avg_per_request': round(self.token_usage[provider] / total, 2) if total > 0 else 0
                    },
                    'cost': {
                        'total_usd': round(self.estimated_costs[provider], 4),
                        'avg_per_request_usd': round(self.estimated_costs[provider] / total, 6) if total > 0 else 0
                    },
                    'errors': dict(self.error_counts[provider])
                }
        except Exception as e:
            logger.error(f"Error getting provider metrics: {e}")
            return {'provider': provider, 'error': str(e)}
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        try:
            with self.lock:
                self._cleanup_old_data()
                
                # Get provider-specific metrics
                providers = set(self.request_counts.keys())
                provider_metrics = {
                    provider: self.get_provider_metrics(provider)
                    for provider in providers
                }
                
                # Calculate throughput
                window_start = time.time() - self.window_size
                recent_requests = len(self.request_timestamps)
                actual_window = time.time() - self.request_timestamps[0] if self.request_timestamps else self.window_size
                throughput_rps = recent_requests / actual_window if actual_window > 0 else 0
                
                # Aggregate totals
                total_requests = sum(self.request_counts.values())
                total_success = sum(self.success_counts.values())
                total_failed = sum(self.failure_counts.values())
                total_tokens = sum(self.token_usage.values())
                total_cost = sum(self.estimated_costs.values())
                
                return {
                    'timestamp': time.time(),
                    'window_seconds': self.window_size,
                    'providers': provider_metrics,
                    'aggregated': {
                        'requests': {
                            'total': total_requests,
                            'success': total_success,
                            'failed': total_failed,
                            'success_rate': round(total_success / total_requests * 100, 2) if total_requests > 0 else 0
                        },
                        'throughput': {
                            'requests_per_second': round(throughput_rps, 2),
                            'requests_per_minute': round(throughput_rps * 60, 2)
                        },
                        'tokens': {
                            'total': total_tokens,
                            'avg_per_request': round(total_tokens / total_requests, 2) if total_requests > 0 else 0
                        },
                        'cost': {
                            'total_usd': round(total_cost, 4),
                            'avg_per_request_usd': round(total_cost / total_requests, 6) if total_requests > 0 else 0
                        },
                        'conversations': {
                            'generated': self.conversations_generated,
                            'failed': self.conversations_failed,
                            'partial': self.conversations_partial,
                            'total': self.conversations_generated + self.conversations_failed + self.conversations_partial
                        }
                    }
                }
        except Exception as e:
            logger.error(f"Error getting all metrics: {e}", exc_info=True)
            return {'error': str(e), 'timestamp': time.time()}
    
    def log_metrics_summary(self):
        """Log a summary of current metrics."""
        try:
            metrics = self.get_all_metrics()
            agg = metrics.get('aggregated', {})
            
            logger.info("="*60)
            logger.info("METRICS SUMMARY")
            logger.info("="*60)
            
            # Requests
            req = agg.get('requests', {})
            logger.info(f"Requests: {req.get('total', 0)} total, {req.get('success', 0)} success, {req.get('failed', 0)} failed")
            logger.info(f"Success Rate: {req.get('success_rate', 0)}%")
            
            # Throughput
            tp = agg.get('throughput', {})
            logger.info(f"Throughput: {tp.get('requests_per_second', 0)} req/s, {tp.get('requests_per_minute', 0)} req/min")
            
            # Tokens and cost
            tokens = agg.get('tokens', {})
            cost = agg.get('cost', {})
            logger.info(f"Tokens: {tokens.get('total', 0)} total, {tokens.get('avg_per_request', 0)} avg/req")
            logger.info(f"Cost: ${cost.get('total_usd', 0)} total, ${cost.get('avg_per_request_usd', 0)} avg/req")
            
            # Conversations
            convs = agg.get('conversations', {})
            logger.info(f"Conversations: {convs.get('generated', 0)} completed, {convs.get('partial', 0)} partial, {convs.get('failed', 0)} failed")
            
            logger.info("="*60)
        except Exception as e:
            logger.error(f"Error logging metrics summary: {e}")
    
    def reset(self):
        """Reset all metrics."""
        try:
            with self.lock:
                self.request_durations.clear()
                self.request_counts.clear()
                self.success_counts.clear()
                self.failure_counts.clear()
                self.token_usage.clear()
                self.estimated_costs.clear()
                self.error_counts.clear()
                self.conversations_generated = 0
                self.conversations_failed = 0
                self.conversations_partial = 0
                self.request_timestamps.clear()
                logger.info("Metrics reset")
        except Exception as e:
            logger.error(f"Error resetting metrics: {e}")