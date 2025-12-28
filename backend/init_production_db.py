"""
Production Database Initialization Script for My Dr AI Medical Assistant
Sets up PostgreSQL database with optimized configuration, indexes, and initial data
"""
import os
import sys
import logging
import asyncio
import time
from typing import Dict, Any, List
from datetime import datetime, timezone
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import text, create_engine
from production_database import production_db_manager, db_config, DatabaseConfig
from production_config import load_production_settings
from models import Base
from database import DatabaseManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionDatabaseInitializer:
    """Initialize production database with all required components"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.admin_connection_params = {
            'host': config.host,
            'port': config.port,
            'user': 'postgres',  # Default admin user
            'password': os.getenv('POSTGRES_ADMIN_PASSWORD', ''),
            'database': 'postgres'  # Default database
        }
    
    def create_database_and_user(self) -> bool:
        """Create database and user if they don't exist"""
        try:
            # Connect as admin user
            conn = psycopg2.connect(**self.admin_connection_params)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute(
                "SELECT 