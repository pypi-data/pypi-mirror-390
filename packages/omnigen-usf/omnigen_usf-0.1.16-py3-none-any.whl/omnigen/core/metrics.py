"""
Metrics collection for production monitoring (Enhancement 4).

Thread-safe metrics collector for tracking:
- Throughput (items/second)
- Processing times
- API latencies
- Error rates
- Success rates
"""

import time
import threading
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime


class MetricsCollector:
    """
    Thread-safe metrics collector for pipeline monitoring.
    
    Features:
    - Real-time throughput tracking
    - Processing time statistics (avg, median, p95, p99)
    - API latency tracking
    - Error and retry counters
    - Thread-safe operations
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.start_time = time.time()
        self.total_processed = 0
        self.total_errors = 0
        self.total_retries = 0
        self.processing_times = []
        self.api_latencies = []
        self.lock = threading.Lock()
        self.max_history = 10000  # Keep last 10k measurements for memory efficiency
    
    def record_completion(self, duration_ms: float, api_latency_ms: Optional[float] = None):
        """
        Record successful completion.
        
        Args:
            duration_ms: Total processing duration in milliseconds
            api_latency_ms: API call latency in milliseconds (optional)
        """
        with self.lock:
            self.total_processed += 1
            self.processing_times.append(duration_ms)
            
            # Keep history bounded for memory efficiency
            if len(self.processing_times) > self.max_history:
                self.processing_times = self.processing_times[-self.max_history:]
            
            if api_latency_ms is not None:
                self.api_latencies.append(api_latency_ms)
                if len(self.api_latencies) > self.max_history:
                    self.api_latencies = self.api_latencies[-self.max_history:]
    
    def record_error(self):
        """Record error occurrence."""
        with self.lock:
            self.total_errors += 1
    
    def record_retry(self):
        """Record retry attempt."""
        with self.lock:
            self.total_retries += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get current statistics.
        
        Returns:
            Dictionary containing all metrics
        """
        elapsed = time.time() - self.start_time
        # Ensure elapsed is always positive and non-zero for calculations
        safe_elapsed = max(0.001, elapsed)  # Minimum 1ms to avoid division by zero
        
        with self.lock:
            total_attempts = self.total_processed + self.total_errors
            
            stats = {
                'timestamp': datetime.utcnow().isoformat(),
                'uptime_seconds': round(elapsed, 2),
                'total_processed': self.total_processed,
                'total_errors': self.total_errors,
                'total_retries': self.total_retries,
                'throughput_per_sec': round(self.total_processed / safe_elapsed, 2),
                'error_rate': round(self.total_errors / max(1, total_attempts), 4),
                'success_rate': round(self.total_processed / max(1, total_attempts), 4),
            }
            
            # Processing time statistics
            if self.processing_times:
                stats['processing_time_ms'] = {
                    'avg': round(np.mean(self.processing_times), 2),
                    'median': round(np.median(self.processing_times), 2),
                    'p95': round(np.percentile(self.processing_times, 95), 2),
                    'p99': round(np.percentile(self.processing_times, 99), 2),
                    'min': round(np.min(self.processing_times), 2),
                    'max': round(np.max(self.processing_times), 2)
                }
            
            # API latency statistics
            if self.api_latencies:
                stats['api_latency_ms'] = {
                    'avg': round(np.mean(self.api_latencies), 2),
                    'median': round(np.median(self.api_latencies), 2),
                    'p95': round(np.percentile(self.api_latencies, 95), 2),
                    'p99': round(np.percentile(self.api_latencies, 99), 2),
                    'min': round(np.min(self.api_latencies), 2),
                    'max': round(np.max(self.api_latencies), 2)
                }
            
            return stats
    
    def print_stats(self):
        """Print formatted statistics to console."""
        stats = self.get_stats()
        
        print("\n" + "="*70)
        print("📊 PIPELINE METRICS")
        print("="*70)
        print(f"⏱️  Uptime:           {stats['uptime_seconds']:.2f}s")
        print(f"✓  Processed:         {stats['total_processed']:,}")
        print(f"✗  Errors:            {stats['total_errors']:,}")
        print(f"🔄 Retries:           {stats['total_retries']:,}")
        print(f"⚡ Throughput:        {stats['throughput_per_sec']:.2f} items/s")
        print(f"📈 Success Rate:      {stats['success_rate']*100:.2f}%")
        print(f"📉 Error Rate:        {stats['error_rate']*100:.2f}%")
        
        if 'processing_time_ms' in stats:
            pt = stats['processing_time_ms']
            print(f"\n⏱️  Processing Time (ms):")
            print(f"   Avg: {pt['avg']:.2f} | Median: {pt['median']:.2f} | P95: {pt['p95']:.2f} | P99: {pt['p99']:.2f}")
        
        if 'api_latency_ms' in stats:
            al = stats['api_latency_ms']
            print(f"🌐 API Latency (ms):")
            print(f"   Avg: {al['avg']:.2f} | Median: {al['median']:.2f} | P95: {al['p95']:.2f} | P99: {al['p99']:.2f}")
        
        print("="*70 + "\n")
    
    def reset(self):
        """Reset all metrics (useful for testing)."""
        with self.lock:
            self.start_time = time.time()
            self.total_processed = 0
            self.total_errors = 0
            self.total_retries = 0
            self.processing_times = []
            self.api_latencies = []
