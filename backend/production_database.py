"""
Production Database Infrastructure for My Dr AI Medical Assistant
Comprehensive PostgreSQL setup with connection pooling, monitoring, and backup systems
"""
import os
import logging
import asyncio
import time
import json
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
from sqlalchemy import create_engine, text, event, exc, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import psycopg2
from psycopg2 import sql
import asyncpg
from production_config import load_production_settings

# Load production settings
try:
    settings = load_production_settings()
except Exception as e:
    # Fallback to development config if production config fails
    from config import Settings
    settings = Settings()

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Production database configuration"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    database: str = os.getenv("DB_NAME", "mydoc_production")
    username: str = os.getenv("DB_USER", "mydoc_user")
    password: str = os.getenv("DB_PASSWORD", "")
    
    # Connection pool settings
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "20"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "30"))
    pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    # Performance settings
    statement_timeout: int = int(os.getenv("DB_STATEMENT_TIMEOUT", "300"))
    idle_in_transaction_timeout: int = int(os.getenv("DB_IDLE_TIMEOUT", "60"))
    
    # SSL settings
    ssl_mode: str = os.getenv("DB_SSL_MODE", "prefer")
    ssl_cert: Optional[str] = os.getenv("DB_SSL_CERT")
    ssl_key: Optional[str] = os.getenv("DB_SSL_KEY")
    ssl_ca: Optional[str] = os.getenv("DB_SSL_CA")
    
    def get_sync_url(self) -> str:
        """Get synchronous database URL"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def get_async_url(self) -> str:
        """Get asynchronous database URL"""
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def get_connection_args(self) -> Dict[str, Any]:
        """Get connection arguments for PostgreSQL"""
        args = {
            "connect_timeout": 10,
            "application_name": "MyDr_Medical_Assistant",
            "options": f"-c timezone=UTC -c statement_timeout={self.statement_timeout}s -c idle_in_transaction_session_timeout={self.idle_in_transaction_timeout}s"
        }
        
        if self.ssl_mode != "disable":
            args["sslmode"] = self.ssl_mode
            if self.ssl_cert:
                args["sslcert"] = self.ssl_cert
            if self.ssl_key:
                args["sslkey"] = self.ssl_key
            if self.ssl_ca:
                args["sslrootcert"] = self.ssl_ca
        
        return args


class ProductionDatabaseManager:
    """Production database manager with comprehensive monitoring and backup"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.sync_engine: Optional[Engine] = None
        self.async_engine = None
        self.sync_session_factory = None
        self.async_session_factory = None
        self._health_metrics = {}
        self._last_health_check = None
        
    def create_sync_engine(self) -> Engine:
        """Create synchronous PostgreSQL engine with optimized settings"""
        if self.sync_engine:
            return self.sync_engine
        
        try:
            self.sync_engine = create_engine(
                self.config.get_sync_url(),
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_pre_ping=True,
                pool_recycle=self.config.pool_recycle,
                pool_timeout=self.config.pool_timeout,
                echo=settings.debug,
                echo_pool=settings.debug,
                connect_args=self.config.get_connection_args(),
                # PostgreSQL specific optimizations
                execution_options={
                    "isolation_level": "READ_COMMITTED",
                    "autocommit": False
                }
            )
            
            # Add event listeners for monitoring
            self._setup_engine_events(self.sync_engine)
            
            logger.info(f"Production PostgreSQL engine created - Pool size: {self.config.pool_size}, Max overflow: {self.config.max_overflow}")
            return self.sync_engine
            
        except Exception as e:
            logger.error(f"Failed to create production database engine: {e}")
            raise
    
    async def create_async_engine(self):
        """Create asynchronous PostgreSQL engine"""
        if self.async_engine:
            return self.async_engine
        
        try:
            self.async_engine = create_async_engine(
                self.config.get_async_url(),
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_pre_ping=True,
                pool_recycle=self.config.pool_recycle,
                echo=settings.debug,
                connect_args={
                    "command_timeout": self.config.statement_timeout,
                    "server_settings": {
                        "application_name": "MyDr_Medical_Assistant_Async",
                        "timezone": "UTC"
                    }
                }
            )
            
            logger.info("Production async PostgreSQL engine created")
            return self.async_engine
            
        except Exception as e:
            logger.error(f"Failed to create async database engine: {e}")
            raise
    
    def _setup_engine_events(self, engine: Engine):
        """Setup engine event listeners for monitoring"""
        
        @event.listens_for(engine, "connect")
        def set_postgresql_settings(dbapi_connection, connection_record):
            """Set PostgreSQL connection settings for medical data optimization"""
            with dbapi_connection.cursor() as cursor:
                # Set timezone and timeouts
                cursor.execute("SET timezone TO 'UTC'")
                cursor.execute(f"SET statement_timeout = '{self.config.statement_timeout}s'")
                cursor.execute(f"SET idle_in_transaction_session_timeout = '{self.config.idle_in_transaction_timeout}s'")
                
                # Optimize for medical data workload
                cursor.execute("SET work_mem = '256MB'")  # Larger work memory for analytics
                cursor.execute("SET maintenance_work_mem = '512MB'")
                cursor.execute("SET effective_cache_size = '4GB'")
                cursor.execute("SET random_page_cost = 1.1")  # SSD optimization
                cursor.execute("SET seq_page_cost = 1.0")
                
                # Enable query planning optimizations
                cursor.execute("SET enable_hashjoin = on")
                cursor.execute("SET enable_mergejoin = on")
                cursor.execute("SET enable_nestloop = on")
                
            logger.debug("PostgreSQL connection optimized for medical data workload")
        
        @event.listens_for(engine, "checkout")
        def log_connection_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection checkout for monitoring"""
            self._health_metrics["connections_checked_out"] = self._health_metrics.get("connections_checked_out", 0) + 1
            logger.debug(f"Connection checked out. Pool status: {engine.pool.status()}")
        
        @event.listens_for(engine, "checkin")
        def log_connection_checkin(dbapi_connection, connection_record):
            """Log connection checkin"""
            self._health_metrics["connections_checked_in"] = self._health_metrics.get("connections_checked_in", 0) + 1
            logger.debug("Connection returned to pool")
        
        @event.listens_for(engine, "invalidate")
        def log_connection_invalidate(dbapi_connection, connection_record, exception):
            """Log connection invalidation"""
            self._health_metrics["connections_invalidated"] = self._health_metrics.get("connections_invalidated", 0) + 1
            logger.warning(f"Connection invalidated: {exception}")
    
    def create_session_factories(self):
        """Create session factories"""
        engine = self.create_sync_engine()
        self.sync_session_factory = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
        logger.info("Production database session factories created")
    
    async def create_async_session_factory(self):
        """Create async session factory"""
        engine = await self.create_async_engine()
        self.async_session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
        logger.info("Production async database session factory created")
    
    def get_session(self) -> Session:
        """Get synchronous database session"""
        if not self.sync_session_factory:
            self.create_session_factories()
        return self.sync_session_factory()
    
    @asynccontextmanager
    async def get_async_session(self):
        """Get asynchronous database session"""
        if not self.async_session_factory:
            await self.create_async_session_factory()
        
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """Test database connection"""
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT version(), current_database(), current_user"))
                version_info = result.fetchone()
                logger.info(f"Database connection successful: {version_info}")
                return True, None
        except Exception as e:
            error_msg = f"Database connection failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    async def test_async_connection(self) -> Tuple[bool, Optional[str]]:
        """Test async database connection"""
        try:
            async with self.get_async_session() as session:
                result = await session.execute(text("SELECT version(), current_database(), current_user"))
                version_info = result.fetchone()
                logger.info(f"Async database connection successful: {version_info}")
                return True, None
        except Exception as e:
            error_msg = f"Async database connection failed: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def comprehensive_health_check(self) -> Dict[str, Any]:
        """Comprehensive database health check"""
        health_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "unknown",
            "database_info": {},
            "connection_pool": {},
            "performance_metrics": {},
            "storage_info": {},
            "replication_status": {},
            "errors": []
        }
        
        try:
            start_time = time.time()
            
            with self.get_session() as session:
                # Database version and info
                result = session.execute(text("""
                    SELECT version(), current_database(), current_user, 
                           current_setting('server_version_num')::int as version_num
                """))
                db_info = result.fetchone()
                
                health_data["database_info"] = {
                    "version": db_info[0],
                    "database": db_info[1],
                    "user": db_info[2],
                    "version_number": db_info[3]
                }
                
                # Connection pool status
                pool = self.sync_engine.pool
                health_data["connection_pool"] = {
                    "size": pool.size(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                    "checked_in": pool.checkedin(),
                    "status": pool.status()
                }
                
                # Performance metrics
                perf_start = time.time()
                session.execute(text("SELECT COUNT(*) FROM pg_stat_activity"))
                query_time = (time.time() - perf_start) * 1000
                
                health_data["performance_metrics"] = {
                    "simple_query_ms": round(query_time, 2),
                    "total_check_time_ms": round((time.time() - start_time) * 1000, 2)
                }
                
                # Database size and storage info
                storage_result = session.execute(text("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as db_size,
                           pg_database_size(current_database()) as db_size_bytes
                """))
                storage_info = storage_result.fetchone()
                
                health_data["storage_info"] = {
                    "database_size": storage_info[0],
                    "database_size_bytes": storage_info[1]
                }
                
                # Active connections
                connections_result = session.execute(text("""
                    SELECT count(*) as total_connections,
                           count(*) FILTER (WHERE state = 'active') as active_connections,
                           count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """))
                conn_info = connections_result.fetchone()
                
                health_data["connection_pool"]["active_connections"] = conn_info[1]
                health_data["connection_pool"]["idle_connections"] = conn_info[2]
                health_data["connection_pool"]["total_connections"] = conn_info[0]
                
                # Check for long-running queries
                long_queries_result = session.execute(text("""
                    SELECT count(*) as long_running_queries
                    FROM pg_stat_activity 
                    WHERE state = 'active' 
                    AND query_start < now() - interval '5 minutes'
                    AND datname = current_database()
                """))
                long_queries = long_queries_result.scalar()
                
                health_data["performance_metrics"]["long_running_queries"] = long_queries
                
                # Determine overall health status
                total_time = (time.time() - start_time) * 1000
                
                if total_time < 100 and long_queries == 0:
                    health_data["status"] = "healthy"
                elif total_time < 500 and long_queries < 5:
                    health_data["status"] = "degraded"
                else:
                    health_data["status"] = "unhealthy"
                
        except Exception as e:
            health_data["status"] = "unhealthy"
            health_data["errors"].append(str(e))
            logger.error(f"Health check failed: {e}")
        
        self._health_metrics.update(health_data)
        self._last_health_check = datetime.now(timezone.utc)
        
        return health_data
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        stats = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "table_statistics": {},
            "index_usage": {},
            "query_performance": {},
            "storage_details": {}
        }
        
        try:
            with self.get_session() as session:
                # Table statistics
                table_stats_result = session.execute(text("""
                    SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del, 
                           n_live_tup, n_dead_tup, last_vacuum, last_autovacuum, 
                           last_analyze, last_autoanalyze
                    FROM pg_stat_user_tables
                    ORDER BY n_live_tup DESC
                """))
                
                table_stats = []
                for row in table_stats_result:
                    table_stats.append({
                        "schema": row[0],
                        "table": row[1],
                        "inserts": row[2],
                        "updates": row[3],
                        "deletes": row[4],
                        "live_tuples": row[5],
                        "dead_tuples": row[6],
                        "last_vacuum": row[7].isoformat() if row[7] else None,
                        "last_autovacuum": row[8].isoformat() if row[8] else None,
                        "last_analyze": row[9].isoformat() if row[9] else None,
                        "last_autoanalyze": row[10].isoformat() if row[10] else None
                    })
                
                stats["table_statistics"] = table_stats
                
                # Index usage statistics
                index_stats_result = session.execute(text("""
                    SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
                    FROM pg_stat_user_indexes
                    ORDER BY idx_tup_read DESC
                    LIMIT 20
                """))
                
                index_stats = []
                for row in index_stats_result:
                    index_stats.append({
                        "schema": row[0],
                        "table": row[1],
                        "index": row[2],
                        "tuples_read": row[3],
                        "tuples_fetched": row[4]
                    })
                
                stats["index_usage"] = index_stats
                
                # Storage details by table
                storage_result = session.execute(text("""
                    SELECT schemaname, tablename, 
                           pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
                           pg_total_relation_size(schemaname||'.'||tablename) as total_size_bytes,
                           pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
                           pg_relation_size(schemaname||'.'||tablename) as table_size_bytes
                    FROM pg_tables 
                    WHERE schemaname = 'public'
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                """))
                
                storage_details = []
                for row in storage_result:
                    storage_details.append({
                        "schema": row[0],
                        "table": row[1],
                        "total_size": row[2],
                        "total_size_bytes": row[3],
                        "table_size": row[4],
                        "table_size_bytes": row[5]
                    })
                
                stats["storage_details"] = storage_details
                
        except Exception as e:
            stats["error"] = str(e)
            logger.error(f"Failed to get database statistics: {e}")
        
        return stats
    
    def optimize_database(self) -> Dict[str, Any]:
        """Optimize database performance"""
        optimization_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actions_performed": [],
            "recommendations": [],
            "errors": []
        }
        
        try:
            with self.get_session() as session:
                # Run ANALYZE on all tables
                session.execute(text("ANALYZE"))
                optimization_results["actions_performed"].append("ANALYZE all tables")
                
                # Get vacuum recommendations
                vacuum_result = session.execute(text("""
                    SELECT schemaname, tablename, n_dead_tup, n_live_tup,
                           CASE WHEN n_live_tup > 0 
                                THEN round(n_dead_tup::numeric / n_live_tup::numeric, 3)
                                ELSE 0 
                           END as dead_ratio
                    FROM pg_stat_user_tables
                    WHERE n_dead_tup > 1000
                    ORDER BY dead_ratio DESC
                """))
                
                tables_needing_vacuum = []
                for row in vacuum_result:
                    if row[4] > 0.1:  # More than 10% dead tuples
                        tables_needing_vacuum.append(f"{row[0]}.{row[1]}")
                        optimization_results["recommendations"].append(
                            f"Consider VACUUM on {row[0]}.{row[1]} (dead ratio: {row[4]})"
                        )
                
                # Check for unused indexes
                unused_indexes_result = session.execute(text("""
                    SELECT schemaname, tablename, indexname, idx_tup_read
                    FROM pg_stat_user_indexes
                    WHERE idx_tup_read = 0
                    AND indexname NOT LIKE '%_pkey'
                """))
                
                for row in unused_indexes_result:
                    optimization_results["recommendations"].append(
                        f"Consider dropping unused index: {row[2]} on {row[0]}.{row[1]}"
                    )
                
                session.commit()
                
        except Exception as e:
            optimization_results["errors"].append(str(e))
            logger.error(f"Database optimization failed: {e}")
        
        return optimization_results


