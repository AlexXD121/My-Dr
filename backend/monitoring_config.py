"""
Monitoring System Configuration for My Dr AI Medical Assistant
Centralized configuration for logging, monitoring, and alerting
"""
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoggingConfig:
    """Logging system configuration"""
    log_level: str = "INFO"
    log_directory: str = "logs"
    max_file_size_mb: int = 100
    backup_count: int = 10
    enable_console: bool = True
    enable_file: bool = True
    enable_structured_logging: bool = True
    enable_privacy_protection: bool = True
    log_retention_days: int = 30


@dataclass
class MonitoringConfig:
    """Performance monitoring configuration"""
    enabled: bool = True
    collection_interval_seconds: int = 30
    metrics_retention_count: int = 1000
    enable_system_metrics: bool = True
    enable_database_metrics: bool = True
    enable_application_metrics: bool = True
    health_check_interval_seconds: int = 300


@dataclass
class AlertConfig:
    """Alert system configuration"""
    enabled: bool = True
    default_cooldown_minutes: int = 15
    enable_email_alerts: bool = True
    enable_webhook_alerts: bool = False
    enable_slack_alerts: bool = False
    enable_escalation: bool = True
    escalation_time_minutes: int = 30


@dataclass
class NotificationConfig:
    """Notification system configuration"""
    # Email settings
    smtp_server: str = "localhost"
    smtp_port: int = 587
    smtp_use_tls: bool = True
    smtp_username: str = ""
    smtp_password: str = ""
    email_from: str = "alerts@mydoc.ai"
    email_to: List[str] = None
    
    # Webhook settings
    webhook_url: str = ""
    webhook_timeout_seconds: int = 30
    webhook_headers: Dict[str, str] = None
    
    # Slack settings
    slack_webhook_url: str = ""
    slack_channel: str = "#alerts"
    slack_username: str = "MyDoc Alerts"
    slack_icon_emoji: str = ":warning:"
    
    def __post_init__(self):
        if self.email_to is None:
            self.email_to = ["admin@mydoc.ai"]
        if self.webhook_headers is None:
            self.webhook_headers = {}


