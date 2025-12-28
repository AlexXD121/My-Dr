#!/usr/bin/env python3
"""
Production Database Setup Script for My Dr AI Medical Assistant
Comprehensive setup including PostgreSQL configuration, optimization, and monitoring
"""
import os
import sys
import logging
import asyncio
import argparse
from typing import Dict, Any
from datetime import datetime, timezone

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from production_database import (
    production_db_manager, 
    backup_manager, 
    db_config,
    initialize_production_database
)
from production_config import load_production_settings, create_production_env_template
from database_monitoring import database_monitor, start_database_monitoring
from init_production_db import ProductionDatabaseInitializer
from models import Base

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/mydoc/setup.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)


class ProductionDatabaseSetup:
    """Complete production database setup orchestrator"""
    
    def __init__(self):
        self.settings = None
        self.db_initializer = None
        self.setup_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "steps_completed": [],
            "errors": [],
            "warnings": []
        }
    
    def load_configuration(self) -> bool:
        """Load and validate production configuration"""
        try:
            logger.info("Loading production configuration...")
            self.settings = load_production_settings()
            self.db_initializer = ProductionDatabaseInitializer(db_config)
            
            logger.info(f"Configuration loaded for environment: {self.settings.environment}")
            logger.info(f"Database: {self.settings.db_host}:{self.settings.db_port}/{self.settings.db_name}")
            
            self.setup_results["steps_completed"].append("configuration_loaded")
            return True
            
        except Exception as e:
            error_msg = f"Failed to load production configuration: {e}"
            logger.error(error_msg)
            self.setup_results["errors"].append(error_msg)
            return False
    
    def create_database_and_user(self) -> bool:
        """Create database and user if they don't exist"""
        try:
            logger.info("Creating database and user...")
            
            if not self.db_initializer:
                raise Exception("Database initializer not available")
            
            success = self.db_initializer.create_database_and_user()
            if success:
                logger.info("Database and user created successfully")
                self.setup_results["steps_completed"].append("database_created")
                return True
            else:
                raise Exception("Database creation failed")
                
        except Exception as e:
            error_msg = f"Failed to create database and user: {e}"
            logger.error(error_msg)
            self.setup_results["errors"].append(error_msg)
            return False
    
    def initialize_schema(self) -> bool:
        """Initialize database schema"""
        try:
            logger.info("Initializing database schema...")
            
            # Create all tables
            engine = production_db_manager.create_sync_engine()
            Base.metadata.create_all(bind=engine)
            
            logger.info("Database schema initialized successfully")
            self.setup_results["steps_completed"].append("schema_initialized")
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize schema: {e}"
            logger.error(error_msg)
            self.setup_results["errors"].append(error_msg)
            return False
    
    def optimize_database(self) -> bool:
        """Apply database optimizations"""
        try:
            logger.info("Applying database optimizations...")
            
            # Test connection first
            success, error = production_db_manager.test_connection()
            if not success:
                raise Exception(f"Database connection failed: {error}")
            
            # Run optimization
            optimization_results = production_db_manager.optimize_database()
            
            if optimization_results.get("errors"):
                for error in optimization_results["errors"]:
                    self.setup_results["warnings"].append(f"Optimization warning: {error}")
            
            logger.info("Database optimizations applied")
            logger.info(f"Actions performed: {optimization_results.get('actions_performed', [])}")
            
            self.setup_results["steps_completed"].append("database_optimized")
            return True
            
        except Exception as e:
            error_msg = f"Failed to optimize database: {e}"
            logger.error(error_msg)
            self.setup_results["errors"].append(error_msg)
            return False
    
    def setup_connection_pooling(self) -> bool:
        """Setup and test connection pooling"""
        try:
            logger.info("Setting up connection pooling...")
            
            # Initialize session factories
            production_db_manager.create_session_factories()
            
            # Test connection pool
            with production_db_manager.get_session() as session:
                result = session.execute("SELECT 'Connection pool test'")
                test_result = result.scalar()
                logger.info(f"Connection pool test result: {test_result}")
            
            # Log pool configuration
            pool = production_db_manager.sync_engine.pool
            logger.info(f"Connection pool configured - Size: {pool.size()}, Max overflow: {pool.overflow()}")
            
            self.setup_results["steps_completed"].append("connection_pooling_setup")
            return True
            
        except Exception as e:
            error_msg = f"Failed to setup connection pooling: {e}"
            logger.error(error_msg)
            self.setup_results["errors"].append(error_msg)
            return False
    
    def setup_monitoring(self) -> bool:
        """Setup database monitoring"""
        try:
            logger.info("Setting up database monitoring...")
            
            # Start monitoring
            start_database_monitoring()
            
            # Wait a moment for initial metrics
            import time
            time.sleep(5)
            
            # Get initial health check
            health_data = production_db_manager.comprehensive_health_check()
            logger.info(f"Initial health check - Status: {health_data['status']}")
            logger.info(f"Health score: {health_data.get('performance_metrics', {}).get('total_check_time_ms', 'N/A')}ms")
            
            self.setup_results["steps_completed"].append("monitoring_setup")
            return True
            
        except Exception as e:
            error_msg = f"Failed to setup monitoring: {e}"
            logger.error(error_msg)
            self.setup_results["errors"].append(error_msg)
            return False
    
    def setup_backup_system(self) -> bool:
        """Setup automated backup system"""
        try:
            logger.info("Setting up backup system...")
            
            # Create backup directory
            backup_dir = backup_manager.backup_dir
            os.makedirs(backup_dir, exist_ok=True)
            logger.info(f"Backup directory created: {backup_dir}")
            
            # Create initial schema backup
            backup_result = backup_manager.create_backup("schema_only")
            
            if backup_result["status"] == "success":
                logger.info(f"Initial schema backup created: {backup_result['backup_file']}")
                logger.info(f"Backup size: {backup_result['size_bytes']} bytes")
            else:
                self.setup_results["warnings"].append(f"Initial backup failed: {backup_result.get('error')}")
            
            # Get backup schedule configuration
            schedule_config = backup_manager.schedule_automated_backups()
            logger.info("Automated backup schedule configuration:")
            for backup_type, config in schedule_config["cron_configuration"].items():
                logger.info(f"  {backup_type}: {config['schedule']}")
            
            self.setup_results["steps_completed"].append("backup_system_setup")
            return True
            
        except Exception as e:
            error_msg = f"Failed to setup backup system: {e}"
            logger.error(error_msg)
            self.setup_results["errors"].append(error_msg)
            return False
    
    def run_comprehensive_tests(self) -> bool:
        """Run comprehensive database tests"""
        try:
            logger.info("Running comprehensive database tests...")
            
            # Test synchronous connection
            success, error = production_db_manager.test_connection()
            if not success:
                raise Exception(f"Sync connection test failed: {error}")
            
            # Test asynchronous connection
            async def test_async():
                return await production_db_manager.test_async_connection()
            
            success, error = asyncio.run(test_async())
            if not success:
                raise Exception(f"Async connection test failed: {error}")
            
            # Get database statistics
            stats = production_db_manager.get_database_statistics()
            if "error" in stats:
                self.setup_results["warnings"].append(f"Statistics collection warning: {stats['error']}")
            else:
                logger.info(f"Database statistics collected - {len(stats.get('table_statistics', []))} tables")
            
            # Test monitoring
            monitoring_status = database_monitor.get_current_status()
            if monitoring_status.get("monitoring_active"):
                logger.info("Database monitoring is active")
            else:
                self.setup_results["warnings"].append("Database monitoring is not active")
            
            self.setup_results["steps_completed"].append("comprehensive_tests_passed")
            return True
            
        except Exception as e:
            error_msg = f"Comprehensive tests failed: {e}"
            logger.error(error_msg)
            self.setup_results["errors"].append(error_msg)
            return False
    
    def generate_setup_report(self) -> Dict[str, Any]:
        """Generate comprehensive setup report"""
        report = {
            "setup_timestamp": self.setup_results["timestamp"],
            "completion_timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": self.settings.environment.value if self.settings else "unknown",
            "database_config": {
                "host": db_config.host,
                "port": db_config.port,
                "database": db_config.database,
                "pool_size": db_config.pool_size,
                "max_overflow": db_config.max_overflow
            },
            "steps_completed": self.setup_results["steps_completed"],
            "total_steps": len(self.setup_results["steps_completed"]),
            "errors": self.setup_results["errors"],
            "warnings": self.setup_results["warnings"],
            "success": len(self.setup_results["errors"]) == 0
        }
        
        # Add health check if available
        try:
            health_data = production_db_manager.comprehensive_health_check()
            report["final_health_check"] = {
                "status": health_data["status"],
                "health_score": health_data.get("health_score", 0),
                "connection_pool": health_data.get("connection_pool", {}),
                "performance_metrics": health_data.get("performance_metrics", {})
            }
        except Exception as e:
            report["final_health_check"] = {"error": str(e)}
        
        return report
    
    def run_full_setup(self) -> bool:
        """Run complete production database setup"""
        logger.info("Starting production database setup...")
        logger.info("=" * 60)
        
        setup_steps = [
            ("Load Configuration", self.load_configuration),
            ("Create Database and User", self.create_database_and_user),
            ("Initialize Schema", self.initialize_schema),
            ("Setup Connection Pooling", self.setup_connection_pooling),
            ("Optimize Database", self.optimize_database),
            ("Setup Monitoring", self.setup_monitoring),
            ("Setup Backup System", self.setup_backup_system),
            ("Run Comprehensive Tests", self.run_comprehensive_tests)
        ]
        
        for step_name, step_function in setup_steps:
            logger.info(f"Executing: {step_name}")
            success = step_function()
            
            if success:
                logger.info(f"✓ {step_name} completed successfully")
            else:
                logger.error(f"✗ {step_name} failed")
                if step_name in ["Load Configuration", "Create Database and User"]:
                    logger.error("Critical step failed, aborting setup")
                    break
        
        # Generate final report
        report = self.generate_setup_report()
        
        logger.info("=" * 60)
        logger.info("PRODUCTION DATABASE SETUP COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Success: {report['success']}")
        logger.info(f"Steps completed: {report['total_steps']}")
        logger.info(f"Errors: {len(report['errors'])}")
        logger.info(f"Warnings: {len(report['warnings'])}")
        
        if report.get("final_health_check", {}).get("status"):
            logger.info(f"Final health status: {report['final_health_check']['status']}")
        
        # Save report to file
        import json
        report_file = f"/var/log/mydoc/setup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Setup report saved to: {report_file}")
        except Exception as e:
            logger.warning(f"Failed to save setup report: {e}")
        
        return report['success']


def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Production Database Setup for MyDoc AI")
    parser.add_argument("--create-env-template", action="store_true", 
                       help="Create production environment template file")
    parser.add_argument("--test-only", action="store_true",
                       help="Run tests only, skip setup")
    parser.add_argument("--skip-monitoring", action="store_true",
                       help="Skip monitoring setup")
    
    args = parser.parse_args()
    
    if args.create_env_template:
        logger.info("Creating production environment template...")
        create_production_env_template()
        return
    
    # Ensure log directory exists
    os.makedirs("/var/log/mydoc", exist_ok=True)
    
    setup = ProductionDatabaseSetup()
    
    if args.test_only:
        logger.info("Running database tests only...")
        success = setup.load_configuration() and setup.run_comprehensive_tests()
    else:
        success = setup.run_full_setup()
    
    if success:
        logger.info("Production database setup completed successfully!")
        sys.exit(0)
    else:
        logger.error("Production database setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()