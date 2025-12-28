"""
Startup script for Sukh Mental Health API
Validates configuration and initializes services
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_environment():
    """Validate environment configuration on startup"""
    try:
        from config import Settings
        
        logger.info("🔍 Validating configuration...")
        
        # Basic validation - try to load settings
        settings = Settings()
        
        # Check for AI providers (local AI or API keys)
        providers = []
        if settings.use_local_ai:
            providers.append("Local AI (Jan AI)")
        if settings.perplexity_api_key:
            providers.append("Perplexity AI")
        if settings.huggingface_api_key:
            providers.append("Hugging Face")
        
        if not providers:
            logger.error("❌ No AI providers configured")
            return False
        
        logger.info(f"🤖 AI providers available: {', '.join(providers)}")
        logger.info("✅ Configuration validation passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration validation error: {e}")
        return False


def initialize_logging():
    """Initialize application logging"""
    try:
        # Set log level to INFO
        logging.getLogger().setLevel(logging.INFO)
        
        # Configure basic console logging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(console_handler)
        
        logger.info("📋 Logging initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize logging: {e}")
        return False


def initialize_database():
    """Initialize database connection and run migrations"""
    try:
        from config import settings
        from migrations import run_database_setup
        from database import test_database_connection
        
        if not settings.database_url:
            logger.info("📊 No database configured, using SQLite in-memory storage")
            # Still run setup for in-memory database
            if not run_database_setup():
                logger.error("❌ In-memory database setup failed")
                return False
            logger.info("📊 In-memory database initialized successfully")
            return True
        
        # Test database connection
        logger.info("📊 Testing database connection...")
        if not test_database_connection():
            logger.error("❌ Database connection test failed")
            return False
        
        # Run database setup and migrations
        logger.info("📊 Running database setup and migrations...")
        if not run_database_setup():
            logger.error("❌ Database setup failed")
            return False
        
        logger.info(f"📊 Database initialized: {settings.database_url.split('@')[0] if '@' in settings.database_url else 'SQLite'}@***")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False


def initialize_redis():
    """Skip Redis initialization - not needed for demo"""
    logger.info("🔄 Skipping Redis initialization (not needed)")
    return True


def initialize_ai_services():
    """Initialize AI service connections"""
    try:
        from config import settings
        
        providers = []
        
        if settings.use_local_ai:
            providers.append("Local AI (Jan AI)")
        
        if settings.perplexity_api_key:
            providers.append("Perplexity AI")
        
        if settings.huggingface_api_key:
            providers.append("Hugging Face")
        
        if not providers:
            logger.error("❌ No AI providers configured")
            return False
        
        logger.info(f"🤖 AI providers initialized: {', '.join(providers)}")
        return True
        
    except Exception as e:
        logger.error(f"❌ AI services initialization failed: {e}")
        return False


def initialize_firebase():
    """Skip Firebase initialization - no auth required"""
    logger.info("🔥 Skipping Firebase initialization (no auth)")
    return True


def startup_application():
    """Complete application startup sequence"""
    logger.info("🚀 Starting Sukh Mental Health API...")
    
    # Step 1: Validate configuration
    if not validate_environment():
        logger.error("❌ Startup failed: Configuration validation failed")
        return False
    
    # Step 2: Initialize logging
    if not initialize_logging():
        logger.error("❌ Startup failed: Logging initialization failed")
        return False
    
    # Step 3: Initialize database
    if not initialize_database():
        logger.error("❌ Startup failed: Database initialization failed")
        return False
    
    # Step 4: Initialize Redis
    if not initialize_redis():
        logger.warning("⚠️  Redis initialization failed, continuing without caching")
    
    # Step 5: Initialize AI services
    if not initialize_ai_services():
        logger.error("❌ Startup failed: AI services initialization failed")
        return False
    
    # Step 6: Initialize Firebase
    if not initialize_firebase():
        logger.error("❌ Startup failed: Firebase initialization failed")
        return False
    
    logger.info("✅ Application startup completed successfully")
    return True


if __name__ == "__main__":
    """Run startup validation independently"""
    if not startup_application():
        sys.exit(1)
    
    print("✅ Startup validation passed - ready to run the application")