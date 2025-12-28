"""
Database migrations and setup for MyDoc AI Medical Assistant
"""
import logging
from typing import List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import text, inspect
from database import get_db_session, create_database_engine
from models import Base, User, Conversation, Message, MedicalRecord, Consultation, HealthAnalytics, SymptomPattern

logger = logging.getLogger(__name__)


def run_database_setup() -> bool:
    """Run complete database setup including migrations"""
    try:
        logger.info("🔧 Starting database setup...")
        
        # Create database engine
        engine = create_database_engine()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Run any necessary data migrations
        if not run_data_migrations():
            logger.warning("⚠️  Some data migrations failed, but continuing...")
        
        logger.info("✅ Database setup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False


def run_data_migrations() -> bool:
    """Run data migrations"""
    try:
        with get_db_session() as db:
            # Check if we need to run any migrations
            inspector = inspect(db.bind)
            tables = inspector.get_table_names()
            
            if 'users' in tables:
                # Migration 1: Ensure all users have proper UUIDs
                result = db.execute(text("SELECT COUNT(*) FROM users WHERE id IS NULL OR id = ''"))
                null_count = result.scalar()
                
                if null_count > 0:
                    logger.info(f"Fixing {null_count} users with missing IDs...")
                    db.execute(text("""
                        UPDATE users 
                        SET id = gen_random_uuid()::text 
                        WHERE id IS NULL OR id = ''
                    """))
                    logger.info("✅ Fixed user IDs")
            
            # Migration 2: Add default preferences for existing users
            if 'users' in tables:
                result = db.execute(text("SELECT COUNT(*) FROM users WHERE preferences IS NULL"))
                null_prefs = result.scalar()
                
                if null_prefs > 0:
                    logger.info(f"Adding default preferences for {null_prefs} users...")
                    db.execute(text("""
                        UPDATE users 
                        SET preferences = '{}' 
                        WHERE preferences IS NULL
                    """))
                    logger.info("✅ Added default preferences")
        
        logger.info("✅ Data migrations completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Data migrations failed: {e}")
        return False


def create_indexes() -> bool:
    """Create additional database indexes for performance"""
    try:
        with get_db_session() as db:
            # Create performance indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_messages_conversation_timestamp ON messages(conversation_id, timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_conversations_user_status ON conversations(user_id, status)",
                "CREATE INDEX IF NOT EXISTS idx_medical_records_user_date ON medical_records(user_id, created_at)",
                "CREATE INDEX IF NOT EXISTS idx_users_firebase_uid ON users(firebase_uid)",
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"
            ]
            
            for index_sql in indexes:
                try:
                    db.execute(text(index_sql))
                    logger.info(f"✅ Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
                except Exception as e:
                    logger.warning(f"⚠️  Index creation failed (may already exist): {e}")
        
        logger.info("✅ Database indexes created")
        return True
        
    except Exception as e:
        logger.error(f"❌ Index creation failed: {e}")
        return False


def check_database_health() -> Dict[str, Any]:
    """Check database health and return status"""
    try:
        with get_db_session() as db:
            # Test basic connectivity
            db.execute(text("SELECT 1"))
            
            # Get table counts
            inspector = inspect(db.bind)
            tables = inspector.get_table_names()
            
            table_counts = {}
            for table in tables:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    table_counts[table] = result.scalar()
                except Exception as e:
                    table_counts[table] = f"Error: {e}"
            
            return {
                "status": "healthy",
                "tables": len(tables),
                "table_counts": table_counts,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


def reset_database_schema() -> bool:
    """Reset database schema (USE WITH CAUTION)"""
    try:
        logger.warning("🚨 RESETTING DATABASE SCHEMA - ALL DATA WILL BE LOST!")
        
        engine = create_database_engine()
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.warning("❌ All tables dropped")
        
        # Recreate all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables recreated")
        
        # Create indexes
        create_indexes()
        
        logger.info("✅ Database schema reset completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database schema reset failed: {e}")
        return False


if __name__ == "__main__":
    """Run migrations directly"""
    logging.basicConfig(level=logging.INFO)
    
    if run_database_setup():
        print("✅ Database setup completed successfully")
        
        # Create indexes
        if create_indexes():
            print("✅ Database indexes created successfully")
        
        # Check health
        health = check_database_health()
        print(f"📊 Database health: {health['status']}")
        print(f"📊 Tables: {health.get('tables', 0)}")
        
    else:
        print("❌ Database setup failed")
        exit(1)