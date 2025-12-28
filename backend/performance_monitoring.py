"""
Application Performance Monitoring System for My Dr AI Medical Assistant
Comprehensive performance tracking, error monitoring, and alerting system
"""
import os
import time
import json
import asyncio
import threading
import psutil
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from queue import Queue, Empty
import statistics
from pathlib import Path
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

from logging_system import get_medical_logger, LogContext, PerformanceMetrics


@dataclass
class ErrorMetrics:
    """Error tracking metrics"""
    timestamp: str
    error_type: str
    error_message: str
    module: str
    function: str
    line_number: int
    user_id: Optional[str] = None
    endpoint: Optional[str] = None
    stack_trace: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class SystemMetrics:
    """System resource metrics"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    active_connections: int
    response_time_avg_ms: float
    error_rate_percent: float
    requests_per_minute: int


@dataclass
class AlertThreshold:
    """Alert threshold configuration"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    comparison: str = "greater_than"  # greater_than, less_than, equals
    enabled: bool = True
    cooldown_minutes: int = 15


@dataclass
class Alert:
    """Alert information"""
    timestamp: str
    alert_type: str
    severity: str  # warning, critical
    metric_name: str
    current_value: float
    threshold_value: float
    message: str
    context: Optional[Dict[str, Any]] = None


class MetricsCollector:
    """Collects various application and system metrics"""
    
    def __init__(self):
        self.logger = get_medical_logger("metrics_collector")
        self.metrics_history = deque(maxlen=1000)
        self.error_history = deque(maxlen=500)
        self.request_times = deque(maxlen=100)
        self.error_counts = defaultdict(int)
        self.request_counts = defaultdict(int)
        self.last_cleanup = time.time()
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network connections (approximate active connections)
            connections = len(psutil.net_connections(kind='inet'))
            
            # Calculate request metrics
            current_time = time.time()
            minute_ago = current_time - 60
            
            # Recent request times for average calculation
            recent_times = [t for t in self.request_times if t > minute_ago]
            avg_response_time = statistics.mean(recent_times) if recent_times else 0
            
            # Error rate calculation
            total_requests = sum(self.request_counts.values())
            total_errors = sum(self.error_counts.values())
            error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
            
            # Requests per minute
            requests_per_minute = len([t for t in self.request_times if t > minute_ago])
            
            metrics = SystemMetrics(
                timestamp=datetime.now(timezone.utc).isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk.used / disk.total * 100,
                disk_free_gb=disk.free / (1024 * 1024 * 1024),
                active_connections=connections,
                response_time_avg_ms=avg_response_time,
                error_rate_percent=error_rate,
                requests_per_minute=requests_per_minute
            )
            
            self.metrics_history.append(metrics)
            
            # Cleanup old data periodically
            if current_time - self.last_cleanup > 300:  # Every 5 minutes
                self._cleanup_old_data()
                self.last_cleanup = current_time
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(timezone.utc).isoformat(),
                cpu_percent=0, memory_percent=0, memory_used_mb=0,
                memory_available_mb=0, disk_usage_percent=0, disk_free_gb=0,
                active_connections=0, response_time_avg_ms=0,
                error_rate_percent=0, requests_per_minute=0
            )
    
    def record_request(self, response_time_ms: float, endpoint: str, status_code: int):
        """Record API request metrics"""
        current_time = time.time()
        self.request_times.append(current_time)
        self.request_counts[endpoint] += 1
        
        if status_code >= 400:
            self.error_counts[endpoint] += 1
    
    def record_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Record error occurrence"""
        import traceback
        
        error_metrics = ErrorMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            error_type=type(error).__name__,
            error_message=str(error),
            module=context.get('module', 'unknown') if context else 'unknown',
            function=context.get('function', 'unknown') if context else 'unknown',
            line_number=context.get('line_number', 0) if context else 0,
            user_id=context.get('user_id') if context else None,
            endpoint=context.get('endpoint') if context else None,
            stack_trace=traceback.format_exc(),
            context=context
        )
        
        self.error_history.append(error_metrics)
        self.logger.error(f"Error recorded: {error_metrics.error_type} - {error_metrics.error_message}")
    
    def get_metrics_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """Get metrics summary for the specified time period"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        # Filter recent metrics
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp.replace('Z', '+00:00')) > cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No metrics available for the specified period"}
        
        # Calculate statistics
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        response_times = [m.response_time_avg_ms for m in recent_metrics]
        error_rates = [m.error_rate_percent for m in recent_metrics]
        
        return {
            "period_minutes": minutes,
            "total_samples": len(recent_metrics),
            "cpu_stats": {
                "avg": statistics.mean(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values)
            },
            "memory_stats": {
                "avg": statistics.mean(memory_values),
                "max": max(memory_values),
                "min": min(memory_values)
            },
            "response_time_stats": {
                "avg": statistics.mean(response_times),
                "max": max(response_times),
                "min": min(response_times)
            },
            "error_rate_stats": {
                "avg": statistics.mean(error_rates),
                "max": max(error_rates),
                "current": error_rates[-1] if error_rates else 0
            },
            "latest_metrics": asdict(recent_metrics[-1]) if recent_metrics else None
        }
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the specified time period"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Filter recent errors
        recent_errors = [
            e for e in self.error_history
            if datetime.fromisoformat(e.timestamp.replace('Z', '+00:00')) > cutoff_time
        ]
        
        # Group by error type
        error_types = defaultdict(int)
        error_modules = defaultdict(int)
        error_endpoints = defaultdict(int)
        
        for error in recent_errors:
            error_types[error.error_type] += 1
            error_modules[error.module] += 1
            if error.endpoint:
                error_endpoints[error.endpoint] += 1
        
        return {
            "period_hours": hours,
            "total_errors": len(recent_errors),
            "error_types": dict(error_types),
            "error_modules": dict(error_modules),
            "error_endpoints": dict(error_endpoints),
            "recent_errors": [asdict(e) for e in recent_errors[-10:]]  # Last 10 errors
        }
    
    def _cleanup_old_data(self):
        """Clean up old data to prevent memory leaks"""
        current_time = time.time()
        hour_ago = current_time - 3600
        
        # Clean up request times older than 1 hour
        self.request_times = deque(
            [t for t in self.request_times if t > hour_ago],
            maxlen=100
        )
        
        # Reset counters periodically (every hour)
        if current_time % 3600 < 300:  # Within 5 minutes of the hour
            self.request_counts.clear()
            self.error_counts.clear()


