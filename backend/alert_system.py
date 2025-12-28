"""
Automated Alert System for My Dr AI Medical Assistant
Comprehensive alerting for critical errors, performance issues, and system health
"""
import os
import json
import time
import asyncio
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from queue import Queue, Empty
from pathlib import Path

try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from logging_system import get_medical_logger, LogContext
from performance_monitoring import SystemMetrics, Alert


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    description: str
    condition: str  # Python expression to evaluate
    severity: str  # warning, critical, emergency
    cooldown_minutes: int = 15
    enabled: bool = True
    notification_channels: List[str] = None
    escalation_rules: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ["email", "log"]


@dataclass
class NotificationChannel:
    """Notification channel configuration"""
    name: str
    type: str  # email, webhook, sms, slack
    config: Dict[str, Any]
    enabled: bool = True


@dataclass
class EscalationRule:
    """Alert escalation rule"""
    alert_name: str
    escalation_time_minutes: int
    escalation_channels: List[str]
    escalation_message: str


class AlertEvaluator:
    """Evaluates alert conditions against metrics"""
    
    def __init__(self):
        self.logger = get_medical_logger("alert_evaluator")
        self.safe_globals = {
            '__builtins__': {},
            'abs': abs,
            'max': max,
            'min': min,
            'round': round,
            'len': len,
            'sum': sum,
            'any': any,
            'all': all,
        }
    
    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Safely evaluate alert condition"""
        try:
            # Create safe evaluation context
            eval_context = {**self.safe_globals, **context}
            
            # Evaluate condition
            result = eval(condition, eval_context)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate alert condition '{condition}': {e}")
            return False
    
    def prepare_context(self, metrics: SystemMetrics, additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare evaluation context from metrics"""
        context = {
            'cpu_percent': metrics.cpu_percent,
            'memory_percent': metrics.memory_percent,
            'memory_used_mb': metrics.memory_used_mb,
            'memory_available_mb': metrics.memory_available_mb,
            'disk_usage_percent': metrics.disk_usage_percent,
            'disk_free_gb': metrics.disk_free_gb,
            'active_connections': metrics.active_connections,
            'response_time_avg_ms': metrics.response_time_avg_ms,
            'error_rate_percent': metrics.error_rate_percent,
            'requests_per_minute': metrics.requests_per_minute,
        }
        
        if additional_context:
            context.update(additional_context)
        
        return context


