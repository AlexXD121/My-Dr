"""
Database Monitoring and Alerting System for My Dr AI Medical Assistant
Comprehensive monitoring with performance metrics, alerting, and health dashboards
"""
import os
import logging
import asyncio
import time
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from threading import Thread, Event
from queue import Queue, Empty
import psutil
from sqlalchemy import text

try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

try:
    from production_database import production_db_manager, db_config
    PRODUCTION_DB_AVAILABLE = True
except ImportError:
    PRODUCTION_DB_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class AlertThreshold:
    """Alert threshold configuration"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    comparison: str = "greater_than"  # greater_than, less_than, equals
    enabled: bool = True


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    description: str
    thresholds: List[AlertThreshold]
    cooldown_minutes: int = 15
    notification_channels: List[str] = None
    
    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ["email", "log"]


class DatabaseMetricsCollector:
    """Collects comprehensive database metrics"""
    
    def __init__(self):
        if PRODUCTION_DB_AVAILABLE:
            self.db_manager = production_db_manager
        else:
            self.db_manager = None
        self.metrics_history = []
        self.max_history_size = 1000
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all database metrics"""
        if not self.db_manager:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": "Database manager not available",
                "health_score": 0
            }
            
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "connection_metrics": self._collect_connection_metrics(),
            "performance_metrics": self._collect_performance_metrics(),
            "storage_metrics": self._collect_storage_metrics(),
            "query_metrics": self._collect_query_metrics(),
            "system_metrics": self._collect_system_metrics(),
            "health_score": 0
        }
        
        # Calculate overall health score
        metrics["health_score"] = self._calculate_health_score(metrics)
        
        # Store in history
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)
        
        return metrics
    
    def _collect_connection_metrics(self) -> Dict[str, Any]:
        """Collect database connection metrics"""
        if not self.db_manager:
            return {"error": "Database manager not available"}
            
        try:
            with self.db_manager.get_session() as session:
                # Active connections
                result = session.execute(text("""
                    SELECT 
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections,
                        count(*) FILTER (WHERE state = 'idle') as idle_connections,
                        count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction,
                        count(*) FILTER (WHERE state = 'idle in transaction (aborted)') as idle_in_transaction_aborted,
                        count(*) FILTER (WHERE backend_type = 'client backend') as client_backends,
                        max(EXTRACT(EPOCH FROM (now() - query_start))) as longest_query_seconds,
                        max(EXTRACT(EPOCH FROM (now() - state_change))) as longest_idle_seconds
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """))
                
                conn_data = result.fetchone()
                
                # Connection pool metrics
                pool = self.db_manager.sync_engine.pool
                
                return {
                    "total_connections": conn_data[0],
                    "active_connections": conn_data[1],
                    "idle_connections": conn_data[2],
                    "idle_in_transaction": conn_data[3],
                    "idle_in_transaction_aborted": conn_data[4],
                    "client_backends": conn_data[5],
                    "longest_query_seconds": float(conn_data[6]) if conn_data[6] else 0,
                    "longest_idle_seconds": float(conn_data[7]) if conn_data[7] else 0,
                    "pool_size": pool.size(),
                    "pool_checked_out": pool.checkedout(),
                    "pool_overflow": pool.overflow(),
                    "pool_checked_in": pool.checkedin(),
                    "pool_utilization": (pool.checkedout() / pool.size()) * 100 if pool.size() > 0 else 0
                }
                
        except Exception as e:
            logger.error(f"Failed to collect connection metrics: {e}")
            return {"error": str(e)}
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect database performance metrics"""
        try:
            with self.db_manager.get_session() as session:
                # Query performance
                start_time = time.time()
                session.execute(text("SELECT 1"))
                simple_query_time = (time.time() - start_time) * 1000
                
                # Database statistics
                result = session.execute(text("""
                    SELECT 
                        sum(numbackends) as backends,
                        sum(xact_commit) as commits,
                        sum(xact_rollback) as rollbacks,
                        sum(blks_read) as blocks_read,
                        sum(blks_hit) as blocks_hit,
                        sum(tup_returned) as tuples_returned,
                        sum(tup_fetched) as tuples_fetched,
                        sum(tup_inserted) as tuples_inserted,
                        sum(tup_updated) as tuples_updated,
                        sum(tup_deleted) as tuples_deleted
                    FROM pg_stat_database 
                    WHERE datname = current_database()
                """))
                
                db_stats = result.fetchone()
                
                # Cache hit ratio
                cache_hit_ratio = 0
                if db_stats[3] and db_stats[4]:  # blocks_read and blocks_hit
                    total_reads = db_stats[3] + db_stats[4]
                    cache_hit_ratio = (db_stats[4] / total_reads) * 100 if total_reads > 0 else 0
                
                # Transaction ratio
                transaction_ratio = 0
                if db_stats[1] and db_stats[2]:  # commits and rollbacks
                    total_transactions = db_stats[1] + db_stats[2]
                    transaction_ratio = (db_stats[1] / total_transactions) * 100 if total_transactions > 0 else 0
                
                return {
                    "simple_query_ms": round(simple_query_time, 2),
                    "cache_hit_ratio": round(cache_hit_ratio, 2),
                    "transaction_success_ratio": round(transaction_ratio, 2),
                    "backends": db_stats[0] or 0,
                    "commits": db_stats[1] or 0,
                    "rollbacks": db_stats[2] or 0,
                    "blocks_read": db_stats[3] or 0,
                    "blocks_hit": db_stats[4] or 0,
                    "tuples_returned": db_stats[5] or 0,
                    "tuples_fetched": db_stats[6] or 0,
                    "tuples_inserted": db_stats[7] or 0,
                    "tuples_updated": db_stats[8] or 0,
                    "tuples_deleted": db_stats[9] or 0
                }
                
        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {e}")
            return {"error": str(e)}
    
    def _collect_storage_metrics(self) -> Dict[str, Any]:
        """Collect database storage metrics"""
        try:
            with self.db_manager.get_session() as session:
                # Database size
                result = session.execute(text("""
                    SELECT 
                        pg_database_size(current_database()) as db_size_bytes,
                        pg_size_pretty(pg_database_size(current_database())) as db_size_pretty
                """))
                
                size_data = result.fetchone()
                
                # Table sizes
                table_sizes_result = session.execute(text("""
                    SELECT 
                        schemaname,
                        tablename,
                        pg_total_relation_size(schemaname||'.'||tablename) as total_size_bytes,
                        pg_relation_size(schemaname||'.'||tablename) as table_size_bytes
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                    LIMIT 10
                """))
                
                table_sizes = []
                total_table_size = 0
                for row in table_sizes_result:
                    table_info = {
                        "schema": row[0],
                        "table": row[1],
                        "total_size_bytes": row[2],
                        "table_size_bytes": row[3]
                    }
                    table_sizes.append(table_info)
                    total_table_size += row[2]
                
                # Tablespace usage (if available)
                tablespace_result = session.execute(text("""
                    SELECT spcname, pg_tablespace_size(spcname) as size_bytes
                    FROM pg_tablespace
                """))
                
                tablespaces = []
                for row in tablespace_result:
                    tablespaces.append({
                        "name": row[0],
                        "size_bytes": row[1]
                    })
                
                return {
                    "database_size_bytes": size_data[0],
                    "database_size_pretty": size_data[1],
                    "total_table_size_bytes": total_table_size,
                    "largest_tables": table_sizes,
                    "tablespaces": tablespaces
                }
                
        except Exception as e:
            logger.error(f"Failed to collect storage metrics: {e}")
            return {"error": str(e)}
    
    def _collect_query_metrics(self) -> Dict[str, Any]:
        """Collect query performance metrics"""
        try:
            with self.db_manager.get_session() as session:
                # Long running queries
                long_queries_result = session.execute(text("""
                    SELECT 
                        pid,
                        usename,
                        application_name,
                        state,
                        EXTRACT(EPOCH FROM (now() - query_start)) as duration_seconds,
                        left(query, 100) as query_preview
                    FROM pg_stat_activity 
                    WHERE state = 'active' 
                    AND query_start < now() - interval '30 seconds'
                    AND datname = current_database()
                    ORDER BY query_start
                """))
                
                long_queries = []
                for row in long_queries_result:
                    long_queries.append({
                        "pid": row[0],
                        "username": row[1],
                        "application": row[2],
                        "state": row[3],
                        "duration_seconds": float(row[4]),
                        "query_preview": row[5]
                    })
                
                # Blocked queries
                blocked_queries_result = session.execute(text("""
                    SELECT 
                        blocked_locks.pid AS blocked_pid,
                        blocked_activity.usename AS blocked_user,
                        blocking_locks.pid AS blocking_pid,
                        blocking_activity.usename AS blocking_user,
                        blocked_activity.query AS blocked_statement,
                        blocking_activity.query AS blocking_statement
                    FROM pg_catalog.pg_locks blocked_locks
                    JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
                    JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
                        AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
                        AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
                        AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
                        AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
                        AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
                        AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
                        AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
                        AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
                        AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
                        AND blocking_locks.pid != blocked_locks.pid
                    JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
                    WHERE NOT blocked_locks.granted
                """))
                
                blocked_queries = []
                for row in blocked_queries_result:
                    blocked_queries.append({
                        "blocked_pid": row[0],
                        "blocked_user": row[1],
                        "blocking_pid": row[2],
                        "blocking_user": row[3],
                        "blocked_query": row[4][:100] if row[4] else "",
                        "blocking_query": row[5][:100] if row[5] else ""
                    })
                
                return {
                    "long_running_queries": long_queries,
                    "long_running_count": len(long_queries),
                    "blocked_queries": blocked_queries,
                    "blocked_count": len(blocked_queries)
                }
                
        except Exception as e:
            logger.error(f"Failed to collect query metrics: {e}")
            return {"error": str(e)}
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage for database directory
            disk_usage = psutil.disk_usage('/')
            
            # Load average (Unix-like systems)
            load_avg = None
            try:
                load_avg = os.getloadavg()
            except (OSError, AttributeError):
                pass  # Not available on Windows
            
            return {
                "cpu_percent": cpu_percent,
                "memory_total_bytes": memory.total,
                "memory_available_bytes": memory.available,
                "memory_used_bytes": memory.used,
                "memory_percent": memory.percent,
                "disk_total_bytes": disk_usage.total,
                "disk_used_bytes": disk_usage.used,
                "disk_free_bytes": disk_usage.free,
                "disk_percent": (disk_usage.used / disk_usage.total) * 100,
                "load_average": list(load_avg) if load_avg else None
            }
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_health_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall database health score (0-100)"""
        score = 100.0
        
        try:
            # Connection health (25% weight)
            conn_metrics = metrics.get("connection_metrics", {})
            if "pool_utilization" in conn_metrics:
                pool_util = conn_metrics["pool_utilization"]
                if pool_util > 90:
                    score -= 15
                elif pool_util > 75:
                    score -= 10
                elif pool_util > 50:
                    score -= 5
            
            # Performance health (30% weight)
            perf_metrics = metrics.get("performance_metrics", {})
            if "simple_query_ms" in perf_metrics:
                query_time = perf_metrics["simple_query_ms"]
                if query_time > 1000:
                    score -= 20
                elif query_time > 500:
                    score -= 15
                elif query_time > 100:
                    score -= 10
            
            if "cache_hit_ratio" in perf_metrics:
                cache_ratio = perf_metrics["cache_hit_ratio"]
                if cache_ratio < 80:
                    score -= 15
                elif cache_ratio < 90:
                    score -= 10
                elif cache_ratio < 95:
                    score -= 5
            
            # Query health (25% weight)
            query_metrics = metrics.get("query_metrics", {})
            if "long_running_count" in query_metrics:
                long_queries = query_metrics["long_running_count"]
                if long_queries > 10:
                    score -= 15
                elif long_queries > 5:
                    score -= 10
                elif long_queries > 0:
                    score -= 5
            
            if "blocked_count" in query_metrics:
                blocked = query_metrics["blocked_count"]
                if blocked > 5:
                    score -= 10
                elif blocked > 0:
                    score -= 5
            
            # System health (20% weight)
            system_metrics = metrics.get("system_metrics", {})
            if "cpu_percent" in system_metrics:
                cpu = system_metrics["cpu_percent"]
                if cpu > 90:
                    score -= 10
                elif cpu > 75:
                    score -= 5
            
            if "memory_percent" in system_metrics:
                memory = system_metrics["memory_percent"]
                if memory > 90:
                    score -= 10
                elif memory > 80:
                    score -= 5
            
        except Exception as e:
            logger.error(f"Failed to calculate health score: {e}")
            score = 50  # Default to moderate health if calculation fails
        
        return max(0, min(100, score))
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the specified time period"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m["timestamp"].replace('Z', '+00:00')) > cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No metrics available for the specified period"}
        
        # Calculate averages and trends
        health_scores = [m["health_score"] for m in recent_metrics]
        query_times = [
            m.get("performance_metrics", {}).get("simple_query_ms", 0) 
            for m in recent_metrics
        ]
        
        return {
            "period_hours": hours,
            "total_samples": len(recent_metrics),
            "average_health_score": sum(health_scores) / len(health_scores),
            "min_health_score": min(health_scores),
            "max_health_score": max(health_scores),
            "average_query_time_ms": sum(query_times) / len(query_times) if query_times else 0,
            "max_query_time_ms": max(query_times) if query_times else 0,
            "first_sample": recent_metrics[0]["timestamp"],
            "last_sample": recent_metrics[-1]["timestamp"]
        }


