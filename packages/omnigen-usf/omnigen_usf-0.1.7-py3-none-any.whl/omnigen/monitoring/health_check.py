"""
Health check system for monitoring production status.

Provides health status for circuit breakers, rate limiters, and system resources.
"""

import time
import psutil
from typing import Dict, Any, Optional
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class HealthCheck:
    """
    System health check for production monitoring.
    
    Monitors:
    - Circuit breaker states
    - Rate limiter utilization
    - System resources (CPU, memory, disk)
    - Overall system status
    """
    
    def __init__(
        self,
        circuit_breaker_manager=None,
        rate_limit_manager=None
    ):
        """
        Initialize health check.
        
        Args:
            circuit_breaker_manager: CircuitBreakerManager instance
            rate_limit_manager: ProviderRateLimitManager instance
        """
        self.circuit_breaker_manager = circuit_breaker_manager
        self.rate_limit_manager = rate_limit_manager
        self.start_time = time.time()
    
    def check_circuit_breakers(self) -> Dict[str, Any]:
        """Check circuit breaker health."""
        if not self.circuit_breaker_manager:
            return {'status': 'not_configured', 'breakers': {}}
        
        try:
            breaker_states = self.circuit_breaker_manager.get_all_states()
            
            # Count breaker states
            open_count = sum(1 for b in breaker_states.values() if b.get('state') == 'open')
            half_open_count = sum(1 for b in breaker_states.values() if b.get('state') == 'half_open')
            closed_count = sum(1 for b in breaker_states.values() if b.get('state') == 'closed')
            
            # Determine overall status
            if open_count > 0:
                status = 'degraded'
            elif half_open_count > 0:
                status = 'recovering'
            else:
                status = 'healthy'
            
            return {
                'status': status,
                'open': open_count,
                'half_open': half_open_count,
                'closed': closed_count,
                'breakers': breaker_states
            }
        except Exception as e:
            logger.error(f"Error checking circuit breakers: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def check_rate_limiters(self) -> Dict[str, Any]:
        """Check rate limiter health."""
        if not self.rate_limit_manager:
            return {'status': 'not_configured', 'limiters': {}}
        
        try:
            limiter_stats = self.rate_limit_manager.get_all_stats()
            
            # Check for high utilization
            high_util_count = sum(
                1 for stats in limiter_stats.values()
                if stats.get('utilization', 0) > 80
            )
            
            # Determine status
            if high_util_count > 0:
                status = 'high_utilization'
            else:
                status = 'healthy'
            
            return {
                'status': status,
                'high_utilization_count': high_util_count,
                'limiters': limiter_stats
            }
        except Exception as e:
            logger.error(f"Error checking rate limiters: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free_gb = disk.free / (1024**3)
            
            # Determine status
            status = 'healthy'
            warnings = []
            
            if cpu_percent > 90:
                status = 'critical'
                warnings.append(f'CPU usage critical: {cpu_percent}%')
            elif cpu_percent > 75:
                status = 'warning'
                warnings.append(f'CPU usage high: {cpu_percent}%')
            
            if memory_percent > 90:
                status = 'critical'
                warnings.append(f'Memory usage critical: {memory_percent}%')
            elif memory_percent > 75:
                if status != 'critical':
                    status = 'warning'
                warnings.append(f'Memory usage high: {memory_percent}%')
            
            if disk_percent > 90:
                status = 'critical'
                warnings.append(f'Disk usage critical: {disk_percent}%')
            elif disk_percent > 75:
                if status == 'healthy':
                    status = 'warning'
                warnings.append(f'Disk usage high: {disk_percent}%')
            
            return {
                'status': status,
                'warnings': warnings,
                'cpu_percent': round(cpu_percent, 2),
                'memory_percent': round(memory_percent, 2),
                'memory_available_gb': round(memory_available_gb, 2),
                'disk_percent': round(disk_percent, 2),
                'disk_free_gb': round(disk_free_gb, 2)
            }
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_uptime(self) -> Dict[str, Any]:
        """Get system uptime."""
        try:
            uptime_seconds = time.time() - self.start_time
            uptime_hours = uptime_seconds / 3600
            uptime_days = uptime_hours / 24
            
            return {
                'uptime_seconds': round(uptime_seconds, 2),
                'uptime_hours': round(uptime_hours, 2),
                'uptime_days': round(uptime_days, 2),
                'started_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))
            }
        except Exception as e:
            logger.error(f"Error getting uptime: {e}")
            return {'error': str(e)}
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status.
        
        Returns:
            Health status dictionary with all checks
        """
        try:
            # Run all checks
            circuit_breaker_health = self.check_circuit_breakers()
            rate_limiter_health = self.check_rate_limiters()
            system_health = self.check_system_resources()
            uptime = self.get_uptime()
            
            # Determine overall status
            statuses = [
                circuit_breaker_health.get('status'),
                rate_limiter_health.get('status'),
                system_health.get('status')
            ]
            
            if 'critical' in statuses or 'error' in statuses:
                overall_status = 'unhealthy'
            elif 'degraded' in statuses or 'warning' in statuses or 'high_utilization' in statuses:
                overall_status = 'degraded'
            elif 'recovering' in statuses:
                overall_status = 'recovering'
            else:
                overall_status = 'healthy'
            
            return {
                'status': overall_status,
                'timestamp': time.time(),
                'uptime': uptime,
                'circuit_breakers': circuit_breaker_health,
                'rate_limiters': rate_limiter_health,
                'system_resources': system_health
            }
        except Exception as e:
            logger.error(f"Error getting health status: {e}", exc_info=True)
            return {
                'status': 'error',
                'timestamp': time.time(),
                'error': str(e)
            }
    
    def log_health_status(self):
        """Log current health status."""
        try:
            status = self.get_health_status()
            
            overall = status.get('status', 'unknown')
            logger.info(f"Health Check - Overall Status: {overall.upper()}")
            
            # Log warnings if any
            system = status.get('system_resources', {})
            warnings = system.get('warnings', [])
            if warnings:
                for warning in warnings:
                    logger.warning(f"  - {warning}")
            
            # Log circuit breaker issues
            cb = status.get('circuit_breakers', {})
            if cb.get('open', 0) > 0:
                logger.warning(f"  - {cb['open']} circuit breakers are OPEN")
            
            # Log rate limiter issues
            rl = status.get('rate_limiters', {})
            if rl.get('high_utilization_count', 0) > 0:
                logger.warning(f"  - {rl['high_utilization_count']} rate limiters at high utilization")
            
        except Exception as e:
            logger.error(f"Error logging health status: {e}")