class NotificationManager:
    """Manages different notification channels"""
    
    def __init__(self):
        self.logger = get_medical_logger("notification_manager")
        self.channels = {}
        self._load_notification_channels()
    
    def _load_notification_channels(self):
        """Load notification channel configurations"""
        # Email channel
        if os.getenv("SMTP_SERVER"):
            self.channels["email"] = NotificationChannel(
                name="email",
                type="email",
                config={
                    "smtp_server": os.getenv("SMTP_SERVER", "localhost"),
                    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                    "username": os.getenv("SMTP_USERNAME", ""),
                    "password": os.getenv("SMTP_PASSWORD", ""),
                    "from_address": os.getenv("ALERT_EMAIL_FROM", "alerts@mydoc.ai"),
                    "to_addresses": os.getenv("ALERT_EMAIL_TO", "admin@mydoc.ai").split(","),
                    "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true"
                },
                enabled=bool(os.getenv("SMTP_USERNAME"))
            )
        
        # Webhook channel
        if os.getenv("WEBHOOK_URL"):
            self.channels["webhook"] = NotificationChannel(
                name="webhook",
                type="webhook",
                config={
                    "url": os.getenv("WEBHOOK_URL"),
                    "headers": json.loads(os.getenv("WEBHOOK_HEADERS", "{}")),
                    "timeout": int(os.getenv("WEBHOOK_TIMEOUT", "30"))
                },
                enabled=True
            )
        
        # Slack channel
        if os.getenv("SLACK_WEBHOOK_URL"):
            self.channels["slack"] = NotificationChannel(
                name="slack",
                type="slack",
                config={
                    "webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
                    "channel": os.getenv("SLACK_CHANNEL", "#alerts"),
                    "username": os.getenv("SLACK_USERNAME", "MyDoc Alerts"),
                    "icon_emoji": os.getenv("SLACK_ICON", ":warning:")
                },
                enabled=True
            )
        
        # Log channel (always available)
        self.channels["log"] = NotificationChannel(
            name="log",
            type="log",
            config={},
            enabled=True
        )
    
    async def send_notification(self, alert: Alert, channels: List[str]):
        """Send notification through specified channels"""
        for channel_name in channels:
            if channel_name not in self.channels:
                self.logger.warning(f"Unknown notification channel: {channel_name}")
                continue
            
            channel = self.channels[channel_name]
            if not channel.enabled:
                continue
            
            try:
                if channel.type == "email":
                    await self._send_email_notification(alert, channel)
                elif channel.type == "webhook":
                    await self._send_webhook_notification(alert, channel)
                elif channel.type == "slack":
                    await self._send_slack_notification(alert, channel)
                elif channel.type == "log":
                    await self._send_log_notification(alert, channel)
                
            except Exception as e:
                self.logger.error(f"Failed to send notification via {channel_name}: {e}")
    
    async def _send_email_notification(self, alert: Alert, channel: NotificationChannel):
        """Send email notification"""
        if not EMAIL_AVAILABLE:
            self.logger.warning("Email functionality not available")
            return
            
        config = channel.config
        
        if not config.get("username") or not config.get("to_addresses"):
            self.logger.warning("Email configuration incomplete")
            return
        
        try:
            msg = MimeMultipart()
            msg['From'] = config["from_address"]
            msg['To'] = ", ".join(config["to_addresses"])
            msg['Subject'] = f"[{alert.severity.upper()}] MyDoc Alert - {alert.alert_type}"
            
            # Create email body
            body = self._create_email_body(alert)
            msg.attach(MimeText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            if config.get("use_tls", True):
                server.starttls()
            if config["username"]:
                server.login(config["username"], config["password"])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email alert sent for {alert.alert_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
    
    async def _send_webhook_notification(self, alert: Alert, channel: NotificationChannel):
        """Send webhook notification"""
        if not REQUESTS_AVAILABLE:
            self.logger.warning("Requests library not available for webhook notifications")
            return
            
        config = channel.config
        
        try:
            payload = {
                "alert": asdict(alert),
                "service": "MyDoc AI Medical Assistant",
                "environment": os.getenv("ENVIRONMENT", "production")
            }
            
            headers = {"Content-Type": "application/json"}
            headers.update(config.get("headers", {}))
            
            response = requests.post(
                config["url"],
                json=payload,
                headers=headers,
                timeout=config.get("timeout", 30)
            )
            response.raise_for_status()
            
            self.logger.info(f"Webhook alert sent for {alert.alert_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to send webhook notification: {e}")
    
    async def _send_slack_notification(self, alert: Alert, channel: NotificationChannel):
        """Send Slack notification"""
        if not REQUESTS_AVAILABLE:
            self.logger.warning("Requests library not available for Slack notifications")
            return
            
        config = channel.config
        
        try:
            # Create Slack message
            color = "danger" if alert.severity == "critical" else "warning"
            
            payload = {
                "channel": config.get("channel", "#alerts"),
                "username": config.get("username", "MyDoc Alerts"),
                "icon_emoji": config.get("icon_emoji", ":warning:"),
                "attachments": [
                    {
                        "color": color,
                        "title": f"{alert.severity.upper()} Alert: {alert.alert_type}",
                        "text": alert.message,
                        "fields": [
                            {
                                "title": "Metric",
                                "value": alert.metric_name,
                                "short": True
                            },
                            {
                                "title": "Current Value",
                                "value": f"{alert.current_value:.2f}",
                                "short": True
                            },
                            {
                                "title": "Threshold",
                                "value": f"{alert.threshold_value:.2f}",
                                "short": True
                            },
                            {
                                "title": "Time",
                                "value": alert.timestamp,
                                "short": True
                            }
                        ],
                        "footer": "MyDoc AI Medical Assistant",
                        "ts": int(datetime.fromisoformat(alert.timestamp.replace('Z', '+00:00')).timestamp())
                    }
                ]
            }
            
            response = requests.post(
                config["webhook_url"],
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            self.logger.info(f"Slack alert sent for {alert.alert_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {e}")
    
    async def _send_log_notification(self, alert: Alert, channel: NotificationChannel):
        """Send log notification"""
        self.logger.warning(f"ALERT: {alert.message}",
                          alert_type=alert.alert_type,
                          severity=alert.severity,
                          metric_name=alert.metric_name,
                          current_value=alert.current_value,
                          threshold_value=alert.threshold_value)
    
    def _create_email_body(self, alert: Alert) -> str:
        """Create HTML email body for alert"""
        severity_color = "#dc3545" if alert.severity == "critical" else "#ffc107"
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="background-color: {severity_color}; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">{alert.severity.upper()} Alert</h1>
                    <p style="margin: 5px 0 0 0; font-size: 16px;">{alert.alert_type}</p>
                </div>
                
                <div style="padding: 20px;">
                    <h2 style="color: #333; margin-top: 0;">Alert Details</h2>
                    
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold; width: 30%;">Message:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;">{alert.message}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Metric:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;">{alert.metric_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Current Value:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;">{alert.current_value:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Threshold:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;">{alert.threshold_value:.2f}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Time:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #eee;">{alert.timestamp}</td>
                        </tr>
                    </table>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #333;">Recommended Actions</h3>
                        <ul style="margin: 10px 0;">
                            <li>Check system resources and performance</li>
                            <li>Review recent application logs for errors</li>
                            <li>Monitor the situation for escalation</li>
                            <li>Contact system administrator if issue persists</li>
                        </ul>
                    </div>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 0 0 8px 8px; text-align: center; color: #666;">
                    <p style="margin: 0; font-size: 14px;">MyDoc AI Medical Assistant Monitoring System</p>
                    <p style="margin: 5px 0 0 0; font-size: 12px;">This is an automated alert. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """


class EscalationManager:
    """Manages alert escalation rules"""
    
    def __init__(self, notification_manager: NotificationManager):
        self.logger = get_medical_logger("escalation_manager")
        self.notification_manager = notification_manager
        self.escalation_rules = []
        self.pending_escalations = {}
        self.escalation_thread = None
        self.stop_event = threading.Event()
    
    def add_escalation_rule(self, rule: EscalationRule):
        """Add escalation rule"""
        self.escalation_rules.append(rule)
        self.logger.info(f"Added escalation rule for {rule.alert_name}")
    
    def start_escalation_processor(self):
        """Start escalation processor thread"""
        if self.escalation_thread and self.escalation_thread.is_alive():
            return
        
        self.stop_event.clear()
        self.escalation_thread = threading.Thread(target=self._escalation_loop)
        self.escalation_thread.daemon = True
        self.escalation_thread.start()
        self.logger.info("Escalation processor started")
    
    def stop_escalation_processor(self):
        """Stop escalation processor thread"""
        self.stop_event.set()
        if self.escalation_thread:
            self.escalation_thread.join(timeout=5)
        self.logger.info("Escalation processor stopped")
    
    def register_alert_for_escalation(self, alert: Alert):
        """Register alert for potential escalation"""
        for rule in self.escalation_rules:
            if rule.alert_name == alert.alert_type or rule.alert_name == alert.metric_name:
                escalation_time = datetime.now(timezone.utc) + timedelta(minutes=rule.escalation_time_minutes)
                
                escalation_key = f"{alert.alert_type}_{alert.metric_name}_{alert.timestamp}"
                self.pending_escalations[escalation_key] = {
                    "alert": alert,
                    "rule": rule,
                    "escalation_time": escalation_time,
                    "escalated": False
                }
                
                self.logger.info(f"Alert registered for escalation: {alert.alert_type}")
    
    def cancel_escalation(self, alert: Alert):
        """Cancel escalation for resolved alert"""
        keys_to_remove = []
        for key, escalation in self.pending_escalations.items():
            if (escalation["alert"].alert_type == alert.alert_type and 
                escalation["alert"].metric_name == alert.metric_name):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.pending_escalations[key]
            self.logger.info(f"Escalation cancelled for {alert.alert_type}")
    
    def _escalation_loop(self):
        """Main escalation processing loop"""
        while not self.stop_event.is_set():
            try:
                current_time = datetime.now(timezone.utc)
                
                for key, escalation in list(self.pending_escalations.items()):
                    if escalation["escalated"]:
                        continue
                    
                    if current_time >= escalation["escalation_time"]:
                        # Escalate alert
                        asyncio.run(self._escalate_alert(escalation))
                        escalation["escalated"] = True
                
                # Clean up old escalations
                cutoff_time = current_time - timedelta(hours=24)
                keys_to_remove = [
                    key for key, escalation in self.pending_escalations.items()
                    if datetime.fromisoformat(escalation["alert"].timestamp.replace('Z', '+00:00')) < cutoff_time
                ]
                
                for key in keys_to_remove:
                    del self.pending_escalations[key]
                
            except Exception as e:
                self.logger.error(f"Error in escalation loop: {e}")
            
            # Wait before next check
            self.stop_event.wait(60)  # Check every minute
    
    async def _escalate_alert(self, escalation: Dict[str, Any]):
        """Escalate an alert"""
        alert = escalation["alert"]
        rule = escalation["rule"]
        
        # Create escalated alert
        escalated_alert = Alert(
            timestamp=datetime.now(timezone.utc).isoformat(),
            alert_type=f"ESCALATED_{alert.alert_type}",
            severity="critical",
            metric_name=alert.metric_name,
            current_value=alert.current_value,
            threshold_value=alert.threshold_value,
            message=f"ESCALATED: {rule.escalation_message} - Original: {alert.message}",
            context=alert.context
        )
        
        # Send escalated notification
        await self.notification_manager.send_notification(escalated_alert, rule.escalation_channels)
        
        self.logger.critical(f"Alert escalated: {alert.alert_type}")


class AutomatedAlertSystem:
    """Main automated alert system"""
    
    def __init__(self):
        self.logger = get_medical_logger("alert_system")
        self.alert_evaluator = AlertEvaluator()
        self.notification_manager = NotificationManager()
        self.escalation_manager = EscalationManager(self.notification_manager)
        self.alert_rules = []
        self.alert_history = deque(maxlen=1000)
        self.last_alerts = {}
        self.is_active = False
        
        # Load default alert rules
        self._load_default_alert_rules()
    
    def _load_default_alert_rules(self):
        """Load default alert rules"""
        self.alert_rules = [
            AlertRule(
                name="High CPU Usage",
                description="CPU usage is critically high",
                condition="cpu_percent > 90",
                severity="critical",
                cooldown_minutes=10,
                notification_channels=["email", "log", "slack"]
            ),
            AlertRule(
                name="High Memory Usage",
                description="Memory usage is critically high",
                condition="memory_percent > 95",
                severity="critical",
                cooldown_minutes=15,
                notification_channels=["email", "log", "slack"]
            ),
            AlertRule(
                name="Low Disk Space",
                description="Disk space is running low",
                condition="disk_free_gb < 1",
                severity="critical",
                cooldown_minutes=30,
                notification_channels=["email", "log"]
            ),
            AlertRule(
                name="High Error Rate",
                description="Application error rate is high",
                condition="error_rate_percent > 10",
                severity="critical",
                cooldown_minutes=5,
                notification_channels=["email", "log", "slack"]
            ),
            AlertRule(
                name="Slow Response Time",
                description="Average response time is too high",
                condition="response_time_avg_ms > 2000",
                severity="warning",
                cooldown_minutes=10,
                notification_channels=["log", "slack"]
            ),
            AlertRule(
                name="Database Connection Issues",
                description="Database connection problems detected",
                condition="active_connections < 1",
                severity="critical",
                cooldown_minutes=5,
                notification_channels=["email", "log", "slack"]
            )
        ]
        
        # Add escalation rules
        self.escalation_manager.add_escalation_rule(
            EscalationRule(
                alert_name="High CPU Usage",
                escalation_time_minutes=30,
                escalation_channels=["email"],
                escalation_message="CPU usage remains critically high for 30 minutes"
            )
        )
        
        self.escalation_manager.add_escalation_rule(
            EscalationRule(
                alert_name="High Error Rate",
                escalation_time_minutes=15,
                escalation_channels=["email", "slack"],
                escalation_message="Error rate remains high for 15 minutes"
            )
        )
    
    def start(self):
        """Start the alert system"""
        if self.is_active:
            return
        
        self.escalation_manager.start_escalation_processor()
        self.is_active = True
        self.logger.info("Automated alert system started")
    
    def stop(self):
        """Stop the alert system"""
        if not self.is_active:
            return
        
        self.escalation_manager.stop_escalation_processor()
        self.is_active = False
        self.logger.info("Automated alert system stopped")
    
    async def check_alerts(self, metrics: SystemMetrics, additional_context: Optional[Dict[str, Any]] = None) -> List[Alert]:
        """Check all alert rules against current metrics"""
        if not self.is_active:
            return []
        
        triggered_alerts = []
        current_time = datetime.now(timezone.utc)
        
        # Prepare evaluation context
        context = self.alert_evaluator.prepare_context(metrics, additional_context)
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            # Check cooldown
            last_alert_time = self.last_alerts.get(rule.name)
            if last_alert_time:
                time_since_last = (current_time - last_alert_time).total_seconds() / 60
                if time_since_last < rule.cooldown_minutes:
                    continue
            
            # Evaluate condition
            if self.alert_evaluator.evaluate_condition(rule.condition, context):
                # Create alert
                alert = Alert(
                    timestamp=current_time.isoformat(),
                    alert_type=rule.name,
                    severity=rule.severity,
                    metric_name="system_metrics",
                    current_value=0,  # Would extract specific value based on condition
                    threshold_value=0,  # Would extract threshold based on condition
                    message=f"{rule.description} - {rule.condition}",
                    context=context
                )
                
                triggered_alerts.append(alert)
                self.last_alerts[rule.name] = current_time
                
                # Send notifications
                await self.notification_manager.send_notification(alert, rule.notification_channels)
                
                # Register for escalation
                self.escalation_manager.register_alert_for_escalation(alert)
                
                self.logger.warning(f"Alert triggered: {rule.name}")
        
        # Store in history
        if triggered_alerts:
            self.alert_history.extend(triggered_alerts)
        
        return triggered_alerts
    
    def add_alert_rule(self, rule: AlertRule):
        """Add custom alert rule"""
        self.alert_rules.append(rule)
        self.logger.info(f"Added alert rule: {rule.name}")
    
    def remove_alert_rule(self, rule_name: str):
        """Remove alert rule"""
        self.alert_rules = [rule for rule in self.alert_rules if rule.name != rule_name]
        self.logger.info(f"Removed alert rule: {rule_name}")
    
    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert summary"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        recent_alerts = [
            alert for alert in self.alert_history
            if datetime.fromisoformat(alert.timestamp.replace('Z', '+00:00')) > cutoff_time
        ]
        
        severity_counts = defaultdict(int)
        for alert in recent_alerts:
            severity_counts[alert.severity] += 1
        
        return {
            "period_hours": hours,
            "total_alerts": len(recent_alerts),
            "severity_breakdown": dict(severity_counts),
            "recent_alerts": [asdict(alert) for alert in recent_alerts[-10:]],
            "active_rules": len([rule for rule in self.alert_rules if rule.enabled]),
            "system_active": self.is_active
        }


# Global alert system instance
alert_system = AutomatedAlertSystem()

# Convenience functions
def start_alert_system():
    """Start the automated alert system"""
    alert_system.start()

def stop_alert_system():
    """Stop the automated alert system"""
    alert_system.stop()

async def check_system_alerts(metrics: SystemMetrics, additional_context: Optional[Dict[str, Any]] = None) -> List[Alert]:
    """Check system alerts"""
    return await alert_system.check_alerts(metrics, additional_context)

def get_alert_system_status() -> Dict[str, Any]:
    """Get alert system status"""
    return {
        "active": alert_system.is_active,
        "total_rules": len(alert_system.alert_rules),
        "enabled_rules": len([rule for rule in alert_system.alert_rules if rule.enabled]),
        "notification_channels": len(alert_system.notification_manager.channels),
        "escalation_rules": len(alert_system.escalation_manager.escalation_rules),
        "pending_escalations": len(alert_system.escalation_manager.pending_escalations)
    }