"""
Monitoring Middleware for My Dr AI Medical Assistant
Integrates logging, performance monitoring, and alerting with FastAPI requests
"""
import time
import json
import asyncio
from datetime import datetime, timezone
from typing import Callable, Optional, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import psutil

from logging_system import get_medical_logger, LogContext, logging_context
from performance_monitoring import (
    performance_monitor, 
    record_api_request, 
    record_application_error,
    get_system_health
)
from alert_system import alert_system, check_system_alerts


class MonitoringMiddleware:
    """Middleware for comprehensive request monitoring and logging"""
    
    def __init__(self):
        self.logger = get_medical_logger("monitoring_middleware")
        self.request_count = 0
        self.error_count = 0
        self.last_health_check = 0
        self.health_check_interval = 300  # 5 minutes
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process request with comprehensive monitoring"""
        start_time = time.time()
        request_id = f"req_{int(start_time * 1000)}_{self.request_count}"
        self.request_count += 1
        
        # Extract request information
        method = request.method
        url = str(request.url)
        endpoint = request.url.path
        user_agent = request.headers.get("user-agent", "")
        ip_address = self._get_client_ip(request)
        user_id = None
        
        # Try to get user ID from request state (set by auth middleware)
        if hasattr(request.state, 'user') and request.state.user:
            user_id = getattr(request.state.user, 'id', None)
        
        # Create logging context
        context = LogContext(
            request_id=request_id,
            endpoint=endpoint,
            method=method,
            ip_address=ip_address,
            user_agent=user_agent,
            user_id=user_id
        )
        
        response = None
        status_code = 500
        error_occurred = False
        error_details = None
        
        try:
            # Set logging context for this request
            with logging_context(context):
                # Log request start
                self.logger.info(f"Request started: {method} {endpoint}",
                               request_id=request_id,
                               user_id=user_id,
                               ip_address=ip_address,
                               user_agent=user_agent)
                
                # Process request
                response = await call_next(request)
                status_code = response.status_code
                
                # Check if this is an error response
                if status_code >= 400:
                    error_occurred = True
                    self.error_count += 1
        
        except Exception as e:
            error_occurred = True
            error_details = str(e)
            self.error_count += 1
            
            # Log the error
            self.logger.error(f"Request failed: {method} {endpoint} - {error_details}",
                            request_id=request_id,
                            user_id=user_id,
                            endpoint=endpoint,
                            error_type=type(e).__name__)
            
            # Record error for monitoring
            error_context = {
                'module': 'api_request',
                'function': endpoint,
                'user_id': user_id,
                'endpoint': endpoint,
                'request_id': request_id
            }
            record_application_error(e, error_context)
            
            # Return error response
            response = JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": request_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )
            status_code = 500
        
        finally:
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Update context with processing time
            context.processing_time_ms = processing_time_ms
            
            # Log request completion
            log_level = "error" if error_occurred else "info"
            log_message = f"Request completed: {method} {endpoint} - {status_code} - {processing_time_ms:.2f}ms"
            
            if error_occurred and error_details:
                log_message += f" - Error: {error_details}"
            
            getattr(self.logger, log_level)(log_message,
                                          request_id=request_id,
                                          status_code=status_code,
                                          processing_time_ms=processing_time_ms,
                                          user_id=user_id,
                                          endpoint=endpoint,
                                          error_occurred=error_occurred)
            
            # Record metrics for performance monitoring
            record_api_request(processing_time_ms, endpoint, status_code)
            
            # Periodic health checks and alerting
            current_time = time.time()
            if current_time - self.last_health_check > self.health_check_interval:
                asyncio.create_task(self._perform_health_check())
                self.last_health_check = current_time
            
            # Add monitoring headers to response
            if response:
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Processing-Time"] = f"{processing_time_ms:.2f}ms"
                response.headers["X-Server-Time"] = datetime.now(timezone.utc).isoformat()
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def _perform_health_check(self):
        """Perform periodic health check and alerting"""
        try:
            # Get current system health
            health_status = get_system_health()
            
            # Check if alert system is active and perform alert checks
            if alert_system.is_active:
                current_metrics = performance_monitor.metrics_collector.collect_system_metrics()
                
                # Additional context for alerts
                additional_context = {
                    'total_requests': self.request_count,
                    'total_errors': self.error_count,
                    'error_rate': (self.error_count / self.request_count * 100) if self.request_count > 0 else 0
                }
                
                # Check for alerts
                alerts = await check_system_alerts(current_metrics, additional_context)
                
                if alerts:
                    self.logger.warning(f"Health check triggered {len(alerts)} alerts",
                                      alert_count=len(alerts),
                                      health_score=health_status.get("health_score", 0))
            
            # Log health status periodically
            self.logger.info("Periodic health check completed",
                           health_score=health_status.get("health_score", 0),
                           status=health_status.get("status", "unknown"),
                           total_requests=self.request_count,
                           total_errors=self.error_count)
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")


class DatabaseMonitoringMiddleware:
    """Middleware specifically for database operation monitoring"""
    
    def __init__(self):
        self.logger = get_medical_logger("db_monitoring_middleware")
    
    async def monitor_database_operation(self, operation: str, table: str, func: Callable, *args, **kwargs):
        """Monitor database operation performance"""
        start_time = time.time()
        success = False
        error = None
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            success = True
            return result
            
        except Exception as e:
            error = str(e)
            self.logger.error(f"Database operation failed: {operation} on {table} - {error}")
            raise
            
        finally:
            duration_ms = (time.time() - start_time) * 1000
            
            # Log database operation
            self.logger.log_database_operation(operation, table, duration_ms, success, error)


class MedicalConsultationMonitoringMiddleware:
    """Middleware specifically for medical consultation monitoring"""
    
    def __init__(self):
        self.logger = get_medical_logger("medical_consultation_middleware")
    
    async def monitor_consultation(self, user_id: str, message: str, ai_response: str, 
                                 processing_time_ms: float, ai_model: str, 
                                 emergency_detected: bool = False):
        """Monitor medical consultation with privacy protection"""
        
        # Log consultation with privacy protection
        self.logger.log_medical_consultation(
            user_id=user_id,
            message=message,
            ai_response=ai_response,
            processing_time_ms=processing_time_ms,
            ai_model=ai_model,
            emergency_detected=emergency_detected
        )
        
        # Additional monitoring for emergency situations
        if emergency_detected:
            self.logger.critical("Emergency situation detected in medical consultation",
                               user_id=user_id,
                               ai_model=ai_model,
                               processing_time_ms=processing_time_ms,
                               emergency_flag=True)
            
            # Could trigger immediate alerts here
            try:
                # Create emergency alert context
                emergency_context = {
                    'user_id': user_id,
                    'ai_model': ai_model,
                    'emergency_detected': True,
                    'consultation_length': len(message),
                    'response_time_ms': processing_time_ms
                }
                
                # This could trigger immediate emergency notifications
                # For now, just log it with high priority
                self.logger.critical("EMERGENCY CONSULTATION ALERT",
                                   **emergency_context)
                
            except Exception as e:
                self.logger.error(f"Failed to process emergency alert: {e}")


# Global middleware instances
monitoring_middleware = MonitoringMiddleware()
db_monitoring_middleware = DatabaseMonitoringMiddleware()
medical_consultation_middleware = MedicalConsultationMonitoringMiddleware()


# Decorator for monitoring database operations
def monitor_db_operation(operation: str, table: str):
    """Decorator for monitoring database operations"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            return await db_monitoring_middleware.monitor_database_operation(
                operation, table, func, *args, **kwargs
            )
        
        def sync_wrapper(*args, **kwargs):
            import asyncio
            return asyncio.run(db_monitoring_middleware.monitor_database_operation(
                operation, table, func, *args, **kwargs
            ))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Decorator for monitoring medical consultations
