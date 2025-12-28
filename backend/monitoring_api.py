"""
Monitoring and Health Dashboard API for My Dr AI Medical Assistant
Provides endpoints for system health monitoring, metrics, and alerts
"""
import os
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import asyncio

from auth_middleware import get_current_user, require_auth
from models import User
from logging_system import get_medical_logger, logging_system
from performance_monitoring import performance_monitor, get_system_health
from database_monitoring import DatabaseMetricsCollector, DatabaseAlertManager

logger = get_medical_logger("monitoring_api")

# Create router
router = APIRouter(prefix="/monitoring", tags=["monitoring"])


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Overall system status")
    health_score: int = Field(..., description="Health score (0-100)")
    timestamp: str = Field(..., description="Check timestamp")
    components: Dict[str, Any] = Field(..., description="Component health status")
    monitoring_active: bool = Field(..., description="Whether monitoring is active")


class MetricsResponse(BaseModel):
    """Metrics response model"""
    period_minutes: int = Field(..., description="Time period for metrics")
    system_metrics: Dict[str, Any] = Field(..., description="System performance metrics")
    database_metrics: Dict[str, Any] = Field(..., description="Database performance metrics")
    application_metrics: Dict[str, Any] = Field(..., description="Application metrics")
    timestamp: str = Field(..., description="Collection timestamp")


class AlertsResponse(BaseModel):
    """Alerts response model"""
    period_hours: int = Field(..., description="Time period for alerts")
    total_alerts: int = Field(..., description="Total number of alerts")
    critical_alerts: int = Field(..., description="Number of critical alerts")
    warning_alerts: int = Field(..., description="Number of warning alerts")
    alerts: List[Dict[str, Any]] = Field(..., description="Alert details")
    timestamp: str = Field(..., description="Collection timestamp")


class LogsResponse(BaseModel):
    """Logs response model"""
    total_entries: int = Field(..., description="Total log entries")
    entries: List[Dict[str, Any]] = Field(..., description="Log entries")
    filters_applied: Dict[str, Any] = Field(..., description="Applied filters")
    timestamp: str = Field(..., description="Collection timestamp")


# Initialize monitoring components
db_metrics_collector = DatabaseMetricsCollector()
db_alert_manager = DatabaseAlertManager()


@router.get("/health", response_model=HealthCheckResponse)
async def get_system_health_status():
    """Get comprehensive system health status"""
    try:
        # Get overall system health
        health_status = get_system_health()
        
        # Get database health
        db_metrics = db_metrics_collector.collect_all_metrics()
        db_health_score = db_metrics.get("health_score", 0)
        
        # Component health checks
        components = {
            "application": {
                "status": "healthy" if health_status["health_score"] > 70 else "degraded",
                "health_score": health_status["health_score"],
                "cpu_percent": health_status["current_metrics"]["cpu_percent"],
                "memory_percent": health_status["current_metrics"]["memory_percent"],
                "response_time_ms": health_status["current_metrics"]["response_time_avg_ms"],
                "error_rate": health_status["current_metrics"]["error_rate_percent"]
            },
            "database": {
                "status": "healthy" if db_health_score > 70 else "degraded",
                "health_score": db_health_score,
                "connection_pool_utilization": db_metrics.get("connection_metrics", {}).get("pool_utilization", 0),
                "cache_hit_ratio": db_metrics.get("performance_metrics", {}).get("cache_hit_ratio", 0),
                "query_time_ms": db_metrics.get("performance_metrics", {}).get("simple_query_ms", 0)
            },
            "logging": {
                "status": "healthy" if logging_system.is_configured else "degraded",
                "configured": logging_system.is_configured,
                "log_files": len(logging_system.get_log_files())
            },
            "monitoring": {
                "status": "healthy" if performance_monitor.monitoring_active else "inactive",
                "active": performance_monitor.monitoring_active,
                "interval_seconds": performance_monitor.monitoring_interval
            }
        }
        
        # Calculate overall status
        component_scores = [comp.get("health_score", 100) for comp in components.values() if "health_score" in comp]
        overall_score = int(sum(component_scores) / len(component_scores)) if component_scores else 0
        
        if overall_score >= 90:
            overall_status = "excellent"
        elif overall_score >= 75:
            overall_status = "good"
        elif overall_score >= 50:
            overall_status = "fair"
        elif overall_score >= 25:
            overall_status = "poor"
        else:
            overall_status = "critical"
        
        return HealthCheckResponse(
            status=overall_status,
            health_score=overall_score,
            timestamp=datetime.now(timezone.utc).isoformat(),
            components=components,
            monitoring_active=performance_monitor.monitoring_active
        )
        
    except Exception as e:
        logger.error(f"Failed to get system health status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system health status")


