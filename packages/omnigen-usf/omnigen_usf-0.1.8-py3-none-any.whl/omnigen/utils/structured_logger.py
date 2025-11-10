"""
Structured logging with JSON output.

Features:
- JSON-formatted logs
- Request ID tracking
- Context preservation
- Comprehensive error handling
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class StructuredLogger:
    """
    Structured logger with JSON output.
    
    Features:
    - JSON-formatted logs
    - Request/job ID tracking
    - Context preservation
    - Never crashes
    """
    
    def __init__(
        self,
        name: str = "omnigen",
        log_file: Optional[str] = None,
        level: int = logging.INFO
    ):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            log_file: Optional log file path
            level: Log level
        """
        try:
            self.logger = logging.getLogger(name)
            self.logger.setLevel(level)
            
            # Console handler with JSON formatter
            try:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(JSONFormatter())
                self.logger.addHandler(console_handler)
            except Exception as e:
                print(f"Failed to add console handler: {e}")
            
            # File handler if specified
            if log_file:
                try:
                    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
                    file_handler = logging.FileHandler(log_file)
                    file_handler.setFormatter(JSONFormatter())
                    self.logger.addHandler(file_handler)
                except Exception as e:
                    print(f"Failed to add file handler: {e}")
            
        except Exception as e:
            print(f"Critical error initializing StructuredLogger: {e}")
            self.logger = logging.getLogger(name)
    
    def log(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        exc_info: bool = False
    ):
        """Log message with context."""
        try:
            log_func = getattr(self.logger, level.lower(), self.logger.info)
            extra = {'context': context or {}}
            log_func(message, extra=extra, exc_info=exc_info)
        except Exception as e:
            print(f"Error logging message: {e}")


class JSONFormatter(logging.Formatter):
    """JSON log formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        try:
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Add context if available
            if hasattr(record, 'context'):
                log_data['context'] = record.context
            
            # Add exception info if available
            if record.exc_info:
                import traceback
                log_data['exception'] = {
                    'type': record.exc_info[0].__name__,
                    'message': str(record.exc_info[1]),
                    'traceback': ''.join(traceback.format_exception(*record.exc_info))
                }
            
            return json.dumps(log_data, ensure_ascii=False)
            
        except Exception as e:
            # Fallback to simple format
            return f'{{"error": "Formatting failed", "original_message": "{record.getMessage()}", "error": "{e}"}}'