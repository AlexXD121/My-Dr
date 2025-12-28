#!/usr/bin/env python3
"""
Migration script to set up PostgreSQL database for My Dr AI Medical Assistant
"""

import os
import sys
import logging
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup environment for production database"""
    # Load production environment
    from dotenv import load_dotenv
    load_dotenv('.env.production')
    
    # Verify DATABASE_URL is set
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL not found in environment")
        return False
    
    logger.info(f"✅ Using database: {database_url.split('@')[0]}@***")
    return True

def test_database_connection():
    """Test database connection"""
    try:
        from database import test_database_connection
        if test_database_connection():
            logger.info("✅ Database connection successful")
            return True
        else:
            logger.error("❌ Database connection failed")
            return False
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        return False

def create_database_tables():
    """Create all database tables"""
    try:
        from database import init_database
        if init_database():
            logger.info("✅ Database tables created successfully")
            return True
        else:
            logger.error("❌ Failed to create database tables")
            return False
    except Exception as e:
        logger.error(f"❌ Table creation error: {e}")
        return False

def run_migrations():
    """Run database migrations"""
    try:
        from database import db_manager, MigrationManager
        
        migration_manager = MigrationManager(db_manager)
        
        # Initialize migration table
        if not migration_manager.initialize_migration_table():
            logger.error("❌ Failed to initialize migration table")
            return False
        
        # Run initial migrations
        if not migration_manager.run_initial_migrations():
            logger.error("❌ Failed to run initial migrations")
            return False
        
        logger.info("✅ Database migrations completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        return False

def verify_database_setup():
    """Verify database setup is complete"""
    try:
        from database import db_manager
        
        # Run health check
        health_data = db_manager.comprehensive_health_check()
        
        if health_data["status"] == "healthy":
            logger.info("✅ Database health check passed")
            
            # Show statistics
            stats = db_manager.get_database_statistics()
            logger.info("📊 Database Statistics:")
            for table, count in stats.get("table_counts", {}).items():
                logger.info(f"   {table}: {count} records")
            
            return True
        else:
            logger.error(f"❌ Database health check failed: {health_data['status']}")
            for error in health_data.get("errors", []):
                logger.error(f"   Error: {error}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database verification error: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("🚀 Starting PostgreSQL migration for My Dr AI Medical Assistant")
    
    # Step 1: Setup environment
    if not setup_environment():
        logger.error("❌ Migration failed: Environment setup failed")
        return False
    
    # Step 2: Test database connection
    if not test_database_connection():
        logger.error("❌ Migration failed: Database connection failed")
        logger.info("💡 Make sure PostgreSQL is running and credentials are correct")
        logger.info("💡 Run: python setup_postgresql.py")
        return False
    
    # Step 3: Create database tables
    if not create_database_tables():
        logger.error("❌ Migration failed: Table creation failed")
        return False
    
    # Step 4: Run migrations
    if not run_migrations():
        logger.error("❌ Migration failed: Migration execution failed")
        return False
    
    # Step 5: Verify setup
    if not verify_database_setup():
        logger.error("❌ Migration failed: Database verification failed")
        return False
    
    logger.info("🎉 PostgreSQL migration completed successfully!")
    logger.info("📋 Next steps:")
    logger.info("   1. Test the backend: cd backend && python main.py")
    logger.info("   2. Check database health: python -c 'from backend.database import db_manager; print(db_manager.comprehensive_health_check())'")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)