@router.get("/metrics", response_model=MetricsResponse)
async def get_system_metrics(
    period_minutes: int = Query(60, description="Time period in minutes", ge=1, le=1440),
    current_user: User = Depends(require_auth)
):
    """Get comprehensive system metrics"""
    try:
        # Get system metrics
        system_metrics = performance_monitor.metrics_collector.get_metrics_summary(period_minutes)
        
        # Get database metrics
        db_metrics = db_metrics_collector.collect_all_metrics()
        db_summary = db_metrics_collector.get_metrics_summary(period_minutes // 60)
        
        # Get application-specific metrics
        error_summary = performance_monitor.metrics_collector.get_error_summary(period_minutes // 60)
        
        return MetricsResponse(
            period_minutes=period_minutes,
            system_metrics=system_metrics,
            database_metrics=db_summary,
            application_metrics=error_summary,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system metrics")


@router.get("/alerts", response_model=AlertsResponse)
async def get_system_alerts(
    period_hours: int = Query(24, description="Time period in hours", ge=1, le=168),
    severity: Optional[str] = Query(None, description="Filter by severity (warning, critical)"),
    current_user: User = Depends(require_auth)
):
    """Get system alerts"""
    try:
        # Get performance alerts
        perf_alert_summary = performance_monitor.alert_manager.get_alert_summary(period_hours)
        
        # Get database alerts
        db_alerts = []
        try:
            # Check current database metrics for alerts
            db_metrics = db_metrics_collector.collect_all_metrics()
            db_triggered_alerts = db_alert_manager.check_alerts(db_metrics)
            db_alerts = [alert for alert in db_triggered_alerts]
        except Exception as e:
            logger.warning(f"Failed to get database alerts: {e}")
        
        # Combine alerts
        all_alerts = perf_alert_summary.get("recent_alerts", []) + db_alerts
        
        # Filter by severity if specified
        if severity:
            all_alerts = [alert for alert in all_alerts if alert.get("severity") == severity]
        
        # Count by severity
        critical_count = sum(1 for alert in all_alerts if alert.get("severity") == "critical")
        warning_count = sum(1 for alert in all_alerts if alert.get("severity") == "warning")
        
        return AlertsResponse(
            period_hours=period_hours,
            total_alerts=len(all_alerts),
            critical_alerts=critical_count,
            warning_alerts=warning_count,
            alerts=all_alerts,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to get system alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system alerts")


@router.get("/logs", response_model=LogsResponse)
async def get_system_logs(
    level: Optional[str] = Query(None, description="Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    module: Optional[str] = Query(None, description="Filter by module name"),
    limit: int = Query(100, description="Maximum number of entries", ge=1, le=1000),
    offset: int = Query(0, description="Offset for pagination", ge=0),
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    current_user: User = Depends(require_auth)
):
    """Get system logs with filtering"""
    try:
        log_entries = []
        filters_applied = {
            "level": level,
            "module": module,
            "limit": limit,
            "offset": offset,
            "start_time": start_time,
            "end_time": end_time
        }
        
        # Read log files
        log_files = logging_system.get_log_files()
        
        for log_file in log_files:
            if not log_file.suffix == '.jsonl':
                continue
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f):
                        if line_num < offset:
                            continue
                        if len(log_entries) >= limit:
                            break
                        
                        try:
                            log_entry = json.loads(line.strip())
                            
                            # Apply filters
                            if level and log_entry.get("level") != level:
                                continue
                            if module and module not in log_entry.get("logger", ""):
                                continue
                            
                            # Time filters
                            if start_time:
                                entry_time = datetime.fromisoformat(log_entry["timestamp"].replace('Z', '+00:00'))
                                filter_start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                                if entry_time < filter_start:
                                    continue
                            
                            if end_time:
                                entry_time = datetime.fromisoformat(log_entry["timestamp"].replace('Z', '+00:00'))
                                filter_end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                                if entry_time > filter_end:
                                    continue
                            
                            log_entries.append(log_entry)
                            
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                logger.warning(f"Failed to read log file {log_file}: {e}")
                continue
        
        # Sort by timestamp (most recent first)
        log_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return LogsResponse(
            total_entries=len(log_entries),
            entries=log_entries,
            filters_applied=filters_applied,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to get system logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system logs")


@router.get("/dashboard")
async def get_monitoring_dashboard(
    current_user: User = Depends(require_auth)
):
    """Get comprehensive monitoring dashboard data"""
    try:
        # Get all monitoring data
        health_status = await get_system_health_status()
        metrics = await get_system_metrics(period_minutes=60)
        alerts = await get_system_alerts(period_hours=24)
        
        # Get recent performance trends
        recent_metrics = performance_monitor.metrics_collector.get_metrics_summary(60)
        
        # Calculate trends
        trends = {
            "cpu_trend": "stable",  # Would calculate based on historical data
            "memory_trend": "stable",
            "response_time_trend": "stable",
            "error_rate_trend": "stable"
        }
        
        return {
            "health": health_status,
            "metrics": metrics,
            "alerts": alerts,
            "trends": trends,
            "summary": {
                "total_requests_last_hour": recent_metrics.get("total_samples", 0),
                "average_response_time": recent_metrics.get("response_time_stats", {}).get("avg", 0),
                "error_rate": recent_metrics.get("error_rate_stats", {}).get("current", 0),
                "active_alerts": alerts.total_alerts,
                "system_uptime": "99.9%",  # Would calculate from actual uptime data
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get monitoring dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve monitoring dashboard")


@router.post("/monitoring/start")
async def start_monitoring(
    interval_seconds: int = Query(30, description="Monitoring interval in seconds", ge=10, le=300),
    current_user: User = Depends(require_auth)
):
    """Start performance monitoring"""
    try:
        if performance_monitor.monitoring_active:
            return {"message": "Monitoring is already active", "status": "active"}
        
        performance_monitor.start_monitoring(interval_seconds)
        
        logger.info(f"Performance monitoring started by user {current_user.email}",
                   interval_seconds=interval_seconds)
        
        return {
            "message": "Performance monitoring started successfully",
            "status": "active",
            "interval_seconds": interval_seconds,
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to start monitoring: {e}")
        raise HTTPException(status_code=500, detail="Failed to start performance monitoring")


@router.post("/monitoring/stop")
async def stop_monitoring(
    current_user: User = Depends(require_auth)
):
    """Stop performance monitoring"""
    try:
        if not performance_monitor.monitoring_active:
            return {"message": "Monitoring is not active", "status": "inactive"}
        
        performance_monitor.stop_monitoring()
        
        logger.info(f"Performance monitoring stopped by user {current_user.email}")
        
        return {
            "message": "Performance monitoring stopped successfully",
            "status": "inactive",
            "stopped_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to stop monitoring: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop performance monitoring")


@router.get("/logs/download")
async def download_logs(
    log_type: str = Query("app", description="Log type (app, error, performance)"),
    current_user: User = Depends(require_auth)
):
    """Download log files"""
    try:
        log_files = logging_system.get_log_files()
        
        # Find the requested log file
        target_file = None
        for log_file in log_files:
            if log_type == "app" and "mydoc_app" in log_file.name:
                target_file = log_file
                break
            elif log_type == "error" and "mydoc_errors" in log_file.name:
                target_file = log_file
                break
            elif log_type == "performance" and "mydoc_performance" in log_file.name:
                target_file = log_file
                break
        
        if not target_file or not target_file.exists():
            raise HTTPException(status_code=404, detail="Log file not found")
        
        logger.info(f"Log file download requested by user {current_user.email}",
                   log_type=log_type,
                   file_path=str(target_file))
        
        return FileResponse(
            path=str(target_file),
            filename=f"mydoc_{log_type}_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl",
            media_type="application/json"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to download log file")


@router.delete("/logs/cleanup")
async def cleanup_old_logs(
    days_to_keep: int = Query(30, description="Number of days to keep logs", ge=1, le=365),
    current_user: User = Depends(require_auth)
):
    """Clean up old log files"""
    try:
        logging_system.cleanup_old_logs(days_to_keep)
        
        logger.info(f"Log cleanup performed by user {current_user.email}",
                   days_to_keep=days_to_keep)
        
        return {
            "message": f"Log cleanup completed - kept logs from last {days_to_keep} days",
            "days_kept": days_to_keep,
            "cleaned_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup log files")


# Health check endpoint (public)
@router.get("/ping")
async def ping():
    """Simple health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "MyDoc AI Medical Assistant Monitoring"
    }


@router.get("/dashboard-ui")
async def get_health_dashboard_ui():
    """Serve the health dashboard HTML page"""
    try:
        dashboard_path = Path(__file__).parent / "templates" / "health_dashboard.html"
        
        if not dashboard_path.exists():
            raise HTTPException(status_code=404, detail="Dashboard template not found")
        
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to serve health dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to load health dashboard")