class AlertManager:
    """Manages performance alerts and notifications"""
    
    def __init__(self):
        self.logger = get_medical_logger("alert_manager")
        self.alert_thresholds = self._load_default_thresholds()
        self.alert_history = deque(maxlen=200)
        self.last_alerts = {}  # Track last alert time for cooldown
        self.notification_queue = Queue()
        self.notification_thread = None
        self.stop_event = threading.Event()
        
        # Email configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.alert_email_from = os.getenv("ALERT_EMAIL_FROM", "alerts@mydoc.ai")
        self.alert_email_to = os.getenv("ALERT_EMAIL_TO", "admin@mydoc.ai").split(",")
    
    def _load_default_thresholds(self) -> List[AlertThreshold]:
        """Load default alert thresholds"""
        return [
            AlertThreshold("cpu_percent", 75, 90),
            AlertThreshold("memory_percent", 80, 95),
            AlertThreshold("disk_usage_percent", 85, 95),
            AlertThreshold("response_time_avg_ms", 1000, 2000),
            AlertThreshold("error_rate_percent", 5, 10),
            AlertThreshold("disk_free_gb", 5, 1, "less_than"),
        ]
    
    def check_alerts(self, metrics: SystemMetrics) -> List[Alert]:
        """Check metrics against alert thresholds"""
        triggered_alerts = []
        current_time = datetime.now(timezone.utc)
        
        for threshold in self.alert_thresholds:
            if not threshold.enabled:
                continue
            
            # Check cooldown
            last_alert_time = self.last_alerts.get(threshold.metric_name)
            if last_alert_time:
                time_since_last = (current_time - last_alert_time).total_seconds() / 60
                if time_since_last < threshold.cooldown_minutes:
                    continue
            
            # Get metric value
            metric_value = getattr(metrics, threshold.metric_name, None)
            if metric_value is None:
                continue
            
            # Check thresholds
            alert_triggered = False
            severity = None
            
            if threshold.comparison == "greater_than":
                if metric_value >= threshold.critical_threshold:
                    alert_triggered = True
                    severity = "critical"
                elif metric_value >= threshold.warning_threshold:
                    alert_triggered = True
                    severity = "warning"
            elif threshold.comparison == "less_than":
                if metric_value <= threshold.critical_threshold:
                    alert_triggered = True
                    severity = "critical"
                elif metric_value <= threshold.warning_threshold:
                    alert_triggered = True
                    severity = "warning"
            
            if alert_triggered:
                alert = Alert(
                    timestamp=current_time.isoformat(),
                    alert_type="performance",
                    severity=severity,
                    metric_name=threshold.metric_name,
                    current_value=metric_value,
                    threshold_value=threshold.critical_threshold if severity == "critical" else threshold.warning_threshold,
                    message=f"{threshold.metric_name} is {metric_value:.2f} (threshold: {threshold.critical_threshold if severity == 'critical' else threshold.warning_threshold})",
                    context=asdict(metrics)
                )
                
                triggered_alerts.append(alert)
                self.last_alerts[threshold.metric_name] = current_time
                
                # Queue notification
                self.notification_queue.put(alert)
                
                self.logger.warning(f"Alert triggered: {alert.message}", 
                                  alert_type=alert.alert_type,
                                  severity=alert.severity,
                                  metric_name=alert.metric_name,
                                  current_value=alert.current_value)
        
        # Store in history
        if triggered_alerts:
            self.alert_history.extend(triggered_alerts)
        
        return triggered_alerts
    
    def start_notification_processor(self):
        """Start the notification processor thread"""
        if self.notification_thread and self.notification_thread.is_alive():
            return
        
        self.stop_event.clear()
        self.notification_thread = threading.Thread(target=self._process_notifications)
        self.notification_thread.daemon = True
        self.notification_thread.start()
        self.logger.info("Alert notification processor started")
    
    def stop_notification_processor(self):
        """Stop the notification processor thread"""
        self.stop_event.set()
        if self.notification_thread:
            self.notification_thread.join(timeout=5)
        self.logger.info("Alert notification processor stopped")
    
    def _process_notifications(self):
        """Process notification queue"""
        while not self.stop_event.is_set():
            try:
                alert = self.notification_queue.get(timeout=1)
                self._send_notifications(alert)
            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing notification: {e}")
    
    def _send_notifications(self, alert: Alert):
        """Send alert notifications"""
        try:
            # Log notification
            self._log_alert(alert)
            
            # Send email if configured
            if self.smtp_username and self.alert_email_to:
                self._send_email_alert(alert)
            
        except Exception as e:
            self.logger.error(f"Failed to send notifications: {e}")
    
    def _log_alert(self, alert: Alert):
        """Log alert to file"""
        self.logger.warning(f"ALERT: {alert.message}",
                          alert_type=alert.alert_type,
                          severity=alert.severity,
                          metric_name=alert.metric_name,
                          current_value=alert.current_value,
                          threshold_value=alert.threshold_value)
    
    def _send_email_alert(self, alert: Alert):
        """Send email alert"""
        try:
            msg = MimeMultipart()
            msg['From'] = self.alert_email_from
            msg['To'] = ", ".join(self.alert_email_to)
            msg['Subject'] = f"[{alert.severity.upper()}] MyDoc Performance Alert - {alert.metric_name}"
            
            body = f"""
Performance Alert Triggered

Severity: {alert.severity.upper()}
Metric: {alert.metric_name}
Current Value: {alert.current_value:.2f}
Threshold: {alert.threshold_value:.2f}
Time: {alert.timestamp}

Message: {alert.message}

Please check the system immediately.

---
MyDoc AI Medical Assistant Monitoring System
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email alert sent for {alert.metric_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert summary for the specified time period"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Filter recent alerts
        recent_alerts = [
            a for a in self.alert_history
            if datetime.fromisoformat(a.timestamp.replace('Z', '+00:00')) > cutoff_time
        ]
        
        # Group by severity and type
        severity_counts = defaultdict(int)
        metric_counts = defaultdict(int)
        
        for alert in recent_alerts:
            severity_counts[alert.severity] += 1
            metric_counts[alert.metric_name] += 1
        
        return {
            "period_hours": hours,
            "total_alerts": len(recent_alerts),
            "severity_breakdown": dict(severity_counts),
            "metric_breakdown": dict(metric_counts),
            "recent_alerts": [asdict(a) for a in recent_alerts[-10:]]  # Last 10 alerts
        }


class PerformanceMonitor:
    """Main performance monitoring system"""
    
    def __init__(self):
        self.logger = get_medical_logger("performance_monitor")
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.monitoring_active = False
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        self.monitoring_interval = 30  # seconds
    
    def start_monitoring(self, interval_seconds: int = 30):
        """Start performance monitoring"""
        if self.monitoring_active:
            self.logger.warning("Performance monitoring is already active")
            return
        
        self.monitoring_interval = interval_seconds
        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        # Start alert notification processor
        self.alert_manager.start_notification_processor()
        
        self.monitoring_active = True
        self.logger.info(f"Performance monitoring started with {interval_seconds}s interval")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        if not self.monitoring_active:
            return
        
        self.stop_event.set()
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        
        self.alert_manager.stop_notification_processor()
        
        self.monitoring_active = False
        self.logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self.stop_event.is_set():
            try:
                # Collect metrics
                metrics = self.metrics_collector.collect_system_metrics()
                
                # Check for alerts
                alerts = self.alert_manager.check_alerts(metrics)
                
                # Log metrics periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self.logger.info("System metrics collected",
                                   cpu_percent=metrics.cpu_percent,
                                   memory_percent=metrics.memory_percent,
                                   response_time_avg_ms=metrics.response_time_avg_ms,
                                   error_rate_percent=metrics.error_rate_percent)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
            
            # Wait for next interval
            self.stop_event.wait(self.monitoring_interval)
    
    def record_request(self, response_time_ms: float, endpoint: str, status_code: int):
        """Record API request metrics"""
        self.metrics_collector.record_request(response_time_ms, endpoint, status_code)
    
    def record_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Record error occurrence"""
        self.metrics_collector.record_error(error, context)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            current_metrics = self.metrics_collector.collect_system_metrics()
            metrics_summary = self.metrics_collector.get_metrics_summary(60)
            error_summary = self.metrics_collector.get_error_summary(24)
            alert_summary = self.alert_manager.get_alert_summary(24)
            
            # Calculate health score (0-100)
            health_score = 100
            
            # Deduct points for high resource usage
            if current_metrics.cpu_percent > 80:
                health_score -= 20
            elif current_metrics.cpu_percent > 60:
                health_score -= 10
            
            if current_metrics.memory_percent > 90:
                health_score -= 20
            elif current_metrics.memory_percent > 75:
                health_score -= 10
            
            # Deduct points for high error rate
            if current_metrics.error_rate_percent > 5:
                health_score -= 15
            elif current_metrics.error_rate_percent > 2:
                health_score -= 5
            
            # Deduct points for slow response times
            if current_metrics.response_time_avg_ms > 1000:
                health_score -= 15
            elif current_metrics.response_time_avg_ms > 500:
                health_score -= 10
            
            # Deduct points for recent alerts
            recent_critical_alerts = sum(1 for a in self.alert_manager.alert_history 
                                       if a.severity == "critical" and 
                                       (datetime.now(timezone.utc) - datetime.fromisoformat(a.timestamp.replace('Z', '+00:00'))).total_seconds() < 3600)
            health_score -= recent_critical_alerts * 10
            
            health_score = max(0, min(100, health_score))
            
            # Determine status
            if health_score >= 90:
                status = "excellent"
            elif health_score >= 75:
                status = "good"
            elif health_score >= 50:
                status = "fair"
            elif health_score >= 25:
                status = "poor"
            else:
                status = "critical"
            
            return {
                "status": status,
                "health_score": health_score,
                "monitoring_active": self.monitoring_active,
                "current_metrics": asdict(current_metrics),
                "metrics_summary": metrics_summary,
                "error_summary": error_summary,
                "alert_summary": alert_summary,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get health status: {e}")
            return {
                "status": "unknown",
                "health_score": 0,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Convenience functions
def start_performance_monitoring(interval_seconds: int = 30):
    """Start performance monitoring"""
    performance_monitor.start_monitoring(interval_seconds)

def stop_performance_monitoring():
    """Stop performance monitoring"""
    performance_monitor.stop_monitoring()

def record_api_request(response_time_ms: float, endpoint: str, status_code: int):
    """Record API request metrics"""
    performance_monitor.record_request(response_time_ms, endpoint, status_code)

def record_application_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Record application error"""
    performance_monitor.record_error(error, context)

def get_system_health() -> Dict[str, Any]:
    """Get system health status"""
    return performance_monitor.get_health_status()