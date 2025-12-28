#!/usr/bin/env python3
"""
Initialize Monitoring System for My Dr AI Medical Assistant
Sets up comprehensive logging, monitoring, and alerting system
"""
import os
import sys
import asyncio
import argparse
from pathlib import Path
from typing import List

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from monitoring_config import (
    get_monitoring_config, 
    validate_monitoring_config,
    create_monitoring_env_template
)
from logging_system import logging_system, get_medical_logger
from performance_monitoring import start_performance_monitoring, stop_performance_monitoring
from alert_system import start_alert_system, stop_alert_system
from database_monitoring import DatabaseMetricsCollector, DatabaseAlertManager


def setup_logging():
    """Setup basic logging for initialization"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def validate_environment() -> List[str]:
    """Validate environment and configuration"""
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8 or higher is required")
    
    # Validate monitoring configuration
    config_issues = validate_monitoring_config()
    issues.extend(config_issues)
    
    # Check required directories
    config = get_monitoring_config()
    log_dir = Path(config.logging.log_directory)
    
    try:
        log_dir.mkdir(exist_ok=True)
    except Exception as e:
        issues.append(f"Cannot create log directory {log_dir}: {e}")
    
    # Check write permissions
    if log_dir.exists() and not os.access(log_dir, os.W_OK):
        issues.append(f"No write permission for log directory {log_dir}")
    
    return issues


def initialize_logging_system():
    """Initialize the logging system"""
    print("📊 Initializing logging system...")
    
    config = get_monitoring_config()
    
    try:
        logging_system.configure_logging(
            log_level=config.logging.log_level,
            log_directory=config.logging.log_directory,
            max_file_size=config.logging.max_file_size_mb * 1024 * 1024,
            backup_count=config.logging.backup_count,
            enable_console=config.logging.enable_console,
            enable_file=config.logging.enable_file
        )
        
        logger = get_medical_logger("monitoring_init")
        logger.info("Logging system initialized successfully")
        print("✅ Logging system initialized")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize logging system: {e}")
        return False


def initialize_performance_monitoring():
    """Initialize performance monitoring"""
    print("📈 Initializing performance monitoring...")
    
    config = get_monitoring_config()
    
    if not config.monitoring.enabled:
        print("⚠️  Performance monitoring is disabled in configuration")
        return True
    
    try:
        start_performance_monitoring(config.monitoring.collection_interval_seconds)
        
        logger = get_medical_logger("monitoring_init")
        logger.info("Performance monitoring started",
                   interval_seconds=config.monitoring.collection_interval_seconds)
        print("✅ Performance monitoring initialized")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize performance monitoring: {e}")
        return False


def initialize_alert_system():
    """Initialize alert system"""
    print("🚨 Initializing alert system...")
    
    config = get_monitoring_config()
    
    if not config.alerts.enabled:
        print("⚠️  Alert system is disabled in configuration")
        return True
    
    try:
        start_alert_system()
        
        logger = get_medical_logger("monitoring_init")
        logger.info("Alert system started")
        print("✅ Alert system initialized")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize alert system: {e}")
        return False


def initialize_database_monitoring():
    """Initialize database monitoring"""
    print("🗄️  Initializing database monitoring...")
    
    config = get_monitoring_config()
    
    if not config.monitoring.enable_database_metrics:
        print("⚠️  Database monitoring is disabled in configuration")
        return True
    
    try:
        # Test database monitoring components
        db_collector = DatabaseMetricsCollector()
        db_alert_manager = DatabaseAlertManager()
        
        # Start database alert notification processor
        db_alert_manager.start_notification_processor()
        
        logger = get_medical_logger("monitoring_init")
        logger.info("Database monitoring initialized")
        print("✅ Database monitoring initialized")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize database monitoring: {e}")
        return False


def test_monitoring_system():
    """Test the monitoring system"""
    print("🧪 Testing monitoring system...")
    
    try:
        logger = get_medical_logger("monitoring_test")
        
        # Test logging
        logger.info("Testing logging system")
        logger.warning("Testing warning level")
        logger.error("Testing error level (this is a test)")
        
        # Test performance monitoring
        from performance_monitoring import get_system_health
        health_status = get_system_health()
        
        if health_status.get("status") == "unknown":
            print("⚠️  Performance monitoring test returned unknown status")
        else:
            print(f"✅ Performance monitoring test passed - Health: {health_status.get('health_score', 0)}")
        
        # Test alert system
        from alert_system import get_alert_system_status
        alert_status = get_alert_system_status()
        
        if alert_status.get("active"):
            print("✅ Alert system test passed")
        else:
            print("⚠️  Alert system is not active")
        
        logger.info("Monitoring system test completed successfully")
        print("✅ Monitoring system test completed")
        return True
        
    except Exception as e:
        print(f"❌ Monitoring system test failed: {e}")
        return False


def create_monitoring_status_report():
    """Create monitoring system status report"""
    print("\n📋 Monitoring System Status Report")
    print("=" * 50)
    
    config = get_monitoring_config()
    config_dict = config.to_dict()
    
    # Configuration status
    print("\n🔧 Configuration:")
    print(f"  Logging Level: {config_dict['logging']['log_level']}")
    print(f"  Log Directory: {config_dict['logging']['log_directory']}")
    print(f"  Monitoring Enabled: {config_dict['monitoring']['enabled']}")
    print(f"  Alerts Enabled: {config_dict['alerts']['enabled']}")
    print(f"  Email Alerts: {config_dict['alerts']['enable_email_alerts']}")
    print(f"  Webhook Alerts: {config_dict['alerts']['enable_webhook_alerts']}")
    print(f"  Slack Alerts: {config_dict['alerts']['enable_slack_alerts']}")
    
    # System status
    print("\n📊 System Status:")
    try:
        from performance_monitoring import get_system_health
        health_status = get_system_health()
        print(f"  Overall Health: {health_status.get('status', 'unknown')}")
        print(f"  Health Score: {health_status.get('health_score', 0)}/100")
        print(f"  Monitoring Active: {health_status.get('monitoring_active', False)}")
    except Exception as e:
        print(f"  Status Check Failed: {e}")
    
    # Alert system status
    print("\n🚨 Alert System:")
    try:
        from alert_system import get_alert_system_status
        alert_status = get_alert_system_status()
        print(f"  Active: {alert_status.get('active', False)}")
        print(f"  Total Rules: {alert_status.get('total_rules', 0)}")
        print(f"  Enabled Rules: {alert_status.get('enabled_rules', 0)}")
        print(f"  Notification Channels: {alert_status.get('notification_channels', 0)}")
    except Exception as e:
        print(f"  Alert Status Check Failed: {e}")
    
    # Log files
    print("\n📝 Log Files:")
    try:
        log_files = logging_system.get_log_files()
        for log_file in log_files:
            size_mb = log_file.stat().st_size / (1024 * 1024)
            print(f"  {log_file.name}: {size_mb:.2f} MB")
    except Exception as e:
        print(f"  Log Files Check Failed: {e}")
    
    print("\n" + "=" * 50)


async def main():
    """Main initialization function"""
    parser = argparse.ArgumentParser(description="Initialize MyDoc AI Monitoring System")
    parser.add_argument("--validate-only", action="store_true", 
                       help="Only validate configuration without initializing")
    parser.add_argument("--test-only", action="store_true",
                       help="Only run tests without full initialization")
    parser.add_argument("--create-env-template", action="store_true",
                       help="Create environment variable template")
    parser.add_argument("--status-report", action="store_true",
                       help="Generate status report")
    parser.add_argument("--stop", action="store_true",
                       help="Stop monitoring services")
    
    args = parser.parse_args()
    
    setup_logging()
    
    if args.create_env_template:
        print("Creating environment variable template...")
        template = create_monitoring_env_template()
        template_file = Path("monitoring.env.template")
        with open(template_file, 'w') as f:
            f.write(template)
        print(f"✅ Environment template created: {template_file}")
        return
    
    if args.stop:
        print("🛑 Stopping monitoring services...")
        try:
            stop_performance_monitoring()
            stop_alert_system()
            print("✅ Monitoring services stopped")
        except Exception as e:
            print(f"❌ Failed to stop monitoring services: {e}")
        return
    
    print("🚀 MyDoc AI Monitoring System Initialization")
    print("=" * 50)
    
    # Validate environment
    print("🔍 Validating environment...")
    issues = validate_environment()
    
    if issues:
        print("❌ Environment validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    
    print("✅ Environment validation passed")
    
    if args.validate_only:
        print("✅ Validation completed successfully")
        return
    
    # Initialize components
    success = True
    
    if not initialize_logging_system():
        success = False
    
    if not initialize_performance_monitoring():
        success = False
    
    if not initialize_alert_system():
        success = False
    
    if not initialize_database_monitoring():
        success = False
    
    if not success:
        print("\n❌ Monitoring system initialization failed")
        sys.exit(1)
    
    # Run tests
    if args.test_only or not args.validate_only:
        if not test_monitoring_system():
            print("\n⚠️  Some monitoring tests failed")
    
    # Generate status report
    if args.status_report or not args.test_only:
        create_monitoring_status_report()
    
    print("\n🎉 Monitoring system initialization completed successfully!")
    print("\nNext steps:")
    print("1. Review the status report above")
    print("2. Configure email/webhook/Slack notifications if needed")
    print("3. Access the health dashboard at /monitoring/dashboard-ui")
    print("4. Monitor logs in the configured log directory")


if __name__ == "__main__":
    asyncio.run(main())