class DatabaseAlertManager:
    """Manages database alerts and notifications"""
    
    def __init__(self):
        self.alert_rules = self._load_default_alert_rules()
        self.alert_history = []
        self.last_alerts = {}  # Track last alert time for cooldown
        self.notification_queue = Queue()
        self.notification_thread = None
        self.stop_event = Event()
        
        # Email configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.alert_email_from = os.getenv("ALERT_EMAIL_FROM", "alerts@mydoc.ai")
        self.alert_email_to = os.getenv("ALERT_EMAIL_TO", "admin@mydoc.ai").split(",")
    
    def _load_default_alert_rules(self) -> List[AlertRule]:
        """Load default alert rules"""
        return [
            AlertRule(
                name="High Connection Pool Utilization",
                description="Connection pool utilization is high",
                thresholds=[
                    AlertThreshold("connection_metrics.pool_utilization", 75, 90)
                ],
                cooldown_minutes=15
            ),
            AlertRule(
                name="Slow Query Performance",
                description="Database queries are running slowly",
                thresholds=[
                    AlertThreshold("performance_metrics.simple_query_ms", 500, 1000)
                ],
                cooldown_minutes=10
            ),
            AlertRule(
                name="Low Cache Hit Ratio",
                description="Database cache hit ratio is low",
                thresholds=[
                    AlertThreshold("performance_metrics.cache_hit_ratio", 90, 80, "less_than")
                ],
                cooldown_minutes=30
            ),
            AlertRule(
                name="Long Running Queries",
                description="Too many long-running queries detected",
                thresholds=[
                    AlertThreshold("query_metrics.long_running_count", 5, 10)
                ],
                cooldown_minutes=5
            ),
            AlertRule(
                name="Blocked Queries",
                description="Queries are being blocked",
                thresholds=[
                    AlertThreshold("query_metrics.blocked_count", 1, 5)
                ],
                cooldown_minutes=5
            ),
            AlertRule(
                name="High CPU Usage",
                description="System CPU usage is high",
                thresholds=[
                    AlertThreshold("system_metrics.cpu_percent", 75, 90)
                ],
                cooldown_minutes=10
            ),
            AlertRule(
                name="High Memory Usage",
                description="System memory usage is high",
                thresholds=[
                    AlertThreshold("system_metrics.memory_percent", 80, 90)
                ],
                cooldown_minutes=15
            ),
            AlertRule(
                name="Low Health Score",
                description="Overall database health score is low",
                thresholds=[
                    AlertThreshold("health_score", 70, 50, "less_than")
                ],
                cooldown_minutes=20
            )
        ]
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check metrics against alert rules"""
        triggered_alerts = []
        current_time = datetime.now(timezone.utc)
        
        for rule in self.alert_rules:
            if not any(t.enabled for t in rule.thresholds):
                continue
            
            # Check cooldown
            last_alert_time = self.last_alerts.get(rule.name)
            if last_alert_time:
                time_since_last = (current_time - last_alert_time).total_seconds() / 60
                if time_since_last < rule.cooldown_minutes:
                    continue
            
            # Check thresholds
            for threshold in rule.thresholds:
                if not threshold.enabled:
                    continue
                
                metric_value = self._get_nested_metric_value(metrics, threshold.metric_name)
                if metric_value is None:
                    continue
                
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
                    alert = {
                        "timestamp": current_time.isoformat(),
                        "rule_name": rule.name,
                        "description": rule.description,
                        "severity": severity,
                        "metric_name": threshold.metric_name,
                        "metric_value": metric_value,
                        "threshold_value": threshold.critical_threshold if severity == "critical" else threshold.warning_threshold,
                        "notification_channels": rule.notification_channels
                    }
                    
                    triggered_alerts.append(alert)
                    self.last_alerts[rule.name] = current_time
                    
                    # Queue notification
                    self.notification_queue.put(alert)
        
        # Store in history
        if triggered_alerts:
            self.alert_history.extend(triggered_alerts)
            # Keep only last 1000 alerts
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]
        
        return triggered_alerts
    
    def _get_nested_metric_value(self, metrics: Dict[str, Any], metric_path: str) -> Optional[float]:
        """Get nested metric value using dot notation"""
        try:
            keys = metric_path.split('.')
            value = metrics
            for key in keys:
                value = value[key]
            return float(value) if value is not None else None
        except (KeyError, TypeError, ValueError):
            return None
    
    def start_notification_processor(self):
        """Start the notification processor thread"""
        if self.notification_thread and self.notification_thread.is_alive():
            return
        
        self.stop_event.clear()
        self.notification_thread = Thread(target=self._process_notifications)
        self.notification_thread.daemon = True
        self.notification_thread.start()
        logger.info("Alert notification processor started")
    
    def stop_notification_processor(self):
        """Stop the notification processor thread"""
        self.stop_event.set()
        if self.notification_thread:
            self.notification_thread.join(timeout=5)
        logger.info("Alert notification processor stopped")
    
    def _process_notifications(self):
        """Process notification queue"""
        while not self.stop_event.is_set():
            try:
                alert = self.notification_queue.get(timeout=1)
                self._send_notifications(alert)
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing notification: {e}")
    
    def _send_notifications(self, alert: Dict[str, Any]):
        """Send alert notifications"""
        for channel in alert.get("notification_channels", []):
            try:
                if channel == "email":
                    self._send_email_alert(alert)
                elif channel == "log":
                    self._log_alert(alert)
                # Add more notification channels as needed
            except Exception as e:
                logger.error(f"Failed to send {channel} notification: {e}")
    
    def _send_email_alert(self, alert: Dict[str, Any]):
        """Send email alert"""
        if not EMAIL_AVAILABLE:
            logger.warning("Email functionality not available")
            return
            
        if not self.smtp_username or not self.alert_email_to:
            logger.warning("Email configuration incomplete, skipping email alert")
            return
        
        try:
            msg = MimeMultipart()
            msg['From'] = self.alert_email_from
            msg['To'] = ", ".join(self.alert_email_to)
            msg['Subject'] = f"[{alert.get('severity', 'ALERT').upper()}] MyDoc Database Alert: {alert.get('rule_name', 'Unknown')}"
            
            body = f"""
