#!/usr/bin/env python3
"""
Production Database Maintenance Script for My Dr AI Medical Assistant
Automated maintenance tasks including vacuum, analyze, reindex, and cleanup
"""
import os
import sys
import logging
import argparse
import time
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from production_database import production_db_manager, backup_manager
from database_monitoring import database_monitor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseMaintenanceManager:
    """Comprehensive database maintenance manager"""
    
    def __init__(self):
        self.maintenance_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tasks_completed": [],
            "tasks_failed": [],
            "warnings": [],
            "statistics": {}
        }
    
    def vacuum_analyze_tables(self, table_names: List[str] = None) -> Dict[str, Any]:
        """Perform VACUUM ANALYZE on specified tables or all tables"""
        task_result = {
            "task": "vacuum_analyze",
            "status": "unknown",
            "details": {},
            "duration_seconds": 0
        }
        
        start_time = time.time()
        
        try:
            with production_db_manager.get_session() as session:
                if table_names:
                    # Vacuum specific tables
                    for table_name in table_names:
                        logger.info(f"Running VACUUM ANALYZE on table: {table_name}")
                        session.execute(f"VACUUM ANALYZE {table_name}")
                        task_result["details"][table_name] = "completed"
                else:
                    # Vacuum all tables
                    logger.info("Running VACUUM ANALYZE on all tables")
                    session.execute("VACUUM ANALYZE")
                    task_result["details"]["all_tables"] = "completed"
                
                session.commit()
                task_result["status"] = "success"
                
        except Exception as e:
            task_result["status"] = "failed"
            task_result["details"]["error"] = str(e)
            logger.error(f"VACUUM ANALYZE failed: {e}")
        
        task_result["duration_seconds"] = round(time.time() - start_time, 2)
        return task_result
    
    def reindex_tables(self, table_names: List[str] = None) -> Dict[str, Any]:
        """Reindex specified tables or all tables"""
        task_result = {
            "task": "reindex",
            "status": "unknown",
            "details": {},
            "duration_seconds": 0
        }
        
        start_time = time.time()
        
        try:
            with production_db_manager.get_session() as session:
                if table_names:
                    # Reindex specific tables
                    for table_name in table_names:
                        logger.info(f"Reindexing table: {table_name}")
                        session.execute(f"REINDEX TABLE {table_name}")
                        task_result["details"][table_name] = "reindexed"
                else:
                    # Reindex entire database
                    logger.info("Reindexing entire database")
                    session.execute("REINDEX DATABASE CONCURRENTLY")
                    task_result["details"]["database"] = "reindexed"
                
                session.commit()
                task_result["status"] = "success"
                
        except Exception as e:
            task_result["status"] = "failed"
            task_result["details"]["error"] = str(e)
            logger.error(f"REINDEX failed: {e}")
        
        task_result["duration_seconds"] = round(time.time() - start_time, 2)
        return task_result
    
    def update_table_statistics(self) -> Dict[str, Any]:
        """Update table statistics for query planner"""
        task_result = {
            "task": "update_statistics",
            "status": "unknown",
            "details": {},
            "duration_seconds": 0
        }
        
        start_time = time.time()
        
        try:
            with production_db_manager.get_session() as session:
                # Get table statistics before update
                before_stats = session.execute("""
                    SELECT schemaname, tablename, n_live_tup, n_dead_tup, last_analyze
                    FROM pg_stat_user_tables
                    ORDER BY n_live_tup DESC
                """).fetchall()
                
                # Run ANALYZE on all tables
                logger.info("Updating table statistics with ANALYZE")
                session.execute("ANALYZE")
                
                # Get table statistics after update
                after_stats = session.execute("""
                    SELECT schemaname, tablename, n_live_tup, n_dead_tup, last_analyze
                    FROM pg_stat_user_tables
                    ORDER BY n_live_tup DESC
                """).fetchall()
                
                task_result["details"] = {
                    "tables_analyzed": len(after_stats),
                    "before_stats": [dict(zip(["schema", "table", "live_tuples", "dead_tuples", "last_analyze"], row)) for row in before_stats[:10]],
                    "after_stats": [dict(zip(["schema", "table", "live_tuples", "dead_tuples", "last_analyze"], row)) for row in after_stats[:10]]
                }
                
                session.commit()
                task_result["status"] = "success"
                
        except Exception as e:
            task_result["status"] = "failed"
            task_result["details"]["error"] = str(e)
            logger.error(f"Statistics update failed: {e}")
        
        task_result["duration_seconds"] = round(time.time() - start_time, 2)
        return task_result
    
    def cleanup_old_data(self, retention_days: int = 90) -> Dict[str, Any]:
        """Clean up old data based on retention policies"""
        task_result = {
            "task": "cleanup_old_data",
            "status": "unknown",
            "details": {},
            "duration_seconds": 0
        }
        
        start_time = time.time()
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        
        try:
            with production_db_manager.get_session() as session:
                cleanup_results = {}
                
                # Clean up old messages (keep conversations but remove old messages)
                old_messages_result = session.execute("""
                    DELETE FROM messages 
                    WHERE created_at < :cutoff_date 
                    AND conversation_id IN (
                        SELECT id FROM conversations 
                        WHERE last_message_at < :cutoff_date - INTERVAL '30 days'
                    )
                """, {"cutoff_date": cutoff_date})
                
                cleanup_results["old_messages_deleted"] = old_messages_result.rowcount
                
                # Clean up old health analytics data (keep recent data)
                old_analytics_result = session.execute("""
                    DELETE FROM health_analytics 
                    WHERE date_recorded < :cutoff_date
                """, {"cutoff_date": cutoff_date})
                
                cleanup_results["old_analytics_deleted"] = old_analytics_result.rowcount
                
                # Clean up orphaned records (if any)
                orphaned_messages_result = session.execute("""
                    DELETE FROM messages 
                    WHERE conversation_id NOT IN (SELECT id FROM conversations)
                """)
                
                cleanup_results["orphaned_messages_deleted"] = orphaned_messages_result.rowcount
                
                task_result["details"] = {
                    "retention_days": retention_days,
                    "cutoff_date": cutoff_date.isoformat(),
                    "cleanup_results": cleanup_results
                }
                
                session.commit()
                task_result["status"] = "success"
                
                logger.info(f"Data cleanup completed: {sum(cleanup_results.values())} records removed")
                
        except Exception as e:
            task_result["status"] = "failed"
            task_result["details"]["error"] = str(e)
            logger.error(f"Data cleanup failed: {e}")
        
        task_result["duration_seconds"] = round(time.time() - start_time, 2)
        return task_result
    
    def optimize_indexes(self) -> Dict[str, Any]:
        """Optimize database indexes"""
        task_result = {
            "task": "optimize_indexes",
            "status": "unknown",
            "details": {},
            "duration_seconds": 0
        }
        
        start_time = time.time()
        
        try:
            with production_db_manager.get_session() as session:
                # Find unused indexes
                unused_indexes_result = session.execute("""
                    SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
                    FROM pg_stat_user_indexes
                    WHERE idx_tup_read = 0
                    AND indexname NOT LIKE '%_pkey'
                    AND indexname NOT LIKE '%_unique'
                """).fetchall()
                
                # Find duplicate indexes
                duplicate_indexes_result = session.execute("""
                    SELECT schemaname, tablename, array_agg(indexname) as index_names, 
                           array_agg(indexdef) as index_definitions
                    FROM (
                        SELECT schemaname, tablename, indexname, 
                               regexp_replace(indexdef, 'CREATE .* INDEX .* ON ', '') as indexdef
                        FROM pg_indexes
                        WHERE schemaname = 'public'
                    ) t
                    GROUP BY schemaname, tablename, indexdef
                    HAVING count(*) > 1
                """).fetchall()
                
                # Get index usage statistics
                index_usage_result = session.execute("""
                    SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch,
                           pg_size_pretty(pg_relation_size(indexrelid)) as index_size
                    FROM pg_stat_user_indexes
                    ORDER BY idx_tup_read DESC
                    LIMIT 20
                """).fetchall()
                
                task_result["details"] = {
                    "unused_indexes": [
                        {
                            "schema": row[0],
                            "table": row[1], 
                            "index": row[2],
                            "reads": row[3],
                            "fetches": row[4]
                        } for row in unused_indexes_result
                    ],
                    "duplicate_indexes": [
                        {
                            "schema": row[0],
                            "table": row[1],
                            "index_names": row[2],
                            "definitions": row[3]
                        } for row in duplicate_indexes_result
                    ],
                    "top_used_indexes": [
                        {
                            "schema": row[0],
                            "table": row[1],
                            "index": row[2],
                            "reads": row[3],
                            "fetches": row[4],
                            "size": row[5]
                        } for row in index_usage_result
                    ]
                }
                
                # Add recommendations
                recommendations = []
                if unused_indexes_result:
                    recommendations.append(f"Consider dropping {len(unused_indexes_result)} unused indexes")
                if duplicate_indexes_result:
                    recommendations.append(f"Found {len(duplicate_indexes_result)} sets of duplicate indexes")
                
                task_result["details"]["recommendations"] = recommendations
                task_result["status"] = "success"
                
        except Exception as e:
            task_result["status"] = "failed"
            task_result["details"]["error"] = str(e)
            logger.error(f"Index optimization analysis failed: {e}")
        
        task_result["duration_seconds"] = round(time.time() - start_time, 2)
        return task_result
    
    def check_database_bloat(self) -> Dict[str, Any]:
        """Check for table and index bloat"""
        task_result = {
            "task": "check_bloat",
            "status": "unknown",
            "details": {},
            "duration_seconds": 0
        }
        
        start_time = time.time()
        
        try:
            with production_db_manager.get_session() as session:
                # Check table bloat
                table_bloat_result = session.execute("""
                    SELECT schemaname, tablename, n_live_tup, n_dead_tup,
                           CASE WHEN n_live_tup > 0 
                                THEN round((n_dead_tup::numeric / n_live_tup::numeric) * 100, 2)
                                ELSE 0 
                           END as bloat_ratio
                    FROM pg_stat_user_tables
                    WHERE n_dead_tup > 1000
                    ORDER BY bloat_ratio DESC
                """).fetchall()
                
                # Check index bloat (simplified estimation)
                index_bloat_result = session.execute("""
                    SELECT schemaname, tablename, indexname,
                           pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
                           idx_tup_read, idx_tup_fetch
                    FROM pg_stat_user_indexes
                    WHERE pg_relation_size(indexrelid) > 100 * 1024 * 1024  -- > 100MB
                    ORDER BY pg_relation_size(indexrelid) DESC
                """).fetchall()
                
                task_result["details"] = {
                    "table_bloat": [
                        {
                            "schema": row[0],
                            "table": row[1],
                            "live_tuples": row[2],
                            "dead_tuples": row[3],
                            "bloat_ratio": float(row[4])
                        } for row in table_bloat_result
                    ],
                    "large_indexes": [
                        {
                            "schema": row[0],
                            "table": row[1],
                            "index": row[2],
                            "size": row[3],
                            "reads": row[4],
                            "fetches": row[5]
                        } for row in index_bloat_result
                    ]
                }
                
                # Add recommendations based on bloat
                recommendations = []
                high_bloat_tables = [t for t in task_result["details"]["table_bloat"] if t["bloat_ratio"] > 20]
                if high_bloat_tables:
                    recommendations.append(f"Consider VACUUM FULL on {len(high_bloat_tables)} tables with high bloat")
                
                task_result["details"]["recommendations"] = recommendations
                task_result["status"] = "success"
                
        except Exception as e:
            task_result["status"] = "failed"
            task_result["details"]["error"] = str(e)
            logger.error(f"Bloat check failed: {e}")
        
        task_result["duration_seconds"] = round(time.time() - start_time, 2)
        return task_result
    
    def create_maintenance_backup(self) -> Dict[str, Any]:
        """Create a backup before maintenance operations"""
        task_result = {
            "task": "maintenance_backup",
            "status": "unknown",
            "details": {},
            "duration_seconds": 0
        }
        
        start_time = time.time()
        
        try:
            logger.info("Creating pre-maintenance backup...")
            backup_result = backup_manager.create_backup("maintenance")
            
            task_result["details"] = backup_result
            task_result["status"] = backup_result["status"]
            
            if backup_result["status"] == "success":
                logger.info(f"Maintenance backup created: {backup_result['backup_file']}")
            else:
                logger.error(f"Maintenance backup failed: {backup_result.get('error')}")
                
        except Exception as e:
            task_result["status"] = "failed"
            task_result["details"]["error"] = str(e)
            logger.error(f"Maintenance backup failed: {e}")
        
        task_result["duration_seconds"] = round(time.time() - start_time, 2)
        return task_result
    
    def run_maintenance_tasks(self, tasks: List[str] = None, create_backup: bool = True) -> Dict[str, Any]:
        """Run specified maintenance tasks"""
        logger.info("Starting database maintenance...")
        
        if tasks is None:
            tasks = ["backup", "vacuum_analyze", "update_statistics", "optimize_indexes", "check_bloat", "cleanup_old_data"]
        
        maintenance_start = time.time()
        
        # Create backup if requested
        if create_backup and "backup" in tasks:
            backup_result = self.create_maintenance_backup()
            if backup_result["status"] == "success":
                self.maintenance_report["tasks_completed"].append(backup_result)
            else:
                self.maintenance_report["tasks_failed"].append(backup_result)
                self.maintenance_report["warnings"].append("Pre-maintenance backup failed")
        
        # Run maintenance tasks
        task_functions = {
            "vacuum_analyze": lambda: self.vacuum_analyze_tables(),
            "update_statistics": self.update_table_statistics,
            "optimize_indexes": self.optimize_indexes,
            "check_bloat": self.check_database_bloat,
            "cleanup_old_data": lambda: self.cleanup_old_data(retention_days=90),
            "reindex": lambda: self.reindex_tables()
        }
        
        for task_name in tasks:
            if task_name == "backup":
                continue  # Already handled
                
            if task_name not in task_functions:
                self.maintenance_report["warnings"].append(f"Unknown task: {task_name}")
                continue
            
            logger.info(f"Running maintenance task: {task_name}")
            
            try:
                task_result = task_functions[task_name]()
                
                if task_result["status"] == "success":
                    self.maintenance_report["tasks_completed"].append(task_result)
                    logger.info(f"✓ {task_name} completed in {task_result['duration_seconds']}s")
                else:
                    self.maintenance_report["tasks_failed"].append(task_result)
                    logger.error(f"✗ {task_name} failed: {task_result['details'].get('error')}")
                    
            except Exception as e:
                error_result = {
                    "task": task_name,
                    "status": "failed",
                    "details": {"error": str(e)},
                    "duration_seconds": 0
                }
                self.maintenance_report["tasks_failed"].append(error_result)
                logger.error(f"✗ {task_name} failed with exception: {e}")
        
        # Collect final statistics
        try:
            final_stats = production_db_manager.get_database_statistics()
            self.maintenance_report["statistics"] = {
                "final_database_stats": final_stats,
                "total_maintenance_time": round(time.time() - maintenance_start, 2)
            }
        except Exception as e:
            self.maintenance_report["warnings"].append(f"Failed to collect final statistics: {e}")
        
        # Generate summary
        total_tasks = len(self.maintenance_report["tasks_completed"]) + len(self.maintenance_report["tasks_failed"])
        success_rate = (len(self.maintenance_report["tasks_completed"]) / total_tasks * 100) if total_tasks > 0 else 0
        
        self.maintenance_report["summary"] = {
            "total_tasks": total_tasks,
            "successful_tasks": len(self.maintenance_report["tasks_completed"]),
            "failed_tasks": len(self.maintenance_report["tasks_failed"]),
            "success_rate": round(success_rate, 1),
            "total_duration": round(time.time() - maintenance_start, 2)
        }
        
        logger.info("Database maintenance completed")
        logger.info(f"Success rate: {success_rate:.1f}% ({len(self.maintenance_report['tasks_completed'])}/{total_tasks})")
        
        return self.maintenance_report


