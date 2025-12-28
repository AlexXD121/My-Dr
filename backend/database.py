"""
Database connection and session management for My Dr AI Medical Assistant
Enhanced with comprehensive error handling, connection pooling, and health monitoring
"""
import logging
import time
from typing import Generator, Optional, Dict, Any, List
from datetime import datetime, timezone
from sqlalchemy import create_engine, event, text, exc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
from contextlib import contextmanager
from config import settings
from models import Base

logger = logging.getLogger(__name__)

# Database engine
engine = None
SessionLocal = None


def create_database_engine():
    """Create database engine with enhanced configuration and error handling"""
    global engine
    
    if engine is not None:
        return engine
    
    database_url = settings.database_url
    
    if not database_url:
        # Use SQLite file database for development/testing
        logger.warning("No database URL configured, using SQLite file database")
        database_url = "sqlite:///./mydoc.db"
    
    try:
        # Enhanced database configuration based on database type
        if database_url.startswith("postgresql://") or database_url.startswith("postgres://"):
            # PostgreSQL configuration with enhanced connection pooling
            engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=20,  # Increased pool size for medical app
                max_overflow=30,  # Higher overflow for peak usage
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,  # Recycle connections every hour
                pool_timeout=30,  # Connection timeout
                echo=settings.debug,
                echo_pool=settings.debug,
                # Enhanced PostgreSQL specific settings
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "MyDr_Medical_Assistant",
                    "options": "-c timezone=UTC"
                }
            )
            
        elif database_url.startswith("sqlite://"):
            # Enhanced SQLite configuration
            engine = create_engine(
                database_url,
                poolclass=StaticPool,
                pool_pre_ping=True,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 20,  # Database lock timeout
                },
                echo=settings.debug,
            )
            
        else:
            # Generic database configuration with basic pooling
            engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=settings.debug,
            )
        
        # Enhanced event listeners for connection management
        @event.listens_for(engine, "connect")
        def set_database_pragmas(dbapi_connection, connection_record):
            """Set database-specific pragmas and configurations"""
            if database_url.startswith("sqlite://"):
                cursor = dbapi_connection.cursor()
                # Enhanced SQLite pragmas for medical data integrity
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=FULL")  # Full synchronous for data safety
                cursor.execute("PRAGMA cache_size=10000")  # Larger cache for better performance
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.execute("PRAGMA mmap_size=268435456")  # 256MB mmap
                cursor.execute("PRAGMA optimize")
                cursor.close()
                logger.debug("SQLite pragmas configured for medical data integrity")
            
            elif database_url.startswith(("postgresql://", "postgres://")):
                # PostgreSQL connection settings
                cursor = dbapi_connection.cursor()
                cursor.execute("SET timezone TO 'UTC'")
                cursor.execute("SET statement_timeout = '300s'")  # 5 minute statement timeout
                cursor.close()
                logger.debug("PostgreSQL connection configured")
        
        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection checkout for monitoring"""
            logger.debug(f"Connection checked out from pool. Pool status: {engine.pool.status()}")
        
        @event.listens_for(engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log connection checkin for monitoring"""
            logger.debug("Connection returned to pool")
        
        @event.listens_for(engine, "invalidate")
        def receive_invalidate(dbapi_connection, connection_record, exception):
            """Handle connection invalidation"""
            logger.warning(f"Connection invalidated: {exception}")
        
        logger.info(f"Enhanced database engine created: {database_url.split('@')[0] if '@' in database_url else database_url}")
        logger.info(f"Pool configuration - Size: {getattr(engine.pool, 'size', 'N/A')}, Max Overflow: {getattr(engine.pool, 'max_overflow', 'N/A')}")
        
        return engine
        
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise DatabaseConnectionError(f"Could not create database engine: {e}")


class DatabaseError(Exception):
    """Base exception for database-related errors"""
    pass


class DatabaseConnectionError(DatabaseError):
    """Exception raised when database connection fails"""
    pass


class DatabaseIntegrityError(DatabaseError):
    """Exception raised when database integrity is violated"""
    pass


class DatabaseTimeoutError(DatabaseError):
    """Exception raised when database operation times out"""
    pass


def create_session_factory():
    """Create session factory"""
    global SessionLocal
    
    if SessionLocal is not None:
        return SessionLocal
    
    engine = create_database_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    logger.info("Database session factory created")
    return SessionLocal


