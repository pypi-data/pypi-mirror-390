"""
Health check HTTP endpoint for container orchestration (Enhancement 8).

Provides HTTP endpoints for:
- /health - Basic health check
- /health/ready - Kubernetes readiness probe
- /health/live - Kubernetes liveness probe
- /metrics - JSON metrics endpoint
"""

import json
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any

logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check endpoints."""
    
    def do_GET(self):
        """Handle GET requests for health and metrics."""
        runner = self.server.runner
        
        if self.path == '/health':
            self._handle_health_check(runner)
        elif self.path == '/health/ready':
            self._handle_readiness_check(runner)
        elif self.path == '/health/live':
            self._handle_liveness_check(runner)
        elif self.path == '/metrics':
            self._handle_metrics(runner)
        elif self.path == '/stats':
            self._handle_stats(runner)
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found\n\nAvailable endpoints:\n  /health\n  /health/ready\n  /health/live\n  /metrics\n  /stats')
    
    def _handle_health_check(self, runner):
        """Basic health check - returns 200 if running."""
        is_healthy = (
            hasattr(runner, 'is_running') and 
            callable(runner.is_running) and 
            runner.is_running()
        )
        
        if is_healthy:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(503)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'UNHEALTHY')
    
    def _handle_readiness_check(self, runner):
        """Kubernetes readiness probe - checks if ready to accept requests."""
        is_ready = (
            hasattr(runner, 'is_running') and runner.is_running() and
            not (hasattr(runner, 'is_shutting_down') and runner.is_shutting_down())
        )
        
        if is_ready:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'READY')
        else:
            self.send_response(503)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'NOT_READY')
    
    def _handle_liveness_check(self, runner):
        """Kubernetes liveness probe - checks if process is alive."""
        is_alive = hasattr(runner, 'is_running') and runner.is_running()
        
        if is_alive:
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'ALIVE')
        else:
            self.send_response(503)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'DEAD')
    
    def _handle_metrics(self, runner):
        """Return metrics in JSON format."""
        if hasattr(runner, 'metrics') and runner.metrics is not None:
            try:
                metrics = runner.metrics.get_stats()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(metrics, indent=2).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f'Error getting metrics: {e}'.encode())
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Metrics not enabled')
    
    def _handle_stats(self, runner):
        """Return full pipeline stats."""
        stats = {}
        
        # Add metrics if available
        if hasattr(runner, 'metrics') and runner.metrics:
            stats['metrics'] = runner.metrics.get_stats()
        
        # Add checkpoint progress if available
        if hasattr(runner, 'checkpoint_manager') and runner.checkpoint_manager:
            try:
                progress = runner.checkpoint_manager.get_progress_summary()
                stats['progress'] = progress
            except:
                pass
        
        # Add basic info
        stats['running'] = hasattr(runner, 'is_running') and runner.is_running()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(stats, indent=2).encode())
    
    def log_message(self, format, *args):
        """Suppress default HTTP server logging."""
        pass  # Silent mode


def start_health_check_server(runner: Any, port: int = 8080):
    """
    Start health check server in background thread.
    
    Args:
        runner: Pipeline runner instance
        port: Port to listen on (default: 8080)
        
    Returns:
        HTTPServer instance
    """
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        server.runner = runner
        
        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
            name='HealthCheckServer'
        )
        thread.start()
        
        logger.info(f"✓ Health check server started on port {port}")
        logger.info(f"  Endpoints: /health, /health/ready, /health/live, /metrics, /stats")
        
        return server
        
    except OSError as e:
        if 'Address already in use' in str(e):
            logger.warning(f"Port {port} already in use, health check server not started")
        else:
            logger.error(f"Failed to start health check server: {e}")
        return None
    except Exception as e:
        logger.error(f"Error starting health check server: {e}", exc_info=True)
        return None