def main():
    """Main maintenance function"""
    parser = argparse.ArgumentParser(description="Database Maintenance for MyDoc AI")
    parser.add_argument("--tasks", nargs="+", 
                       choices=["backup", "vacuum_analyze", "update_statistics", "optimize_indexes", 
                               "check_bloat", "cleanup_old_data", "reindex"],
                       help="Specific maintenance tasks to run")
    parser.add_argument("--no-backup", action="store_true", help="Skip pre-maintenance backup")
    parser.add_argument("--retention-days", type=int, default=90, 
                       help="Data retention period for cleanup (default: 90 days)")
    parser.add_argument("--save-report", help="Save maintenance report to specified file")
    
    args = parser.parse_args()
    
    # Ensure log directory exists
    os.makedirs("/var/log/mydoc", exist_ok=True)
    
    maintenance_manager = DatabaseMaintenanceManager()
    
    # Run maintenance tasks
    report = maintenance_manager.run_maintenance_tasks(
        tasks=args.tasks,
        create_backup=not args.no_backup
    )
    
    # Display summary
    print("=" * 60)
    print("DATABASE MAINTENANCE REPORT")
    print("=" * 60)
    print(f"Timestamp: {report['timestamp']}")
    print(f"Total Tasks: {report['summary']['total_tasks']}")
    print(f"Successful: {report['summary']['successful_tasks']}")
    print(f"Failed: {report['summary']['failed_tasks']}")
    print(f"Success Rate: {report['summary']['success_rate']}%")
    print(f"Total Duration: {report['summary']['total_duration']}s")
    print()
    
    if report["warnings"]:
        print("WARNINGS:")
        for warning in report["warnings"]:
            print(f"⚠ {warning}")
        print()
    
    # Save report if requested
    if args.save_report:
        try:
            import json
            os.makedirs(os.path.dirname(args.save_report), exist_ok=True)
            with open(args.save_report, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Maintenance report saved to: {args.save_report}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
    
    # Exit with appropriate code
    if report["summary"]["failed_tasks"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()