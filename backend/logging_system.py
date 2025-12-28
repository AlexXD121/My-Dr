"""
Comprehensive Logging System for My Dr AI Medical Assistant
Implements structured logging with medical data privacy protection and performance monitoring
"""
import os
import json
import logging
import logging.config
import logging.handlers
import time
import traceback
import hashlib
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from contextlib import contextmanager
from functools import wraps
import threading
from queue import Queue, Empty

# Medical data patterns for privacy protection
MEDICAL_PATTERNS = [
    # Personal identifiers
    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
    r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone numbers
    
    # Medical record numbers
    r'\bMRN[-\s]?\d+\b',
    r'\bMR[-\s]?\d+\b',
    r'\bPatient[-\s]?ID[-\s]?\d+\b',
    
    # Specific medical terms that might be sensitive
    r'\b(?:HIV|AIDS|STD|STI|pregnancy|pregnant|abortion|mental health|depression|anxiety|suicide)\b',
    
    # Dates that might be birthdates
    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
    r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
]

COMPILED_MEDICAL_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in MEDICAL_PATTERNS]


@dataclass
class LogContext:
    """Context information for structured logging"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    ai_model: Optional[str] = None
    processing_time_ms: Optional[float] = None
    error_code: Optional[str] = None
    emergency_detected: Optional[bool] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring"""
    timestamp: str
    operation: str
    duration_ms: float
    success: bool
    error_type: Optional[str] = None
    memory_usage_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    database_queries: Optional[int] = None
    ai_response_time_ms: Optional[float] = None


class MedicalDataSanitizer:
    """Sanitizes medical data from logs to protect privacy"""
    
    def __init__(self):
        self.hash_salt = os.getenv("LOG_HASH_SALT", "mydoc-logging-salt-2024")
    
    def sanitize_message(self, message: str) -> str:
        """Sanitize log message by removing or hashing sensitive data"""
        if not isinstance(message, str):
            return str(message)
        
        sanitized = message
        
        # Replace sensitive patterns with hashed versions
        for pattern in COMPILED_MEDICAL_PATTERNS:
            matches = pattern.findall(sanitized)
            for match in matches:
                # Create a consistent hash for the same sensitive data
                hash_value = hashlib.sha256(f"{match}{self.hash_salt}".encode()).hexdigest()[:8]
                sanitized = sanitized.replace(match, f"[REDACTED-{hash_value}]")
        
        return sanitized
    
    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary data"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self.sanitize_message(value)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_message(item) if isinstance(item, str)
                    else self.sanitize_dict(item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def __init__(self):
        super().__init__()
        self.sanitizer = MedicalDataSanitizer()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        # Base log structure
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": self.sanitizer.sanitize_message(record.getMessage()),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "thread_name": record.threadName,
        }
        
        # Add context if available
        if hasattr(record, 'context') and record.context:
            log_entry["context"] = self.sanitizer.sanitize_dict(asdict(record.context))
        
        # Add performance metrics if available
        if hasattr(record, 'metrics') and record.metrics:
            log_entry["metrics"] = asdict(record.metrics)
        
        # Add exception information
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": self.sanitizer.sanitize_message(str(record.exc_info[1])) if record.exc_info[1] else None,
                "traceback": self.sanitizer.sanitize_message(self.formatException(record.exc_info))
            }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
                          'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info', 'context', 'metrics']:
                if isinstance(value, (str, int, float, bool, list, dict)):
                    if isinstance(value, str):
                        log_entry[key] = self.sanitizer.sanitize_message(value)
                    elif isinstance(value, dict):
                        log_entry[key] = self.sanitizer.sanitize_dict(value)
                    else:
                        log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


