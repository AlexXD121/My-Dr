#!/usr/bin/env python3
"""
PostgreSQL Production Database Setup Script
Sets up PostgreSQL database for My Dr AI Medical Assistant
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration from .env.production
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "mydoc_prod"
DB_USER = "postgres"
DB_PASSWORD = "Dhaval@191004"

def check_postgresql_installed():
    """Check if PostgreSQL is installed and running"""
    try:
        # Try to connect to default postgres database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database="postgres",
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.close()
        logger.info("✅ PostgreSQL is installed and running")
        return True
    except psycopg2.OperationalError as e:
        if "password authentication failed" in str(e):
            logger.error(f"❌ Password authentication failed for user '{DB_USER}'")
            logger.error("💡 Try one of these solutions:")
            logger.error("   1. Reset postgres password: ALTER USER postgres PASSWORD 'Dhaval@191004';")
            logger.error("   2. Use Windows Authentication (if available)")
            logger.error("   3. Create a new user with the correct password")
            logger.error("   4. Update the password in .env.production")
        else:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            logger.error("Please ensure PostgreSQL is installed and running")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def create_database():
    """Create the production database if it doesn't exist"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database="postgres",
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if exists:
            logger.info(f"✅ Database '{DB_NAME}' already exists")
        else:
            # Create database
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            logger.info(f"✅ Database '{DB_NAME}' created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create database: {e}")
        return False

def test_database_connection():
    """Test connection to the production database"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        logger.info(f"✅ Connected to PostgreSQL: {version}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

def install_required_extensions():
    """Install required PostgreSQL extensions"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Install UUID extension for better ID generation
        cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
        logger.info("✅ UUID extension installed")
        
        # Install pg_trgm for better text search
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        logger.info("✅ pg_trgm extension installed")
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to install extensions: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Starting PostgreSQL setup for My Dr AI Medical Assistant")
    
    # Step 1: Check PostgreSQL installation
    if not check_postgresql_installed():
        logger.error("❌ Setup failed: PostgreSQL not available")
        logger.info("📋 To install PostgreSQL:")
        logger.info("   Windows: Download from https://www.postgresql.org/download/windows/")
        logger.info("   macOS: brew install postgresql")
        logger.info("   Ubuntu: sudo apt-get install postgresql postgresql-contrib")
        return False
    
    # Step 2: Create database
    if not create_database():
        logger.error("❌ Setup failed: Could not create database")
        return False
    
    # Step 3: Test connection
    if not test_database_connection():
        logger.error("❌ Setup failed: Could not connect to database")
        return False
    
    # Step 4: Install extensions
    if not install_required_extensions():
        logger.error("❌ Setup failed: Could not install extensions")
        return False
    
    logger.info("🎉 PostgreSQL setup completed successfully!")
    logger.info(f"📊 Database: {DB_NAME}")
    logger.info(f"🔗 Connection: postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)