Database Alert Triggered

Rule: {alert['rule_name']}
Severity: {alert['severity'].upper()}
Description: {alert['description']}
Timestamp: {alert['timestamp']}

Metric: {alert['metric_name']}
Current Value: {alert['metric_value']}
Threshold: {alert['threshold_value']}

Please investigate the database system immediately.

--
MyDoc Database Monitoring System
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.smtp_username:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent for: {alert['rule_name']}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def _log_alert(self, alert: Dict[str, Any]):
        """Log alert to application logs"""
        log_level = logging.CRITICAL if alert['severity'] == 'critical' else logging.WARNING
        logger.log(
            log_level,
            f"DATABASE ALERT [{alert['severity'].upper()}] {alert['rule_name']}: "
            f"{alert['description']} - {alert['metric_name']}={alert['metric_value']} "
            f"(threshold: {alert['threshold_value']})"
        )
    
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history for the specified period"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        return [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert["timestamp"]) > cutoff_time
        ]


class DatabaseMonitor:
    """Main database monitoring coordinator"""
    
    def __init__(self):
        self.metrics_collector = DatabaseMetricsCollector()
        self.alert_manager = DatabaseAlertManager()
        self.monitoring_active = False
        self.monitoring_thread = None
        self.stop_event = Event()
        self.collection_interval = int(os.getenv("DB_MONITORING_INTERVAL", "60"))  # seconds
    
    def start_monitoring(self):
        """Start database monitoring"""
        if self.monitoring_active:
            logger.warning("Database monitoring is already active")
            return
        
        self.stop_event.clear()
        self.monitoring_active = True
        
        # Start alert notification processor
        self.alert_manager.start_notification_processor()
        
        # Start monitoring thread
        self.monitoring_thread = Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info(f"Database monitoring started (interval: {self.collection_interval}s)")
    
    def stop_monitoring(self):
        """Stop database monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        self.stop_event.set()
        
        # Stop alert processor
        self.alert_manager.stop_notification_processor()
        
        # Wait for monitoring thread to finish
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        
        logger.info("Database monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self.stop_event.is_set():
            try:
                # Collect metrics
                metrics = self.metrics_collector.collect_all_metrics()
                
                # Check for alerts
                alerts = self.alert_manager.check_alerts(metrics)
                
                if alerts:
                    logger.info(f"Triggered {len(alerts)} alerts")
                
                # Wait for next collection
                self.stop_event.wait(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                self.stop_event.wait(min(self.collection_interval, 30))  # Wait at least 30s on error
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring status and latest metrics"""
        latest_metrics = None
        if self.metrics_collector.metrics_history:
            latest_metrics = self.metrics_collector.metrics_history[-1]
        
        recent_alerts = self.alert_manager.get_alert_history(hours=1)
        
        return {
            "monitoring_active": self.monitoring_active,
            "collection_interval_seconds": self.collection_interval,
            "latest_metrics": latest_metrics,
            "recent_alerts_count": len(recent_alerts),
            "recent_alerts": recent_alerts[:5],  # Last 5 alerts
            "metrics_history_size": len(self.metrics_collector.metrics_history)
        }
    
    def get_health_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive health dashboard data"""
        current_metrics = self.metrics_collector.collect_all_metrics()
        metrics_summary = self.metrics_collector.get_metrics_summary(hours=24)
        recent_alerts = self.alert_manager.get_alert_history(hours=24)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_metrics": current_metrics,
            "24h_summary": metrics_summary,
            "recent_alerts": recent_alerts,
            "alert_summary": {
                "total_alerts_24h": len(recent_alerts),
                "critical_alerts_24h": len([a for a in recent_alerts if a["severity"] == "critical"]),
                "warning_alerts_24h": len([a for a in recent_alerts if a["severity"] == "warning"])
            },
            "monitoring_status": {
                "active": self.monitoring_active,
                "collection_interval": self.collection_interval,
                "uptime_hours": self._get_monitoring_uptime()
            }
        }
    
    def _get_monitoring_uptime(self) -> float:
        """Get monitoring uptime in hours"""
        if not hasattr(self, '_start_time'):
            self._start_time = datetime.now(timezone.utc)
        
        if self.monitoring_active:
            uptime = datetime.now(timezone.utc) - self._start_time
            return uptime.total_seconds() / 3600
        return 0


# Global monitoring instance
database_monitor = DatabaseMonitor()


def start_database_monitoring():
    """Start database monitoring (called from main application)"""
    database_monitor.start_monitoring()


def stop_database_monitoring():
    """Stop database monitoring"""
    database_monitor.stop_monitoring()


def get_monitoring_status():
    """Get current monitoring status"""
    return database_monitor.get_current_status()


def get_health_dashboard():
    """Get health dashboard data"""
    return database_monitor.get_health_dashboard()


if __name__ == "__main__":
    # Test monitoring system
    print("Starting database monitoring test...")
    start_database_monitoring()
    
    try:
        time.sleep(120)  # Monitor for 2 minutes
        status = get_monitoring_status()
        print(f"Monitoring status: {json.dumps(status, indent=2)}")
    finally:
        stop_database_monitoring()