class PerformanceMonitor:
    """Monitors application performance and collects metrics"""
    
    def __init__(self):
        self.metrics_queue = Queue()
        self.active_operations = {}
        self.lock = threading.Lock()
    
    @contextmanager
    def monitor_operation(self, operation_name: str, context: Optional[LogContext] = None):
        """Context manager for monitoring operation performance"""
        start_time = time.time()
        operation_id = f"{operation_name}_{int(start_time * 1000)}"
        
        try:
            with self.lock:
                self.active_operations[operation_id] = {
                    "name": operation_name,
                    "start_time": start_time,
                    "context": context
                }
            
            yield operation_id
            
            # Success case
            duration_ms = (time.time() - start_time) * 1000
            metrics = PerformanceMetrics(
                timestamp=datetime.now(timezone.utc).isoformat(),
                operation=operation_name,
                duration_ms=duration_ms,
                success=True
            )
            
            self.metrics_queue.put(metrics)
            
        except Exception as e:
            # Error case
            duration_ms = (time.time() - start_time) * 1000
            metrics = PerformanceMetrics(
                timestamp=datetime.now(timezone.utc).isoformat(),
                operation=operation_name,
                duration_ms=duration_ms,
                success=False,
                error_type=type(e).__name__
            )
            
            self.metrics_queue.put(metrics)
            raise
            
        finally:
            with self.lock:
                self.active_operations.pop(operation_id, None)
    
    def get_metrics(self, max_items: int = 100) -> List[PerformanceMetrics]:
        """Get collected performance metrics"""
        metrics = []
        for _ in range(max_items):
            try:
                metric = self.metrics_queue.get_nowait()
                metrics.append(metric)
            except Empty:
                break
        return metrics
    
    def get_active_operations(self) -> Dict[str, Any]:
        """Get currently active operations"""
        with self.lock:
            return dict(self.active_operations)