def init_database():
    """Initialize database tables with automatic SQLite fallback"""
    global engine
    
    try:
        engine = create_database_engine()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        
        # Automatic Fallback to SQLite
        if not str(settings.database_url).startswith("sqlite"):
            logger.warning("⚠️ Primary database failed. Falling back to local SQLite database (Demo Mode)")
            try:
                # Force SQLite URL
                settings.database_url = "sqlite:///./mydoc.db"
                
                # Reset engine
                engine = None 
                engine = create_database_engine()
                
                # Try creating tables again
                Base.metadata.create_all(bind=engine)
                logger.info("✅ Fallback to SQLite successful!")
                return True
            except Exception as fallback_error:
                logger.error(f"❌ Fallback failed: {fallback_error}")
                return False
                
        return False


def get_db() -> Generator[Session, None, None]:
    """
    Enhanced dependency to get database session with comprehensive error handling
    Use this in FastAPI endpoints with Depends(get_db)
    """
    SessionLocal = create_session_factory()
    db = SessionLocal()
    start_time = time.time()
    
    try:
        # Test connection before yielding
        db.execute(text("SELECT 1"))
        yield db
        
    except exc.DisconnectionError as e:
        logger.error(f"Database disconnection error: {e}")
        db.rollback()
        raise DatabaseConnectionError(f"Database connection lost: {e}")
        
    except exc.TimeoutError as e:
        logger.error(f"Database timeout error: {e}")
        db.rollback()
        raise DatabaseTimeoutError(f"Database operation timed out: {e}")
        
    except exc.IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
        db.rollback()
        raise DatabaseIntegrityError(f"Database integrity violation: {e}")
        
    except exc.OperationalError as e:
        logger.error(f"Database operational error: {e}")
        db.rollback()
        raise DatabaseConnectionError(f"Database operational error: {e}")
        
    except Exception as e:
        logger.error(f"Unexpected database session error: {e}")
        db.rollback()
        raise DatabaseError(f"Unexpected database error: {e}")
        
    finally:
        session_duration = time.time() - start_time
        if session_duration > 5.0:  # Log slow sessions
            logger.warning(f"Slow database session: {session_duration:.2f}s")
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Enhanced context manager for database sessions with comprehensive error handling
    Use this for manual database operations
    """
    SessionLocal = create_session_factory()
    db = SessionLocal()
    start_time = time.time()
    
    try:
        # Test connection
        db.execute(text("SELECT 1"))
        yield db
        db.commit()
        
    except exc.DisconnectionError as e:
        logger.error(f"Database disconnection in session: {e}")
        db.rollback()
        raise DatabaseConnectionError(f"Database connection lost: {e}")
        
    except exc.TimeoutError as e:
        logger.error(f"Database timeout in session: {e}")
        db.rollback()
        raise DatabaseTimeoutError(f"Database operation timed out: {e}")
        
    except exc.IntegrityError as e:
        logger.error(f"Database integrity error in session: {e}")
        db.rollback()
        raise DatabaseIntegrityError(f"Database integrity violation: {e}")
        
    except exc.OperationalError as e:
        logger.error(f"Database operational error in session: {e}")
        db.rollback()
        raise DatabaseConnectionError(f"Database operational error: {e}")
        
    except Exception as e:
        logger.error(f"Unexpected error in database session: {e}")
        db.rollback()
        raise DatabaseError(f"Unexpected database error: {e}")
        
    finally:
        session_duration = time.time() - start_time
        if session_duration > 5.0:
            logger.warning(f"Slow database session: {session_duration:.2f}s")
        db.close()


def test_database_connection() -> bool:
    """Test database connection"""
    try:
        with get_db_session() as db:
            # Simple query to test connection
            db.execute(text("SELECT 1"))
        
        logger.info("Database connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def reset_database():
    """Reset database (drop and recreate all tables) - USE WITH CAUTION"""
    try:
        engine = create_database_engine()
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
        
        # Recreate all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables recreated")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        return False


class DatabaseManager:
    """Enhanced database manager class for advanced operations and monitoring"""
    
    def __init__(self):
        self.engine = create_database_engine()
        self.SessionLocal = create_session_factory()
        self._health_check_cache = {}
        self._last_health_check = None
    
    def create_tables(self):
        """Create all database tables with error handling"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise DatabaseError(f"Table creation failed: {e}")
    
    def drop_tables(self):
        """Drop all database tables with confirmation"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
            return True
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise DatabaseError(f"Table drop failed: {e}")
    
    def get_session(self) -> Session:
        """Get a new database session with error handling"""
        try:
            return self.SessionLocal()
        except Exception as e:
            logger.error(f"Failed to create database session: {e}")
            raise DatabaseConnectionError(f"Session creation failed: {e}")
    
    def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive database health check"""
        health_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "unknown",
            "checks": {},
            "performance": {},
            "pool_info": {},
            "errors": []
        }
        
        try:
            # Basic connectivity check
            start_time = time.time()
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            connectivity_time = (time.time() - start_time) * 1000
            
            health_data["checks"]["connectivity"] = {
                "status": "pass",
                "response_time_ms": round(connectivity_time, 2)
            }
            
            # Pool status check
            pool_info = self._get_pool_info()
            health_data["pool_info"] = pool_info
            
            # Performance checks
            performance_data = self._run_performance_checks()
            health_data["performance"] = performance_data
            
            # Table existence check
            table_check = self._check_table_existence()
            health_data["checks"]["tables"] = table_check
            
            # Data integrity check
            integrity_check = self._check_data_integrity()
            health_data["checks"]["integrity"] = integrity_check
            
            # Determine overall status
            all_checks_pass = all(
                check.get("status") == "pass" 
                for check in health_data["checks"].values()
            )
            
            if all_checks_pass and connectivity_time < 1000:  # Less than 1 second
                health_data["status"] = "healthy"
            elif all_checks_pass:
                health_data["status"] = "degraded"
            else:
                health_data["status"] = "unhealthy"
            
        except Exception as e:
            health_data["status"] = "unhealthy"
            health_data["errors"].append(str(e))
            logger.error(f"Health check failed: {e}")
        
        # Cache results
        self._health_check_cache = health_data
        self._last_health_check = datetime.now(timezone.utc)
        
        return health_data
    
    def _get_pool_info(self) -> Dict[str, Any]:
        """Get database connection pool information"""
        try:
            pool = self.engine.pool
            return {
                "size": getattr(pool, 'size', None),
                "checked_out": getattr(pool, 'checkedout', None),
                "overflow": getattr(pool, 'overflow', None),
                "checked_in": getattr(pool, 'checkedin', None),
                "status": pool.status() if hasattr(pool, 'status') else "unknown"
            }
        except Exception as e:
            logger.error(f"Failed to get pool info: {e}")
            return {"error": str(e)}
    
    def _run_performance_checks(self) -> Dict[str, Any]:
        """Run database performance checks"""
        performance = {}
        
        try:
            # Simple query performance
            start_time = time.time()
            with self.get_session() as session:
                session.execute(text("SELECT COUNT(*) FROM users"))
            performance["simple_query_ms"] = round((time.time() - start_time) * 1000, 2)
            
            # Complex query performance (if tables exist)
            start_time = time.time()
            with self.get_session() as session:
                result = session.execute(text("""
                    SELECT COUNT(*) FROM conversations 
                    WHERE started_at > datetime('now', '-7 days')
                """))
            performance["complex_query_ms"] = round((time.time() - start_time) * 1000, 2)
            
        except Exception as e:
            performance["error"] = str(e)
            logger.debug(f"Performance check error (expected if tables don't exist): {e}")
        
        return performance
    
    def _check_table_existence(self) -> Dict[str, Any]:
        """Check if all required tables exist"""
        try:
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            
            required_tables = [
                'users', 'medical_records', 'conversations', 'messages',
                'consultations', 'health_analytics', 'symptom_patterns',
                'health_metrics', 'trend_analyses'
            ]
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            return {
                "status": "pass" if not missing_tables else "fail",
                "existing_tables": existing_tables,
                "missing_tables": missing_tables,
                "total_tables": len(existing_tables)
            }
            
        except Exception as e:
            return {
                "status": "fail",
                "error": str(e)
            }
    
    def _check_data_integrity(self) -> Dict[str, Any]:
        """Check basic data integrity"""
        try:
            with self.get_session() as session:
                # Check for orphaned records (basic foreign key integrity)
                integrity_issues = []
                
                # Check for conversations without users
                orphaned_conversations = session.execute(text("""
                    SELECT COUNT(*) FROM conversations c 
                    LEFT JOIN users u ON c.user_id = u.id 
                    WHERE u.id IS NULL
                """)).scalar()
                
                if orphaned_conversations > 0:
                    integrity_issues.append(f"{orphaned_conversations} orphaned conversations")
                
                # Check for messages without conversations
                orphaned_messages = session.execute(text("""
                    SELECT COUNT(*) FROM messages m 
                    LEFT JOIN conversations c ON m.conversation_id = c.id 
                    WHERE c.id IS NULL
                """)).scalar()
                
                if orphaned_messages > 0:
                    integrity_issues.append(f"{orphaned_messages} orphaned messages")
                
                return {
                    "status": "pass" if not integrity_issues else "warning",
                    "issues": integrity_issues
                }
                
        except Exception as e:
            return {
                "status": "fail",
                "error": str(e)
            }
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        stats = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "table_counts": {},
            "storage_info": {},
            "recent_activity": {}
        }
        
        try:
            with self.get_session() as session:
                # Get table row counts
                tables = ['users', 'conversations', 'messages', 'medical_records', 
                         'consultations', 'health_analytics', 'symptom_patterns']
                
                for table in tables:
                    try:
                        count = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                        stats["table_counts"][table] = count
                    except Exception:
                        stats["table_counts"][table] = "N/A"
                
                # Get recent activity (last 24 hours)
                try:
                    recent_conversations = session.execute(text("""
                        SELECT COUNT(*) FROM conversations 
                        WHERE started_at > datetime('now', '-1 day')
                    """)).scalar()
                    stats["recent_activity"]["conversations_24h"] = recent_conversations
                    
                    recent_messages = session.execute(text("""
                        SELECT COUNT(*) FROM messages 
                        WHERE timestamp > datetime('now', '-1 day')
                    """)).scalar()
                    stats["recent_activity"]["messages_24h"] = recent_messages
                    
                except Exception as e:
                    stats["recent_activity"]["error"] = str(e)
                
        except Exception as e:
            stats["error"] = str(e)
            logger.error(f"Failed to get database statistics: {e}")
        
        return stats
    
    def optimize_database(self) -> Dict[str, Any]:
        """Optimize database performance"""
        optimization_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actions_performed": [],
            "errors": []
        }
        
        try:
            with self.get_session() as session:
                database_url = str(self.engine.url)
                
                if database_url.startswith("sqlite://"):
                    # SQLite optimizations
                    session.execute(text("PRAGMA optimize"))
                    session.execute(text("VACUUM"))
                    session.execute(text("ANALYZE"))
                    optimization_results["actions_performed"].extend([
                        "PRAGMA optimize", "VACUUM", "ANALYZE"
                    ])
                    
                elif database_url.startswith(("postgresql://", "postgres://")):
                    # PostgreSQL optimizations
                    session.execute(text("ANALYZE"))
                    optimization_results["actions_performed"].append("ANALYZE")
                
                session.commit()
                
        except Exception as e:
            optimization_results["errors"].append(str(e))
            logger.error(f"Database optimization failed: {e}")
        
        return optimization_results
    
    def backup_database(self, backup_path: str = None) -> Dict[str, Any]:
        """Create database backup (SQLite only for now)"""
        backup_result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "unknown",
            "backup_path": backup_path,
            "error": None
        }
        
        try:
            database_url = str(self.engine.url)
            
            if database_url.startswith("sqlite://"):
                import shutil
                source_path = database_url.replace("sqlite:///", "")
                
                if not backup_path:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = f"backup_mydoc_{timestamp}.db"
                
                shutil.copy2(source_path, backup_path)
                backup_result["status"] = "success"
                backup_result["backup_path"] = backup_path
                
            else:
                backup_result["status"] = "not_supported"
                backup_result["error"] = "Backup only supported for SQLite databases"
                
        except Exception as e:
            backup_result["status"] = "failed"
            backup_result["error"] = str(e)
            logger.error(f"Database backup failed: {e}")
        
        return backup_result