def monitor_medical_consultation(func):
    """Decorator for monitoring medical consultations"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Extract consultation details from result if available
            if isinstance(result, dict) and 'consultation_details' in result:
                details = result['consultation_details']
                processing_time_ms = (time.time() - start_time) * 1000
                
                await medical_consultation_middleware.monitor_consultation(
                    user_id=details.get('user_id', 'unknown'),
                    message=details.get('message', ''),
                    ai_response=details.get('ai_response', ''),
                    processing_time_ms=processing_time_ms,
                    ai_model=details.get('ai_model', 'unknown'),
                    emergency_detected=details.get('emergency_detected', False)
                )
            
            return result
            
        except Exception as e:
            # Log consultation error
            processing_time_ms = (time.time() - start_time) * 1000
            medical_consultation_middleware.logger.error(
                f"Medical consultation failed after {processing_time_ms:.2f}ms: {e}"
            )
            raise
    
    return wrapper


# Startup function to initialize monitoring
async def initialize_monitoring_system():
    """Initialize the comprehensive monitoring system"""
    logger = get_medical_logger("monitoring_system")
    
    try:
        # Configure logging system
        from logging_system import logging_system
        logging_system.configure_logging(
            log_level="INFO",
            log_directory="logs",
            enable_console=True,
            enable_file=True
        )
        
        # Start performance monitoring
        performance_monitor.start_monitoring(interval_seconds=30)
        
        # Start alert system
        alert_system.start()
        
        logger.info("Comprehensive monitoring system initialized successfully",
                   logging_configured=logging_system.is_configured,
                   performance_monitoring_active=performance_monitor.monitoring_active,
                   alert_system_active=alert_system.is_active)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize monitoring system: {e}")
        return False


# Shutdown function
async def shutdown_monitoring_system():
    """Shutdown the monitoring system gracefully"""
    logger = get_medical_logger("monitoring_system")
    
    try:
        # Stop alert system
        alert_system.stop()
        
        # Stop performance monitoring
        performance_monitor.stop_monitoring()
        
        logger.info("Monitoring system shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during monitoring system shutdown: {e}")