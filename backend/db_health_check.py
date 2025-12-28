#!/usr/bin/env python3
"""
Production Database Health Check Script for My Dr AI Medical Assistant
Comprehensive health monitoring and alerting for production database
"""
import os
import sys
import json
import logging
import argparse
from typing import Dict, Any
from datetime import datetime, timezone

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from production_database import production_db_manager, backup_manager
from database_monitoring import database_monitor, get_monitoring_status, get_health_dashboard

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseHealthChecker:
    """Comprehensive database health checker"""
    
    def __init__(self):
        self.health_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "unknown",
            "health_score": 0,
            "checks": {},
            "alerts": [],
            "recommendations": []
        }
    
    def check_connection_health(self) -> Dict[str, Any]:
        """Check database connection health"""
        check_result = {
            "name": "Connection Health",
            "status": "unknown",
            "details": {},
            "score": 0
        }
        
        try:
            # Test synchronous connection
            sync_success, sync_error = production_db_manager.test_connection()
            
            # Test asynchronous connection
            import asyncio
            async def test_async():
                return await production_db_manager.test_async_connection()
            
            async_success, async_error = asyncio.run(test_async())
            
            check_result["details"] = {
                "sync_connection": {
                    "success": sync_success,
                    "error": sync_error
                },
                "async_connection": {
                    "success": async_success,
                    "error": async_error
                }
            }
            
            if sync_success and async_success:
                check_result["status"] = "healthy"
                check_result["score"] = 100
            elif sync_success or async_success:
                check_result["status"] = "degraded"
                check_result["score"] = 50
                self.health_report["alerts"].append("One connection type is failing")
            else:
                check_result["status"] = "unhealthy"
                check_result["score"] = 0
                self.health_report["alerts"].append("All database connections are failing")
                
        except Exception as e:
            check_result["status"] = "error"
            check_result["details"]["error"] = str(e)
            check_result["score"] = 0
            self.health_report["alerts"].append(f"Connection health check failed: {e}")
        
        return check_result
    
    def check_performance_health(self) -> Dict[str, Any]:
        """Check database performance health"""
        check_result = {
            "name": "Performance Health",
            "status": "unknown",
            "details": {},
            "score": 0
        }
        
        try:
            health_data = production_db_manager.comprehensive_health_check()
            perf_metrics = health_data.get("performance_metrics", {})
            
            query_time = perf_metrics.get("simple_query_ms", 0)
            cache_hit_ratio = perf_metrics.get("cache_hit_ratio", 0)
            long_queries = health_data.get("query_metrics", {}).get("long_running_count", 0)
            
            check_result["details"] = {
                "query_time_ms": query_time,
                "cache_hit_ratio": cache_hit_ratio,
                "long_running_queries": long_queries,
                "total_check_time_ms": perf_metrics.get("total_check_time_ms", 0)
            }
            
            # Calculate performance score
            score = 100
            
            if query_time > 1000:
                score -= 40
                self.health_report["alerts"].append(f"Very slow query performance: {query_time}ms")
            elif query_time > 500:
                score -= 20
                self.health_report["alerts"].append(f"Slow query performance: {query_time}ms")
            elif query_time > 100:
                score -= 10
            
            if cache_hit_ratio < 80:
                score -= 30
                self.health_report["alerts"].append(f"Low cache hit ratio: {cache_hit_ratio}%")
                self.health_report["recommendations"].append("Consider increasing shared_buffers or work_mem")
            elif cache_hit_ratio < 90:
                score -= 15
            
            if long_queries > 10:
                score -= 20
                self.health_report["alerts"].append(f"Too many long-running queries: {long_queries}")
            elif long_queries > 5:
                score -= 10
            
            check_result["score"] = max(0, score)
            
            if score >= 80:
                check_result["status"] = "healthy"
            elif score >= 50:
                check_result["status"] = "degraded"
            else:
                check_result["status"] = "unhealthy"
                
        except Exception as e:
            check_result["status"] = "error"
            check_result["details"]["error"] = str(e)
            check_result["score"] = 0
            self.health_report["alerts"].append(f"Performance health check failed: {e}")
        
        return check_result
    
    def check_connection_pool_health(self) -> Dict[str, Any]:
        """Check connection pool health"""
        check_result = {
            "name": "Connection Pool Health",
            "status": "unknown",
            "details": {},
            "score": 0
        }
        
        try:
            health_data = production_db_manager.comprehensive_health_check()
            pool_metrics = health_data.get("connection_pool", {})
            
            pool_size = pool_metrics.get("size", 0)
            checked_out = pool_metrics.get("checked_out", 0)
            overflow = pool_metrics.get("overflow", 0)
            utilization = (checked_out / pool_size * 100) if pool_size > 0 else 0
            
            check_result["details"] = {
                "pool_size": pool_size,
                "checked_out": checked_out,
                "overflow": overflow,
                "utilization_percent": round(utilization, 2),
                "active_connections": pool_metrics.get("active_connections", 0),
                "idle_connections": pool_metrics.get("idle_connections", 0)
            }
            
            # Calculate pool health score
            score = 100
            
            if utilization > 90:
                score -= 40
                self.health_report["alerts"].append(f"Very high pool utilization: {utilization:.1f}%")
                self.health_report["recommendations"].append("Consider increasing connection pool size")
            elif utilization > 75:
                score -= 20
                self.health_report["alerts"].append(f"High pool utilization: {utilization:.1f}%")
            elif utilization > 50:
                score -= 10
            
            if overflow > pool_size * 0.5:
                score -= 20
                self.health_report["alerts"].append(f"High overflow connections: {overflow}")
            
            check_result["score"] = max(0, score)
            
            if score >= 80:
                check_result["status"] = "healthy"
            elif score >= 50:
                check_result["status"] = "degraded"
            else:
                check_result["status"] = "unhealthy"
                
        except Exception as e:
            check_result["status"] = "error"
            check_result["details"]["error"] = str(e)
            check_result["score"] = 0
            self.health_report["alerts"].append(f"Connection pool health check failed: {e}")
        
        return check_result
    
    def check_storage_health(self) -> Dict[str, Any]:
        """Check database storage health"""
        check_result = {
            "name": "Storage Health",
            "status": "unknown",
            "details": {},
            "score": 0
        }
        
        try:
            health_data = production_db_manager.comprehensive_health_check()
            storage_info = health_data.get("storage_info", {})
            
            db_size_bytes = storage_info.get("database_size_bytes", 0)
            db_size_gb = db_size_bytes / (1024**3) if db_size_bytes else 0
            
            # Get system disk usage
            import psutil
            disk_usage = psutil.disk_usage('/')
            disk_free_gb = disk_usage.free / (1024**3)
            disk_used_percent = (disk_usage.used / disk_usage.total) * 100
            
            check_result["details"] = {
                "database_size_gb": round(db_size_gb, 2),
                "database_size_pretty": storage_info.get("database_size", "Unknown"),
                "disk_free_gb": round(disk_free_gb, 2),
                "disk_used_percent": round(disk_used_percent, 2)
            }
            
            # Calculate storage health score
            score = 100
            
            if disk_used_percent > 90:
                score -= 50
                self.health_report["alerts"].append(f"Critical disk usage: {disk_used_percent:.1f}%")
                self.health_report["recommendations"].append("Immediate disk cleanup required")
            elif disk_used_percent > 80:
                score -= 30
                self.health_report["alerts"].append(f"High disk usage: {disk_used_percent:.1f}%")
                self.health_report["recommendations"].append("Consider disk cleanup or expansion")
            elif disk_used_percent > 70:
                score -= 15
            
            if disk_free_gb < 1:
                score -= 30
                self.health_report["alerts"].append(f"Very low disk space: {disk_free_gb:.1f}GB")
            elif disk_free_gb < 5:
                score -= 15
                self.health_report["alerts"].append(f"Low disk space: {disk_free_gb:.1f}GB")
            
            check_result["score"] = max(0, score)
            
            if score >= 80:
                check_result["status"] = "healthy"
            elif score >= 50:
                check_result["status"] = "degraded"
            else:
                check_result["status"] = "unhealthy"
                
        except Exception as e:
            check_result["status"] = "error"
            check_result["details"]["error"] = str(e)
            check_result["score"] = 0
            self.health_report["alerts"].append(f"Storage health check failed: {e}")
        
        return check_result
    
    def check_backup_health(self) -> Dict[str, Any]:
        """Check backup system health"""
        check_result = {
            "name": "Backup System Health",
            "status": "unknown",
            "details": {},
            "score": 0
        }
        
        try:
            backup_dir = backup_manager.backup_dir
            
            # Check if backup directory exists
            if not os.path.exists(backup_dir):
                check_result["status"] = "unhealthy"
                check_result["details"]["error"] = "Backup directory does not exist"
                check_result["score"] = 0
                self.health_report["alerts"].append("Backup directory missing")
                return check_result
            
            # List backup files
            backup_files = []
            total_backup_size = 0
            
            for filename in os.listdir(backup_dir):
                if filename.endswith('.sql'):
                    filepath = os.path.join(backup_dir, filename)
                    file_stat = os.stat(filepath)
                    backup_files.append({
                        "filename": filename,
                        "size_bytes": file_stat.st_size,
                        "modified": datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc).isoformat()
                    })
                    total_backup_size += file_stat.st_size
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x["modified"], reverse=True)
            
            check_result["details"] = {
                "backup_directory": backup_dir,
                "total_backups": len(backup_files),
                "total_size_gb": round(total_backup_size / (1024**3), 2),
                "recent_backups": backup_files[:5]  # Show 5 most recent
            }
            
            # Calculate backup health score
            score = 100
            
            if len(backup_files) == 0:
                score = 0
                self.health_report["alerts"].append("No backup files found")
                self.health_report["recommendations"].append("Create initial database backup")
            else:
                # Check age of most recent backup
                most_recent = datetime.fromisoformat(backup_files[0]["modified"].replace('Z', '+00:00'))
                age_hours = (datetime.now(timezone.utc) - most_recent).total_seconds() / 3600
                
                if age_hours > 48:
                    score -= 40
                    self.health_report["alerts"].append(f"Most recent backup is {age_hours:.1f} hours old")
                    self.health_report["recommendations"].append("Check automated backup system")
                elif age_hours > 24:
                    score -= 20
                    self.health_report["alerts"].append(f"Backup is {age_hours:.1f} hours old")
                
                check_result["details"]["most_recent_backup_age_hours"] = round(age_hours, 1)
            
            check_result["score"] = max(0, score)
            
            if score >= 80:
                check_result["status"] = "healthy"
            elif score >= 50:
                check_result["status"] = "degraded"
            else:
                check_result["status"] = "unhealthy"
                
        except Exception as e:
            check_result["status"] = "error"
            check_result["details"]["error"] = str(e)
            check_result["score"] = 0
            self.health_report["alerts"].append(f"Backup health check failed: {e}")
        
        return check_result
    
    def check_monitoring_health(self) -> Dict[str, Any]:
        """Check monitoring system health"""
        check_result = {
            "name": "Monitoring System Health",
            "status": "unknown",
            "details": {},
            "score": 0
        }
        
        try:
            monitoring_status = get_monitoring_status()
            
            check_result["details"] = {
                "monitoring_active": monitoring_status.get("monitoring_active", False),
                "uptime_hours": monitoring_status.get("uptime_hours", 0),
                "last_check": monitoring_status.get("last_check"),
                "metrics_collected": monitoring_status.get("metrics_collected", 0)
            }
            
            if monitoring_status.get("monitoring_active"):
                check_result["status"] = "healthy"
                check_result["score"] = 100
            else:
                check_result["status"] = "unhealthy"
                check_result["score"] = 0
                self.health_report["alerts"].append("Database monitoring is not active")
                self.health_report["recommendations"].append("Start database monitoring service")
                
        except Exception as e:
            check_result["status"] = "error"
            check_result["details"]["error"] = str(e)
            check_result["score"] = 0
            self.health_report["alerts"].append(f"Monitoring health check failed: {e}")
        
        return check_result
    
    def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run all health checks"""
        logger.info("Running comprehensive database health check...")
        
        health_checks = [
            self.check_connection_health,
            self.check_performance_health,
            self.check_connection_pool_health,
            self.check_storage_health,
            self.check_backup_health,
            self.check_monitoring_health
        ]
        
        total_score = 0
        successful_checks = 0
        
        for check_function in health_checks:
            try:
                check_result = check_function()
                self.health_report["checks"][check_result["name"]] = check_result
                
                if check_result["status"] != "error":
                    total_score += check_result["score"]
                    successful_checks += 1
                    
                logger.info(f"✓ {check_result['name']}: {check_result['status']} (score: {check_result['score']})")
                
            except Exception as e:
                logger.error(f"✗ Health check failed: {e}")
                self.health_report["alerts"].append(f"Health check error: {e}")
        
        # Calculate overall health score
        if successful_checks > 0:
            self.health_report["health_score"] = round(total_score / successful_checks, 1)
        else:
            self.health_report["health_score"] = 0
        
        # Determine overall status
        if self.health_report["health_score"] >= 80:
            self.health_report["overall_status"] = "healthy"
        elif self.health_report["health_score"] >= 50:
            self.health_report["overall_status"] = "degraded"
        else:
            self.health_report["overall_status"] = "unhealthy"
        
        # Add general recommendations
        if self.health_report["health_score"] < 80:
            self.health_report["recommendations"].append("Review database configuration and performance")
        
        if len(self.health_report["alerts"]) > 5:
            self.health_report["recommendations"].append("Multiple issues detected - consider comprehensive database maintenance")
        
        return self.health_report


def main():
    """Main health check function"""
    parser = argparse.ArgumentParser(description="Database Health Check for MyDoc AI")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--save-report", help="Save report to specified file")
    parser.add_argument("--alert-threshold", type=int, default=70, 
                       help="Health score threshold for alerts (default: 70)")
    
    args = parser.parse_args()
    
    checker = DatabaseHealthChecker()
    health_report = checker.run_comprehensive_health_check()
    
    if args.json:
        print(json.dumps(health_report, indent=2))
    else:
        # Human-readable output
        print("=" * 60)
        print("DATABASE HEALTH CHECK REPORT")
        print("=" * 60)
        print(f"Timestamp: {health_report['timestamp']}")
        print(f"Overall Status: {health_report['overall_status'].upper()}")
        print(f"Health Score: {health_report['health_score']}/100")
        print()
        
        # Individual check results
        print("INDIVIDUAL CHECKS:")
        print("-" * 40)
        for check_name, check_result in health_report["checks"].items():
            status_symbol = "✓" if check_result["status"] == "healthy" else "⚠" if check_result["status"] == "degraded" else "✗"
            print(f"{status_symbol} {check_name}: {check_result['status']} ({check_result['score']}/100)")
        print()
        
        # Alerts
        if health_report["alerts"]:
            print("ALERTS:")
            print("-" * 40)
            for alert in health_report["alerts"]:
                print(f"⚠ {alert}")
            print()
        
        # Recommendations
        if health_report["recommendations"]:
            print("RECOMMENDATIONS:")
            print("-" * 40)
            for rec in health_report["recommendations"]:
                print(f"• {rec}")
            print()
    
    # Save report if requested
    if args.save_report:
        try:
            os.makedirs(os.path.dirname(args.save_report), exist_ok=True)
            with open(args.save_report, 'w') as f:
                json.dump(health_report, f, indent=2)
            logger.info(f"Health report saved to: {args.save_report}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
    
    # Exit with appropriate code based on health score
    if health_report["health_score"] < args.alert_threshold:
        logger.warning(f"Health score {health_report['health_score']} is below threshold {args.alert_threshold}")
        sys.exit(1)
    else:
        logger.info("Database health check passed")
        sys.exit(0)


if __name__ == "__main__":
    main()