"""
MongoDB-based real-time monitoring system.

Features:
- Real-time metrics for unlimited users/sessions
- Complete workspace isolation (zero data mixing)
- Automatic background updates
- Comprehensive error handling
"""

import time
import uuid
import pymongo
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from threading import Thread, Lock
from omnigen.utils.logger import setup_logger

# Safe import for psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger = setup_logger()
    logger.warning("psutil not available, resource monitoring disabled")

logger = setup_logger()


class MongoDBMonitor:
    """
    Real-time MongoDB monitoring for unlimited concurrent users/sessions.
    
    Features:
    - Zero data mixing (workspace isolation)
    - Real-time metrics updates every 10 seconds
    - Automatic cleanup
    - Thread-safe operations
    - Comprehensive error handling (never crashes)
    """
    
    def __init__(
        self,
        connection_string: str,
        job_id: str,
        workspace_id: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize MongoDB monitor.
        
        Args:
            connection_string: MongoDB connection string
            job_id: Unique job identifier
            workspace_id: Workspace identifier (user_session format)
            user_id: User identifier
            session_id: Session identifier
            config: Job configuration
        """
        try:
            # Initialize connection
            try:
                self.client = pymongo.MongoClient(
                    connection_string,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=20000
                )
                # Test connection
                self.client.server_info()
                self.db = self.client['omnigen_monitoring']
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}", exc_info=True)
                self.client = None
                self.db = None
            
            # Collections
            if self.db is not None:
                try:
                    self.jobs_col = self.db['jobs']
                    self.metrics_col = self.db['metrics']
                    self.sessions_col = self.db['sessions']
                    self.errors_col = self.db['errors']
                    self.conversations_col = self.db['conversations']
                except Exception as e:
                    logger.error(f"Failed to initialize collections: {e}", exc_info=True)
                    self.jobs_col = None
                    self.metrics_col = None
                    self.sessions_col = None
                    self.errors_col = None
                    self.conversations_col = None
            
            # Job identifiers
            self.job_id = job_id or str(uuid.uuid4())
            self.workspace_id = workspace_id or "default"
            
            try:
                self.user_id = user_id or workspace_id.split('_')[1] if '_' in workspace_id else "unknown"
                self.session_id = session_id or workspace_id.split('_')[-1] if '_' in workspace_id else "unknown"
            except Exception as e:
                logger.warning(f"Could not parse user/session from workspace_id: {e}")
                self.user_id = "unknown"
                self.session_id = "unknown"
            
            # State
            self.config = config or {}
            self.start_time = time.time()
            self.lock = Lock()
            
            # Metrics buffer
            self.metrics_buffer = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'completed': 0,
                'partial': 0,
                'failed': 0,
                'skipped': 0,
                'latencies': [],
                'costs': 0.0
            }
            
            # Background thread for periodic updates
            self.update_interval = 10  # seconds
            self.running = True
            self.update_thread = None
            
            try:
                self.update_thread = Thread(target=self._periodic_update, daemon=True)
                self.update_thread.start()
            except Exception as e:
                logger.error(f"Failed to start update thread: {e}", exc_info=True)
            
            # Initialize job document
            try:
                if self.db is not None:
                    self._initialize_job()
                    self._update_session()
            except Exception as e:
                logger.error(f"Failed to initialize job/session: {e}", exc_info=True)
            
            logger.info(f"MongoDBMonitor initialized for job {job_id}")
            
        except Exception as e:
            logger.critical(f"Critical error initializing MongoDBMonitor: {e}", exc_info=True)
            # Set safe defaults
            self.client = None
            self.db = None
            self.job_id = job_id or "unknown"
            self.workspace_id = workspace_id or "default"
            self.user_id = "unknown"
            self.session_id = "unknown"
            self.config = {}
            self.start_time = time.time()
            self.lock = Lock()
            self.metrics_buffer = {}
            self.running = False
            self.update_thread = None
    
    def _initialize_job(self):
        """Create initial job document."""
        try:
            if self.jobs_col is None:
                return
            
            job_doc = {
                'job_id': self.job_id,
                'workspace_id': self.workspace_id,
                'user_id': self.user_id,
                'session_id': self.session_id,
                'pipeline': 'conversation_extension',
                
                'status': 'pending',
                'config': self.config,
                
                'progress': {
                    'total_requested': self.config.get('generation', {}).get('num_conversations', 0),
                    'completed': 0,
                    'partial': 0,
                    'failed': 0,
                    'skipped': 0,
                    'percentage': 0.0,
                    'current_position': 0,
                    'estimated_completion': None,
                    'time_remaining_seconds': None
                },
                
                'performance': {
                    'conversations_per_second': 0.0,
                    'avg_api_latency_ms': 0.0,
                    'total_tokens_used': 0,
                    'estimated_cost_usd': 0.0
                },
                
                'timestamps': {
                    'created_at': datetime.utcnow(),
                    'started_at': None,
                    'last_updated': datetime.utcnow(),
                    'completed_at': None
                },
                
                'checkpoint': {
                    'enabled': self.config.get('checkpoint', {}).get('enabled', True),
                    'last_checkpoint_at': None,
                    'checkpoint_file': self.config.get('checkpoint', {}).get('checkpoint_file', '')
                },
                
                'output': {
                    'output_file': self.config.get('storage', {}).get('output_file', ''),
                    'failed_file': self.config.get('storage', {}).get('failed_file', ''),
                    'total_size_bytes': 0
                }
            }
            
            self.jobs_col.replace_one(
                {'job_id': self.job_id},
                job_doc,
                upsert=True
            )
            logger.debug(f"Job document initialized: {self.job_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize job document: {e}", exc_info=True)
    
    def _update_session(self):
        """Update session document."""
        try:
            if self.sessions_col is None:
                return
            
            self.sessions_col.update_one(
                {'session_id': self.session_id},
                {
                    '$set': {
                        'user_id': self.user_id,
                        'last_active': datetime.utcnow()
                    },
                    '$addToSet': {
                        'active_jobs': self.job_id
                    },
                    '$inc': {
                        'total_jobs_lifetime': 1
                    },
                    '$setOnInsert': {
                        'created_at': datetime.utcnow(),
                        'stats_lifetime': {
                            'total_conversations': 0,
                            'total_cost_usd': 0.0,
                            'total_time_hours': 0.0
                        },
                        'current_activity': {
                            'active_workers': 0,
                            'conversations_in_progress': 0,
                            'last_activity': datetime.utcnow()
                        }
                    }
                },
                upsert=True
            )
            logger.debug(f"Session updated: {self.session_id}")
            
        except Exception as e:
            logger.error(f"Failed to update session: {e}", exc_info=True)
    
    def start_job(self):
        """Mark job as started."""
        try:
            if self.jobs_col is None:
                return
            
            self.jobs_col.update_one(
                {'job_id': self.job_id},
                {
                    '$set': {
                        'status': 'running',
                        'timestamps.started_at': datetime.utcnow(),
                        'timestamps.last_updated': datetime.utcnow()
                    }
                }
            )
            logger.info(f"Job {self.job_id} started")
            
        except Exception as e:
            logger.error(f"Failed to start job: {e}", exc_info=True)
    
    def record_conversation(
        self,
        conversation_id: int,
        position: int,
        content_hash: str,
        status: str,
        conversations: list,
        processing_time_ms: float,
        tokens: int = 0,
        cost: float = 0.0,
        error: Optional[str] = None
    ):
        """
        Record a completed/failed conversation.
        
        Args:
            conversation_id: Conversation ID
            position: Position in dataset
            content_hash: Content hash
            status: 'completed', 'partial', or 'failed'
            conversations: Conversation messages
            processing_time_ms: Processing time in milliseconds
            tokens: Total tokens used
            cost: Cost in USD
            error: Error message if failed
        """
        try:
            with self.lock:
                # Update buffer
                if status == 'completed':
                    self.metrics_buffer['completed'] = self.metrics_buffer.get('completed', 0) + 1
                    self.metrics_buffer['successful_requests'] = self.metrics_buffer.get('successful_requests', 0) + 1
                elif status == 'partial':
                    self.metrics_buffer['partial'] = self.metrics_buffer.get('partial', 0) + 1
                elif status == 'failed':
                    self.metrics_buffer['failed'] = self.metrics_buffer.get('failed', 0) + 1
                    self.metrics_buffer['failed_requests'] = self.metrics_buffer.get('failed_requests', 0) + 1
                elif status == 'skipped':
                    self.metrics_buffer['skipped'] = self.metrics_buffer.get('skipped', 0) + 1
                
                if 'latencies' not in self.metrics_buffer:
                    self.metrics_buffer['latencies'] = []
                self.metrics_buffer['latencies'].append(processing_time_ms)
                self.metrics_buffer['costs'] = self.metrics_buffer.get('costs', 0.0) + cost
            
            # Save conversation to MongoDB (optional)
            try:
                if self.conversations_col is not None and status in ['completed', 'partial']:
                    conv_doc = {
                        'job_id': self.job_id,
                        'workspace_id': self.workspace_id,
                        'conversation_id': conversation_id,
                        'status': status,
                        'metadata': {
                            'position': position,
                            'content_hash': content_hash,
                            'generated_at': datetime.utcnow(),
                            'processing_time_ms': processing_time_ms
                        },
                        'conversations': conversations,
                        'stats': {
                            'num_turns': sum(1 for m in conversations if m.get('role') == 'user'),
                            'num_messages': len(conversations),
                            'total_tokens': tokens,
                            'cost_usd': cost
                        }
                    }
                    
                    self.conversations_col.insert_one(conv_doc)
            except Exception as e:
                logger.warning(f"Failed to save conversation to MongoDB: {e}")
                
        except Exception as e:
            logger.error(f"Error recording conversation: {e}", exc_info=True)
    
    def record_error(
        self,
        error_type: str,
        severity: str,
        message: str,
        conversation_data: Dict[str, Any],
        error_details: Dict[str, Any],
        action_taken: str
    ):
        """
        Record an error.
        
        Args:
            error_type: Type of error
            severity: Severity level
            message: Error message
            conversation_data: Conversation being processed
            error_details: Detailed error information
            action_taken: Action taken
        """
        try:
            if self.errors_col is None:
                return
            
            error_doc = {
                'job_id': self.job_id,
                'workspace_id': self.workspace_id,
                'error_id': f"err_{self.job_id}_{int(time.time()*1000)}",
                'timestamp': datetime.utcnow(),
                'error_type': error_type,
                'severity': severity,
                'conversation': conversation_data,
                'error_details': {
                    'message': message,
                    **error_details
                },
                'action_taken': action_taken
            }
            
            self.errors_col.insert_one(error_doc)
            
            with self.lock:
                self.metrics_buffer['failed_requests'] = self.metrics_buffer.get('failed_requests', 0) + 1
                
        except Exception as e:
            logger.error(f"Failed to record error: {e}", exc_info=True)
    
    def update_progress(self, current_position: int, total_processed: int):
        """Update job progress."""
        try:
            if self.jobs_col is None:
                return
            
            total_requested = self.config.get('generation', {}).get('num_conversations', 0)
            percentage = (total_processed / total_requested * 100) if total_requested > 0 else 0
            
            # Calculate estimates
            elapsed_time = time.time() - self.start_time
            if total_processed > 0:
                rate = total_processed / elapsed_time
                remaining = total_requested - total_processed
                time_remaining = remaining / rate if rate > 0 else None
                estimated_completion = datetime.utcnow() + timedelta(seconds=time_remaining) if time_remaining else None
            else:
                time_remaining = None
                estimated_completion = None
            
            self.jobs_col.update_one(
                {'job_id': self.job_id},
                {
                    '$set': {
                        'progress.current_position': current_position,
                        'progress.percentage': percentage,
                        'progress.estimated_completion': estimated_completion,
                        'progress.time_remaining_seconds': time_remaining,
                        'timestamps.last_updated': datetime.utcnow()
                    }
                }
            )
        except Exception as e:
            logger.error(f"Failed to update progress: {e}", exc_info=True)
    
    def _periodic_update(self):
        """Periodic background update of metrics."""
        while self.running:
            try:
                time.sleep(self.update_interval)
                self._flush_metrics()
            except Exception as e:
                logger.error(f"Error in periodic update: {e}", exc_info=True)
    
    def _flush_metrics(self):
        """Flush metrics buffer to MongoDB."""
        try:
            if self.metrics_col is None or self.jobs_col is None:
                return
            
            with self.lock:
                if not self.metrics_buffer.get('latencies'):
                    return
                
                # Calculate metrics safely
                try:
                    latencies = self.metrics_buffer['latencies']
                    avg_latency = sum(latencies) / len(latencies) if latencies else 0
                    sorted_latencies = sorted(latencies)
                    p50_latency = sorted_latencies[len(sorted_latencies) // 2] if sorted_latencies else 0
                    p95_latency = sorted_latencies[int(len(sorted_latencies) * 0.95)] if sorted_latencies else 0
                    p99_latency = sorted_latencies[int(len(sorted_latencies) * 0.99)] if sorted_latencies else 0
                except Exception as e:
                    logger.warning(f"Error calculating latency metrics: {e}")
                    avg_latency = p50_latency = p95_latency = p99_latency = 0
                
                # Calculate throughput
                try:
                    elapsed_time = time.time() - self.start_time
                    total_processed = (
                        self.metrics_buffer.get('completed', 0) +
                        self.metrics_buffer.get('partial', 0) +
                        self.metrics_buffer.get('failed', 0) +
                        self.metrics_buffer.get('skipped', 0)
                    )
                    
                    rate_per_second = total_processed / elapsed_time if elapsed_time > 0 else 0
                    rate_per_minute = rate_per_second * 60
                except Exception as e:
                    logger.warning(f"Error calculating throughput: {e}")
                    rate_per_second = rate_per_minute = 0
                
                # System resource usage
                try:
                    if PSUTIL_AVAILABLE:
                        import os
                        process = psutil.Process(os.getpid())
                        memory_mb = process.memory_info().rss / 1024 / 1024
                        cpu_percent = process.cpu_percent(interval=0.1)
                    else:
                        memory_mb = 0
                        cpu_percent = 0
                except Exception as e:
                    logger.warning(f"Error getting resource usage: {e}")
                    memory_mb = cpu_percent = 0
                
                # Metrics document
                try:
                    metrics_doc = {
                        'job_id': self.job_id,
                        'workspace_id': self.workspace_id,
                        'timestamp': datetime.utcnow(),
                        
                        'throughput': {
                            'conversations_per_minute': rate_per_minute,
                            'conversations_per_second': rate_per_second,
                            'tokens_per_minute': 0
                        },
                        
                        'api_metrics': {
                            'total_requests': self.metrics_buffer.get('total_requests', 0),
                            'successful_requests': self.metrics_buffer.get('successful_requests', 0),
                            'failed_requests': self.metrics_buffer.get('failed_requests', 0),
                            'avg_latency_ms': avg_latency,
                            'p50_latency_ms': p50_latency,
                            'p95_latency_ms': p95_latency,
                            'p99_latency_ms': p99_latency
                        },
                        
                        'resource_usage': {
                            'active_workers': 0,
                            'queue_size': 0,
                            'memory_mb': memory_mb,
                            'cpu_percent': cpu_percent
                        },
                        
                        'cost': {
                            'total_cost_usd': self.metrics_buffer.get('costs', 0.0),
                            'cost_per_conversation': (
                                self.metrics_buffer.get('costs', 0.0) / total_processed
                                if total_processed > 0 else 0
                            )
                        },
                        
                        'errors': {
                            'rate_limit_hits': 0,
                            'timeout_errors': 0,
                            'api_errors': 0,
                            'validation_errors': 0
                        }
                    }
                    
                    # Insert metrics
                    self.metrics_col.insert_one(metrics_doc)
                    
                    # Update job document
                    self.jobs_col.update_one(
                        {'job_id': self.job_id},
                        {
                            '$set': {
                                'progress.completed': self.metrics_buffer.get('completed', 0),
                                'progress.partial': self.metrics_buffer.get('partial', 0),
                                'progress.failed': self.metrics_buffer.get('failed', 0),
                                'progress.skipped': self.metrics_buffer.get('skipped', 0),
                                'performance.conversations_per_second': rate_per_second,
                                'performance.avg_api_latency_ms': avg_latency,
                                'performance.estimated_cost_usd': self.metrics_buffer.get('costs', 0.0),
                                'timestamps.last_updated': datetime.utcnow()
                            }
                        }
                    )
                except Exception as e:
                    logger.error(f"Failed to insert metrics: {e}", exc_info=True)
                    
        except Exception as e:
            logger.error(f"Critical error in _flush_metrics: {e}", exc_info=True)
    
    def complete_job(self, status: str = 'completed'):
        """Mark job as completed."""
        try:
            self._flush_metrics()
            
            if self.jobs_col is None:
                return
            
            self.jobs_col.update_one(
                {'job_id': self.job_id},
                {
                    '$set': {
                        'status': status,
                        'timestamps.completed_at': datetime.utcnow(),
                        'timestamps.last_updated': datetime.utcnow()
                    }
                }
            )
            
            # Update session
            try:
                if self.sessions_col is not None:
                    total_time_hours = (time.time() - self.start_time) / 3600
                    total_conversations = (
                        self.metrics_buffer.get('completed', 0) +
                        self.metrics_buffer.get('partial', 0)
                    )
                    
                    self.sessions_col.update_one(
                        {'session_id': self.session_id},
                        {
                            '$pull': {'active_jobs': self.job_id},
                            '$inc': {
                                'stats_lifetime.total_conversations': total_conversations,
                                'stats_lifetime.total_cost_usd': self.metrics_buffer.get('costs', 0.0),
                                'stats_lifetime.total_time_hours': total_time_hours
                            }
                        }
                    )
            except Exception as e:
                logger.warning(f"Failed to update session on completion: {e}")
            
            self.running = False
            logger.info(f"Job {self.job_id} completed with status: {status}")
            
        except Exception as e:
            logger.error(f"Failed to complete job: {e}", exc_info=True)
            try:
                self.running = False
            except:
                pass
    
    def close(self):
        """Close MongoDB connection."""
        try:
            self.running = False
            
            if self.update_thread and self.update_thread.is_alive():
                try:
                    self.update_thread.join(timeout=5)
                except Exception as e:
                    logger.warning(f"Error joining update thread: {e}")
            
            if self.client:
                try:
                    self.client.close()
                except Exception as e:
                    logger.warning(f"Error closing MongoDB client: {e}")
            
            logger.info("MongoDBMonitor closed")
            
        except Exception as e:
            logger.error(f"Error closing monitor: {e}", exc_info=True)