class DatabaseBackupManager:
    """Comprehensive database backup and recovery system"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.backup_dir = os.getenv("DB_BACKUP_DIR", "/var/backups/mydoc")
        
    def create_backup(self, backup_type: str = "full") -> Dict[str, Any]:
        """Create database backup using pg_dump"""
        backup_result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "backup_type": backup_type,
            "status": "unknown",
            "backup_file": None,
            "size_bytes": 0,
            "duration_seconds": 0,
            "error": None
        }
        
        try:
            # Ensure backup directory exists
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"mydoc_backup_{backup_type}_{timestamp}.sql"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            start_time = time.time()
            
            # Prepare pg_dump command
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config.password
            
            cmd = [
                "pg_dump",
                "-h", self.config.host,
                "-p", str(self.config.port),
                "-U", self.config.username,
                "-d", self.config.database,
                "-f", backup_path,
                "--verbose",
                "--no-password"
            ]
            
            if backup_type == "schema_only":
                cmd.append("--schema-only")
            elif backup_type == "data_only":
                cmd.append("--data-only")
            
            # Execute backup
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                backup_result["status"] = "success"
                backup_result["backup_file"] = backup_path
                backup_result["size_bytes"] = os.path.getsize(backup_path)
                backup_result["duration_seconds"] = round(duration, 2)
                
                logger.info(f"Database backup created successfully: {backup_path}")
            else:
                backup_result["status"] = "failed"
                backup_result["error"] = result.stderr
                logger.error(f"Database backup failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            backup_result["status"] = "timeout"
            backup_result["error"] = "Backup operation timed out"
            logger.error("Database backup timed out")
            
        except Exception as e:
            backup_result["status"] = "failed"
            backup_result["error"] = str(e)
            logger.error(f"Database backup failed: {e}")
        
        return backup_result
    
    def restore_backup(self, backup_file: str) -> Dict[str, Any]:
        """Restore database from backup"""
        restore_result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "backup_file": backup_file,
            "status": "unknown",
            "duration_seconds": 0,
            "error": None
        }
        
        try:
            if not os.path.exists(backup_file):
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
            start_time = time.time()
            
            # Prepare psql command for restore
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config.password
            
            cmd = [
                "psql",
                "-h", self.config.host,
                "-p", str(self.config.port),
                "-U", self.config.username,
                "-d", self.config.database,
                "-f", backup_file,
                "--no-password"
            ]
            
            # Execute restore
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                restore_result["status"] = "success"
                restore_result["duration_seconds"] = round(duration, 2)
                logger.info(f"Database restored successfully from: {backup_file}")
            else:
                restore_result["status"] = "failed"
                restore_result["error"] = result.stderr
                logger.error(f"Database restore failed: {result.stderr}")
                
        except Exception as e:
            restore_result["status"] = "failed"
            restore_result["error"] = str(e)
            logger.error(f"Database restore failed: {e}")
        
        return restore_result
    
    def schedule_automated_backups(self) -> Dict[str, Any]:
        """Setup automated backup scheduling (returns cron configuration)"""
        cron_config = {
            "daily_full_backup": {
                "schedule": "0 2 * * *",  # Daily at 2 AM
                "command": f"python -c \"from backend.production_database import create_automated_backup; create_automated_backup('full')\""
            },
            "hourly_incremental": {
                "schedule": "0 * * * *",  # Every hour
                "command": f"python -c \"from backend.production_database import create_automated_backup; create_automated_backup('incremental')\""
            },
            "weekly_schema": {
                "schedule": "0 1 * * 0",  # Weekly on Sunday at 1 AM
                "command": f"python -c \"from backend.production_database import create_automated_backup; create_automated_backup('schema_only')\""
            }
        }
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cron_configuration": cron_config,
            "backup_directory": self.backup_dir,
            "instructions": "Add these cron jobs to your system crontab for automated backups"
        }
    
    def cleanup_old_backups(self, retention_days: int = 30) -> Dict[str, Any]:
        """Clean up old backup files"""
        cleanup_result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "retention_days": retention_days,
            "files_removed": [],
            "space_freed_bytes": 0,
            "error": None
        }
        
        try:
            if not os.path.exists(self.backup_dir):
                return cleanup_result
            
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            total_freed = 0
            
            for filename in os.listdir(self.backup_dir):
                if filename.startswith("mydoc_backup_") and filename.endswith(".sql"):
                    file_path = os.path.join(self.backup_dir, filename)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_mtime < cutoff_date:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        cleanup_result["files_removed"].append(filename)
                        total_freed += file_size
            
            cleanup_result["space_freed_bytes"] = total_freed
            logger.info(f"Cleaned up {len(cleanup_result['files_removed'])} old backup files, freed {total_freed} bytes")
            
        except Exception as e:
            cleanup_result["error"] = str(e)
            logger.error(f"Backup cleanup failed: {e}")
        
        return cleanup_result


# Global instances
db_config = DatabaseConfig()
production_db_manager = ProductionDatabaseManager(db_config)
backup_manager = DatabaseBackupManager(db_config)


def create_automated_backup(backup_type: str = "full"):
    """Function for automated backup creation (called by cron)"""
    try:
        result = backup_manager.create_backup(backup_type)
        
        if result["status"] == "success":
            logger.info(f"Automated {backup_type} backup completed successfully")
            
            # Cleanup old backups after successful backup
            cleanup_result = backup_manager.cleanup_old_backups()
            logger.info(f"Backup cleanup completed: {len(cleanup_result['files_removed'])} files removed")
            
        else:
            logger.error(f"Automated {backup_type} backup failed: {result.get('error')}")
            
    except Exception as e:
        logger.error(f"Automated backup process failed: {e}")


# Database initialization for production
def initialize_production_database():
    """Initialize production database with all optimizations"""
    try:
        # Test connection
        success, error = production_db_manager.test_connection()
        if not success:
            raise Exception(f"Database connection failed: {error}")
        
        # Create session factories
        production_db_manager.create_session_factories()
        
        # Run health check
        health = production_db_manager.comprehensive_health_check()
        logger.info(f"Database health check: {health['status']}")
        
        # Create initial backup
        backup_result = backup_manager.create_backup("schema_only")
        if backup_result["status"] == "success":
            logger.info("Initial schema backup created")
        
        logger.info("Production database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize production database: {e}")
        return False


if __name__ == "__main__":
    # Test production database setup
    initialize_production_database()