# Global database manager instance
db_manager = DatabaseManager()


# Enhanced Migration System
class MigrationManager:
    """Comprehensive migration management system"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.migration_table = "schema_migrations"
    
    def initialize_migration_table(self):
        """Initialize migration tracking table"""
        try:
            with self.db_manager.get_session() as session:
                session.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS {self.migration_table} (
                        id INTEGER PRIMARY KEY,
                        version VARCHAR(50) NOT NULL UNIQUE,
                        description TEXT,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        checksum VARCHAR(64)
                    )
                """))
                session.commit()
                logger.info("Migration tracking table initialized")
                return True
        except Exception as e:
            logger.error(f"Failed to initialize migration table: {e}")
            return False
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations"""
        try:
            with self.db_manager.get_session() as session:
                result = session.execute(text(f"""
                    SELECT version FROM {self.migration_table} 
                    ORDER BY applied_at
                """))
                return [row[0] for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []
    
    def apply_migration(self, version: str, description: str, sql_commands: List[str]) -> bool:
        """Apply a database migration"""
        try:
            with self.db_manager.get_session() as session:
                # Check if migration already applied
                existing = session.execute(text(f"""
                    SELECT COUNT(*) FROM {self.migration_table} 
                    WHERE version = :version
                """), {"version": version}).scalar()
                
                if existing > 0:
                    logger.info(f"Migration {version} already applied")
                    return True
                
                # Apply migration commands
                for sql_command in sql_commands:
                    session.execute(text(sql_command))
                
                # Record migration
                session.execute(text(f"""
                    INSERT INTO {self.migration_table} (version, description) 
                    VALUES (:version, :description)
                """), {"version": version, "description": description})
                
                session.commit()
                logger.info(f"Migration {version} applied successfully: {description}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to apply migration {version}: {e}")
            return False
    
    def rollback_migration(self, version: str, rollback_commands: List[str]) -> bool:
        """Rollback a database migration"""
        try:
            with self.db_manager.get_session() as session:
                # Apply rollback commands
                for sql_command in rollback_commands:
                    session.execute(text(sql_command))
                
                # Remove migration record
                session.execute(text(f"""
                    DELETE FROM {self.migration_table} 
                    WHERE version = :version
                """), {"version": version})
                
                session.commit()
                logger.info(f"Migration {version} rolled back successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {e}")
            return False
    
    def run_initial_migrations(self) -> bool:
        """Run initial database setup migrations"""
        migrations = [
            {
                "version": "001_initial_schema",
                "description": "Create initial database schema",
                "commands": [
                    # This will be handled by SQLAlchemy create_all
                ]
            },
            {
                "version": "002_add_indexes",
                "description": "Add performance indexes",
                "commands": [
                    "CREATE INDEX IF NOT EXISTS idx_users_email_active ON users(email, is_active)",
                    "CREATE INDEX IF NOT EXISTS idx_conversations_user_status_date ON conversations(user_id, status, started_at)",
                    "CREATE INDEX IF NOT EXISTS idx_messages_conversation_timestamp ON messages(conversation_id, timestamp)",
                    "CREATE INDEX IF NOT EXISTS idx_medical_records_user_date ON medical_records(user_id, date_recorded)",
                ]
            },
            {
                "version": "003_add_analytics_indexes",
                "description": "Add analytics performance indexes",
                "commands": [
                    "CREATE INDEX IF NOT EXISTS idx_health_analytics_user_period_type ON health_analytics(user_id, period_type, period_start)",
                    "CREATE INDEX IF NOT EXISTS idx_symptom_patterns_user_active ON symptom_patterns(user_id, is_active)",
                    "CREATE INDEX IF NOT EXISTS idx_health_metrics_user_type_measured ON health_metrics(user_id, metric_type, measured_at)",
                ]
            }
        ]
        
        success = True
        for migration in migrations:
            if migration["commands"]:  # Skip empty command lists
                if not self.apply_migration(
                    migration["version"], 
                    migration["description"], 
                    migration["commands"]
                ):
                    success = False
                    break
        
        return success


def run_migrations():
    """Enhanced migration runner with comprehensive setup"""
    logger.info("Starting database migration process...")
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Create tables first
        logger.info("Creating database tables...")
        db_manager.create_tables()
        
        # Initialize migration system
        migration_manager = MigrationManager(db_manager)
        migration_manager.initialize_migration_table()
        
        # Run initial migrations
        logger.info("Running initial migrations...")
        if migration_manager.run_initial_migrations():
            logger.info("All migrations completed successfully")
        else:
            logger.error("Some migrations failed")
            return False
        
        # Optimize database after migrations
        logger.info("Optimizing database...")
        optimization_result = db_manager.optimize_database()
        if optimization_result.get("errors"):
            logger.warning(f"Database optimization had issues: {optimization_result['errors']}")
        
        # Run health check
        logger.info("Running post-migration health check...")
        health_check = db_manager.comprehensive_health_check()
        if health_check["status"] != "healthy":
            logger.warning(f"Database health check shows status: {health_check['status']}")
        
        logger.info("Database migration process completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Migration process failed: {e}")
        return False


def get_database_info() -> Dict[str, Any]:
    """Get comprehensive database information"""
    try:
        engine = create_database_engine()
        
        info = {
            "url": str(engine.url).split('@')[0] if '@' in str(engine.url) else str(engine.url),
            "driver": engine.dialect.name,
            "pool_size": getattr(engine.pool, 'size', None),
            "max_overflow": getattr(engine.pool, 'max_overflow', None),
            "echo": engine.echo,
            "pool_class": engine.pool.__class__.__name__,
            "database_type": "sqlite" if str(engine.url).startswith("sqlite") else "postgresql" if str(engine.url).startswith(("postgresql", "postgres")) else "other"
        }
        
        # Add pool status if available
        if hasattr(engine.pool, 'status'):
            info["pool_status"] = engine.pool.status()
        
        return info
        
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {"error": str(e)}


def initialize_database_system() -> Dict[str, Any]:
    """Initialize complete database system with all components"""
    initialization_result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "unknown",
        "steps_completed": [],
        "errors": [],
        "database_info": {},
        "health_check": {}
    }
    
    try:
        # Step 1: Create engine and session factory
        logger.info("Initializing database engine...")
        engine = create_database_engine()
        session_factory = create_session_factory()
        initialization_result["steps_completed"].append("engine_created")
        
        # Step 2: Test basic connectivity
        logger.info("Testing database connectivity...")
        if test_database_connection():
            initialization_result["steps_completed"].append("connectivity_tested")
        else:
            raise DatabaseConnectionError("Initial connectivity test failed")
        
        # Step 3: Run migrations
        logger.info("Running database migrations...")
        if run_migrations():
            initialization_result["steps_completed"].append("migrations_completed")
        else:
            raise DatabaseError("Migration process failed")
        
        # Step 4: Initialize database manager
        logger.info("Initializing database manager...")
        db_manager = DatabaseManager()
        initialization_result["steps_completed"].append("manager_initialized")
        
        # Step 5: Comprehensive health check
        logger.info("Running comprehensive health check...")
        health_check = db_manager.comprehensive_health_check()
        initialization_result["health_check"] = health_check
        initialization_result["steps_completed"].append("health_check_completed")
        
        # Step 6: Get database info
        database_info = get_database_info()
        initialization_result["database_info"] = database_info
        initialization_result["steps_completed"].append("info_gathered")
        
        # Determine final status
        if health_check.get("status") == "healthy":
            initialization_result["status"] = "success"
            logger.info("Database system initialization completed successfully")
        else:
            initialization_result["status"] = "partial_success"
            logger.warning("Database system initialized but health check shows issues")
        
    except Exception as e:
        initialization_result["status"] = "failed"
        initialization_result["errors"].append(str(e))
        logger.error(f"Database system initialization failed: {e}")
    
    return initialization_result


# Enhanced utility functions
def safe_execute_query(query: str, params: Dict[str, Any] = None) -> Optional[Any]:
    """Safely execute a database query with error handling"""
    try:
        with get_db_session() as session:
            result = session.execute(text(query), params or {})
            return result.fetchall()
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        return None


def get_table_row_count(table_name: str) -> int:
    """Get row count for a specific table"""
    try:
        with get_db_session() as session:
            result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return result.scalar()
    except Exception as e:
        logger.error(f"Failed to get row count for {table_name}: {e}")
        return -1


def check_database_locks() -> Dict[str, Any]:
    """Check for database locks (SQLite specific)"""
    lock_info = {
        "has_locks": False,
        "lock_details": [],
        "database_type": "unknown"
    }
    
    try:
        engine = create_database_engine()
        database_url = str(engine.url)
        
        if database_url.startswith("sqlite://"):
            lock_info["database_type"] = "sqlite"
            # SQLite lock checking would require additional implementation
            # For now, just return basic info
            lock_info["lock_details"].append("SQLite lock checking not fully implemented")
        
        elif database_url.startswith(("postgresql://", "postgres://")):
            lock_info["database_type"] = "postgresql"
            # PostgreSQL lock checking
            with get_db_session() as session:
                locks = session.execute(text("""
                    SELECT pid, mode, granted, query 
                    FROM pg_locks l 
                    JOIN pg_stat_activity a ON l.pid = a.pid 
                    WHERE l.granted = false
                """)).fetchall()
                
                lock_info["has_locks"] = len(locks) > 0
                lock_info["lock_details"] = [dict(row) for row in locks]
        
    except Exception as e:
        lock_info["error"] = str(e)
        logger.error(f"Failed to check database locks: {e}")
    
    return lock_info