class MedicalLogger:
    """Enhanced logger with medical data protection and structured logging"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.sanitizer = MedicalDataSanitizer()
        self.performance_monitor = PerformanceMonitor()
        self._context = threading.local()
    
    def set_context(self, context: LogContext):
        """Set logging context for current thread"""
        self._context.value = context
    
    def get_context(self) -> Optional[LogContext]:
        """Get logging context for current thread"""
        return getattr(self._context, 'value', None)
    
    def clear_context(self):
        """Clear logging context for current thread"""
        if hasattr(self._context, 'value'):
            delattr(self._context, 'value')
    
    def _log_with_context(self, level: int, message: str, context: Optional[LogContext] = None, 
                         metrics: Optional[PerformanceMetrics] = None, **kwargs):
        """Log message with context and metrics"""
        if not self.logger.isEnabledFor(level):
            return
        
        # Use provided context or thread-local context
        log_context = context or self.get_context()
        
        # Create log record
        record = self.logger.makeRecord(
            self.logger.name, level, "", 0, message, (), None
        )
        
        # Add context and metrics
        if log_context:
            record.context = log_context
        if metrics:
            record.metrics = metrics
        
        # Add extra fields
        for key, value in kwargs.items():
            setattr(record, key, value)
        
        self.logger.handle(record)
    
    def debug(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log debug message"""
        self._log_with_context(logging.DEBUG, message, context, **kwargs)
    
    def info(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log info message"""
        self._log_with_context(logging.INFO, message, context, **kwargs)
    
    def warning(self, message: str, context: Optional[LogContext] = None, **kwargs):
        """Log warning message"""
        self._log_with_context(logging.WARNING, message, context, **kwargs)
    
    def error(self, message: str, context: Optional[LogContext] = None, exc_info: bool = True, **kwargs):
        """Log error message"""
        self._log_with_context(logging.ERROR, message, context, **kwargs)
        if exc_info:
            self.logger.error(message, exc_info=True)
    
    def critical(self, message: str, context: Optional[LogContext] = None, exc_info: bool = True, **kwargs):
        """Log critical message"""
        self._log_with_context(logging.CRITICAL, message, context, **kwargs)
        if exc_info:
            self.logger.critical(message, exc_info=True)
    
    def log_medical_consultation(self, user_id: str, message: str, ai_response: str, 
                               processing_time_ms: float, ai_model: str, emergency_detected: bool = False):
        """Log medical consultation with privacy protection"""
        context = LogContext(
            user_id=user_id,
            ai_model=ai_model,
            processing_time_ms=processing_time_ms,
            emergency_detected=emergency_detected
        )
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation="medical_consultation",
            duration_ms=processing_time_ms,
            success=True,
            ai_response_time_ms=processing_time_ms
        )
        
        self.info(
            f"Medical consultation completed - Response time: {processing_time_ms:.2f}ms",
            context=context,
            metrics=metrics,
            consultation_length=len(message),
            response_length=len(ai_response),
            emergency_flag=emergency_detected
        )
    
    def log_database_operation(self, operation: str, table: str, duration_ms: float, 
                             success: bool, error: Optional[str] = None):
        """Log database operation with performance metrics"""
        metrics = PerformanceMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation=f"db_{operation}",
            duration_ms=duration_ms,
            success=success,
            error_type=error
        )
        
        if success:
            self.info(
                f"Database {operation} on {table} completed in {duration_ms:.2f}ms",
                metrics=metrics,
                table=table,
                operation_type=operation
            )
        else:
            self.error(
                f"Database {operation} on {table} failed after {duration_ms:.2f}ms: {error}",
                metrics=metrics,
                table=table,
                operation_type=operation,
                error_details=error
            )
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, 
                       duration_ms: float, user_id: Optional[str] = None, 
                       ip_address: Optional[str] = None):
        """Log API request with performance metrics"""
        context = LogContext(
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            ip_address=ip_address,
            processing_time_ms=duration_ms
        )
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation="api_request",
            duration_ms=duration_ms,
            success=200 <= status_code < 400
        )
        
        level = logging.INFO if 200 <= status_code < 400 else logging.WARNING
        self._log_with_context(
            level,
            f"{method} {endpoint} - {status_code} - {duration_ms:.2f}ms",
            context=context,
            metrics=metrics,
            status_code=status_code
        )
    
    def monitor_operation(self, operation_name: str, context: Optional[LogContext] = None):
        """Get performance monitor context manager"""
        return self.performance_monitor.monitor_operation(operation_name, context)


class LoggingSystem:
    """Central logging system configuration and management"""
    
    def __init__(self):
        self.loggers = {}
        self.is_configured = False
        self.log_directory = Path("logs")
        self.performance_monitor = PerformanceMonitor()
    
    def configure_logging(self, 
                         log_level: str = "INFO",
                         log_directory: str = "logs",
                         max_file_size: int = 100 * 1024 * 1024,  # 100MB
                         backup_count: int = 10,
                         enable_console: bool = True,
                         enable_file: bool = True):
        """Configure the logging system"""
        
        # Create log directory
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatters
        structured_formatter = StructuredFormatter()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(getattr(logging, log_level.upper()))
            root_logger.addHandler(console_handler)
        
        # File handlers
        if enable_file:
            # Application log file (structured JSON)
            app_log_file = self.log_directory / "mydoc_app.jsonl"
            app_handler = logging.handlers.RotatingFileHandler(
                app_log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            app_handler.setFormatter(structured_formatter)
            app_handler.setLevel(logging.INFO)
            root_logger.addHandler(app_handler)
            
            # Error log file
            error_log_file = self.log_directory / "mydoc_errors.jsonl"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            error_handler.setFormatter(structured_formatter)
            error_handler.setLevel(logging.ERROR)
            root_logger.addHandler(error_handler)
            
            # Performance log file
            perf_log_file = self.log_directory / "mydoc_performance.jsonl"
            perf_handler = logging.handlers.RotatingFileHandler(
                perf_log_file,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            perf_handler.setFormatter(structured_formatter)
            perf_handler.setLevel(logging.INFO)
            
            # Create performance logger
            perf_logger = logging.getLogger("performance")
            perf_logger.addHandler(perf_handler)
            perf_logger.setLevel(logging.INFO)
            perf_logger.propagate = False
        
        self.is_configured = True
        
        # Log configuration success
        logger = self.get_logger("logging_system")
        logger.info("Logging system configured successfully", 
                   log_level=log_level,
                   log_directory=str(self.log_directory),
                   console_enabled=enable_console,
                   file_enabled=enable_file)
    
    def get_logger(self, name: str) -> MedicalLogger:
        """Get or create a medical logger instance"""
        if name not in self.loggers:
            self.loggers[name] = MedicalLogger(name)
        return self.loggers[name]
    
    def get_log_files(self) -> List[Path]:
        """Get list of log files"""
        if not self.log_directory.exists():
            return []
        
        return list(self.log_directory.glob("*.jsonl")) + list(self.log_directory.glob("*.log"))
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log files"""
        if not self.log_directory.exists():
            return
        
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        
        for log_file in self.log_directory.iterdir():
            if log_file.is_file() and log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    print(f"Deleted old log file: {log_file}")
                except Exception as e:
                    print(f"Failed to delete log file {log_file}: {e}")


# Global logging system instance
logging_system = LoggingSystem()

# Convenience function for getting loggers
def get_medical_logger(name: str) -> MedicalLogger:
    """Get a medical logger instance"""
    return logging_system.get_logger(name)

# Performance monitoring decorator
def monitor_performance(operation_name: str = None):
    """Decorator for monitoring function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            logger = get_medical_logger(func.__module__)
            
            with logger.monitor_operation(op_name):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Context manager for logging context
@contextmanager
def logging_context(context: LogContext):
    """Context manager for setting logging context"""
    logger = get_medical_logger("context_manager")
    logger.set_context(context)
    try:
        yield
    finally:
        logger.clear_context()