class MonitoringSystemConfig:
    """Main monitoring system configuration"""
    
    def __init__(self):
        self.logging = self._load_logging_config()
        self.monitoring = self._load_monitoring_config()
        self.alerts = self._load_alert_config()
        self.notifications = self._load_notification_config()
    
    def _load_logging_config(self) -> LoggingConfig:
        """Load logging configuration from environment"""
        return LoggingConfig(
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            log_directory=os.getenv("LOG_DIRECTORY", "logs"),
            max_file_size_mb=int(os.getenv("LOG_MAX_FILE_SIZE_MB", "100")),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", "10")),
            enable_console=os.getenv("LOG_ENABLE_CONSOLE", "true").lower() == "true",
            enable_file=os.getenv("LOG_ENABLE_FILE", "true").lower() == "true",
            enable_structured_logging=os.getenv("LOG_ENABLE_STRUCTURED", "true").lower() == "true",
            enable_privacy_protection=os.getenv("LOG_ENABLE_PRIVACY_PROTECTION", "true").lower() == "true",
            log_retention_days=int(os.getenv("LOG_RETENTION_DAYS", "30"))
        )
    
    def _load_monitoring_config(self) -> MonitoringConfig:
        """Load monitoring configuration from environment"""
        return MonitoringConfig(
            enabled=os.getenv("MONITORING_ENABLED", "true").lower() == "true",
            collection_interval_seconds=int(os.getenv("MONITORING_INTERVAL_SECONDS", "30")),
            metrics_retention_count=int(os.getenv("MONITORING_METRICS_RETENTION", "1000")),
            enable_system_metrics=os.getenv("MONITORING_ENABLE_SYSTEM", "true").lower() == "true",
            enable_database_metrics=os.getenv("MONITORING_ENABLE_DATABASE", "true").lower() == "true",
            enable_application_metrics=os.getenv("MONITORING_ENABLE_APPLICATION", "true").lower() == "true",
            health_check_interval_seconds=int(os.getenv("MONITORING_HEALTH_CHECK_INTERVAL", "300"))
        )
    
    def _load_alert_config(self) -> AlertConfig:
        """Load alert configuration from environment"""
        return AlertConfig(
            enabled=os.getenv("ALERTS_ENABLED", "true").lower() == "true",
            default_cooldown_minutes=int(os.getenv("ALERTS_DEFAULT_COOLDOWN_MINUTES", "15")),
            enable_email_alerts=os.getenv("ALERTS_ENABLE_EMAIL", "true").lower() == "true",
            enable_webhook_alerts=os.getenv("ALERTS_ENABLE_WEBHOOK", "false").lower() == "true",
            enable_slack_alerts=os.getenv("ALERTS_ENABLE_SLACK", "false").lower() == "true",
            enable_escalation=os.getenv("ALERTS_ENABLE_ESCALATION", "true").lower() == "true",
            escalation_time_minutes=int(os.getenv("ALERTS_ESCALATION_TIME_MINUTES", "30"))
        )
    
    def _load_notification_config(self) -> NotificationConfig:
        """Load notification configuration from environment"""
        email_to_list = os.getenv("ALERT_EMAIL_TO", "admin@mydoc.ai").split(",")
        email_to_list = [email.strip() for email in email_to_list if email.strip()]
        
        webhook_headers = {}
        webhook_headers_str = os.getenv("WEBHOOK_HEADERS", "{}")
        try:
            import json
            webhook_headers = json.loads(webhook_headers_str)
        except json.JSONDecodeError:
            pass
        
        return NotificationConfig(
            smtp_server=os.getenv("SMTP_SERVER", "localhost"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
            smtp_username=os.getenv("SMTP_USERNAME", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            email_from=os.getenv("ALERT_EMAIL_FROM", "alerts@mydoc.ai"),
            email_to=email_to_list,
            webhook_url=os.getenv("WEBHOOK_URL", ""),
            webhook_timeout_seconds=int(os.getenv("WEBHOOK_TIMEOUT", "30")),
            webhook_headers=webhook_headers,
            slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL", ""),
            slack_channel=os.getenv("SLACK_CHANNEL", "#alerts"),
            slack_username=os.getenv("SLACK_USERNAME", "MyDoc Alerts"),
            slack_icon_emoji=os.getenv("SLACK_ICON", ":warning:")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "logging": {
                "log_level": self.logging.log_level,
                "log_directory": self.logging.log_directory,
                "max_file_size_mb": self.logging.max_file_size_mb,
                "backup_count": self.logging.backup_count,
                "enable_console": self.logging.enable_console,
                "enable_file": self.logging.enable_file,
                "enable_structured_logging": self.logging.enable_structured_logging,
                "enable_privacy_protection": self.logging.enable_privacy_protection,
                "log_retention_days": self.logging.log_retention_days
            },
            "monitoring": {
                "enabled": self.monitoring.enabled,
                "collection_interval_seconds": self.monitoring.collection_interval_seconds,
                "metrics_retention_count": self.monitoring.metrics_retention_count,
                "enable_system_metrics": self.monitoring.enable_system_metrics,
                "enable_database_metrics": self.monitoring.enable_database_metrics,
                "enable_application_metrics": self.monitoring.enable_application_metrics,
                "health_check_interval_seconds": self.monitoring.health_check_interval_seconds
            },
            "alerts": {
                "enabled": self.alerts.enabled,
                "default_cooldown_minutes": self.alerts.default_cooldown_minutes,
                "enable_email_alerts": self.alerts.enable_email_alerts,
                "enable_webhook_alerts": self.alerts.enable_webhook_alerts,
                "enable_slack_alerts": self.alerts.enable_slack_alerts,
                "enable_escalation": self.alerts.enable_escalation,
                "escalation_time_minutes": self.alerts.escalation_time_minutes
            },
            "notifications": {
                "smtp_server": self.notifications.smtp_server,
                "smtp_port": self.notifications.smtp_port,
                "smtp_use_tls": self.notifications.smtp_use_tls,
                "email_from": self.notifications.email_from,
                "email_to_count": len(self.notifications.email_to),
                "webhook_configured": bool(self.notifications.webhook_url),
                "slack_configured": bool(self.notifications.slack_webhook_url)
            }
        }
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate logging config
        if self.logging.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            issues.append(f"Invalid log level: {self.logging.log_level}")
        
        if self.logging.max_file_size_mb < 1:
            issues.append("Log file size must be at least 1MB")
        
        if self.logging.backup_count < 1:
            issues.append("Backup count must be at least 1")
        
        # Validate monitoring config
        if self.monitoring.collection_interval_seconds < 10:
            issues.append("Monitoring interval must be at least 10 seconds")
        
        if self.monitoring.metrics_retention_count < 100:
            issues.append("Metrics retention count must be at least 100")
        
        # Validate alert config
        if self.alerts.default_cooldown_minutes < 1:
            issues.append("Alert cooldown must be at least 1 minute")
        
        # Validate notification config
        if self.alerts.enable_email_alerts:
            if not self.notifications.smtp_username:
                issues.append("SMTP username required for email alerts")
            if not self.notifications.email_to:
                issues.append("Email recipients required for email alerts")
        
        if self.alerts.enable_webhook_alerts:
            if not self.notifications.webhook_url:
                issues.append("Webhook URL required for webhook alerts")
        
        if self.alerts.enable_slack_alerts:
            if not self.notifications.slack_webhook_url:
                issues.append("Slack webhook URL required for Slack alerts")
        
        return issues
    
    def create_env_template(self) -> str:
        """Create environment variable template"""
        return """
# Monitoring System Configuration

# Logging Configuration
LOG_LEVEL=INFO
LOG_DIRECTORY=logs
LOG_MAX_FILE_SIZE_MB=100
LOG_BACKUP_COUNT=10
LOG_ENABLE_CONSOLE=true
LOG_ENABLE_FILE=true
LOG_ENABLE_STRUCTURED=true
LOG_ENABLE_PRIVACY_PROTECTION=true
LOG_RETENTION_DAYS=30

# Performance Monitoring Configuration
MONITORING_ENABLED=true
MONITORING_INTERVAL_SECONDS=30
MONITORING_METRICS_RETENTION=1000
MONITORING_ENABLE_SYSTEM=true
MONITORING_ENABLE_DATABASE=true
MONITORING_ENABLE_APPLICATION=true
MONITORING_HEALTH_CHECK_INTERVAL=300

# Alert System Configuration
ALERTS_ENABLED=true
ALERTS_DEFAULT_COOLDOWN_MINUTES=15
ALERTS_ENABLE_EMAIL=true
ALERTS_ENABLE_WEBHOOK=false
ALERTS_ENABLE_SLACK=false
ALERTS_ENABLE_ESCALATION=true
ALERTS_ESCALATION_TIME_MINUTES=30

# Email Notification Configuration
SMTP_SERVER=localhost
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=
SMTP_PASSWORD=
ALERT_EMAIL_FROM=alerts@mydoc.ai
ALERT_EMAIL_TO=admin@mydoc.ai

# Webhook Notification Configuration
WEBHOOK_URL=
WEBHOOK_TIMEOUT=30
WEBHOOK_HEADERS={}

# Slack Notification Configuration
SLACK_WEBHOOK_URL=
SLACK_CHANNEL=#alerts
SLACK_USERNAME=MyDoc Alerts
SLACK_ICON=:warning:
        """.strip()


# Global configuration instance
monitoring_config = MonitoringSystemConfig()


def get_monitoring_config() -> MonitoringSystemConfig:
    """Get monitoring system configuration"""
    return monitoring_config


def validate_monitoring_config() -> List[str]:
    """Validate monitoring configuration"""
    return monitoring_config.validate()


def create_monitoring_env_template() -> str:
    """Create monitoring environment template"""
    return monitoring_config.create_env_template()


def get_monitoring_config_dict() -> Dict[str, Any]:
    """Get monitoring configuration as dictionary"""
    return monitoring_config.to_dict()