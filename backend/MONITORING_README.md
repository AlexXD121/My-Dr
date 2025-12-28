# MyDoc AI Monitoring System

Comprehensive logging, performance monitoring, and alerting system for the MyDoc AI Medical Assistant.

## Features

### 🔍 Structured Logging
- **Medical Data Privacy Protection**: Automatically sanitizes sensitive medical information from logs
- **Structured JSON Logging**: Machine-readable logs with consistent format
- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Automatic log file rotation with configurable size limits
- **Context-Aware Logging**: Request IDs, user context, and performance metrics

### 📊 Performance Monitoring
- **Real-time System Metrics**: CPU, memory, disk usage, network connections
- **Application Performance**: Response times, error rates, request throughput
- **Database Monitoring**: Connection pool utilization, query performance, cache hit ratios
- **Health Scoring**: Overall system health score (0-100)
- **Trend Analysis**: Historical performance data and pattern recognition

### 🚨 Automated Alerting
- **Configurable Thresholds**: Warning and critical alert levels
- **Multiple Notification Channels**: Email, Slack, webhooks, log files
- **Alert Escalation**: Automatic escalation for persistent issues
- **Cooldown Periods**: Prevent alert spam with configurable cooldowns
- **Emergency Detection**: Special handling for medical emergency situations

### 📈 Health Dashboard
- **Real-time Visualization**: Live system health metrics and charts
- **Interactive Charts**: CPU, memory, response time trends
- **Alert History**: Recent alerts and their status
- **Component Status**: Individual component health indicators
- **Mobile Responsive**: Works on desktop and mobile devices

## Quick Start

### 1. Initialize the Monitoring System

```bash
# Navigate to backend directory
cd backend

# Initialize monitoring system
python init_monitoring.py

# Or validate configuration only
python init_monitoring.py --validate-only

# Create environment template
python init_monitoring.py --create-env-template
```

### 2. Configure Environment Variables

Copy the generated `monitoring.env.template` to your `.env` file and configure:

```bash
# Essential monitoring settings
LOG_LEVEL=INFO
MONITORING_ENABLED=true
ALERTS_ENABLED=true

# Email alerts (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL_TO=admin@yourdomain.com

# Slack alerts (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
SLACK_CHANNEL=#alerts
```

### 3. Access the Health Dashboard

Once the system is running, access the health dashboard at:
```
http://localhost:8000/monitoring/dashboard-ui
```

## API Endpoints

### Health and Status
- `GET /monitoring/health` - System health status
- `GET /monitoring/ping` - Simple health check
- `GET /monitoring/dashboard-ui` - Health dashboard UI

### Metrics and Data
- `GET /monitoring/metrics?period_minutes=60` - System metrics
- `GET /monitoring/alerts?period_hours=24` - Recent alerts
- `GET /monitoring/logs?level=ERROR&limit=100` - System logs

### Control
- `POST /monitoring/monitoring/start` - Start monitoring
- `POST /monitoring/monitoring/stop` - Stop monitoring
- `GET /monitoring/logs/download?log_type=app` - Download logs
- `DELETE /monitoring/logs/cleanup?days_to_keep=30` - Cleanup old logs

## Configuration

### Logging Configuration
```bash
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_DIRECTORY=logs               # Log file directory
LOG_MAX_FILE_SIZE_MB=100        # Max log file size in MB
LOG_BACKUP_COUNT=10             # Number of backup files to keep
LOG_ENABLE_CONSOLE=true         # Enable console logging
LOG_ENABLE_FILE=true            # Enable file logging
LOG_RETENTION_DAYS=30           # Days to keep log files
```

### Monitoring Configuration
```bash
MONITORING_ENABLED=true                    # Enable/disable monitoring
MONITORING_INTERVAL_SECONDS=30            # Metrics collection interval
MONITORING_METRICS_RETENTION=1000         # Number of metrics to keep in memory
MONITORING_ENABLE_SYSTEM=true             # System metrics (CPU, memory, etc.)
MONITORING_ENABLE_DATABASE=true           # Database performance metrics
MONITORING_ENABLE_APPLICATION=true        # Application-specific metrics
```

### Alert Configuration
```bash
ALERTS_ENABLED=true                       # Enable/disable alerts
ALERTS_DEFAULT_COOLDOWN_MINUTES=15        # Default cooldown between alerts
ALERTS_ENABLE_EMAIL=true                  # Enable email notifications
ALERTS_ENABLE_WEBHOOK=false               # Enable webhook notifications
ALERTS_ENABLE_SLACK=false                 # Enable Slack notifications
ALERTS_ENABLE_ESCALATION=true             # Enable alert escalation
ALERTS_ESCALATION_TIME_MINUTES=30         # Time before escalation
```

## Alert Rules

The system includes default alert rules for:

### System Alerts
- **High CPU Usage**: CPU > 90% (critical), > 75% (warning)
- **High Memory Usage**: Memory > 95% (critical), > 80% (warning)
- **Low Disk Space**: < 1GB free (critical), < 5GB free (warning)
- **High Error Rate**: > 10% (critical), > 5% (warning)
- **Slow Response Time**: > 2000ms (critical), > 1000ms (warning)

### Database Alerts
- **Connection Pool Issues**: Pool utilization > 90%
- **Slow Queries**: Query time > 1000ms
- **Low Cache Hit Ratio**: < 80%
- **Blocked Queries**: Any blocked queries detected

### Medical System Alerts
- **Emergency Consultations**: Automatic alerts for detected emergencies
- **AI Service Failures**: Alerts when AI services are unavailable
- **Data Privacy Violations**: Alerts for potential privacy issues

## Log Files

The system creates several log files:

- `mydoc_app.jsonl` - Application logs (structured JSON)
- `mydoc_errors.jsonl` - Error logs only
- `mydoc_performance.jsonl` - Performance metrics
- `mydoc_medical.jsonl` - Medical consultation logs (privacy protected)

## Privacy Protection

The monitoring system includes comprehensive privacy protection:

### Medical Data Sanitization
- Automatically detects and redacts sensitive medical information
- Hashes consistent identifiers for tracking without exposing data
- Protects SSNs, phone numbers, email addresses, medical record numbers
- Sanitizes medical terminology that might be sensitive

### Compliance Features
- HIPAA-compliant logging practices
- Configurable data retention policies
- Secure log file permissions
- Encrypted sensitive data in logs

## Troubleshooting

### Common Issues

#### Monitoring Not Starting
```bash
# Check configuration
python init_monitoring.py --validate-only

# Check logs
tail -f logs/mydoc_errors.jsonl

# Restart monitoring
python init_monitoring.py --stop
python init_monitoring.py
```

#### Email Alerts Not Working
```bash
# Verify SMTP settings
python -c "
import smtplib
server = smtplib.SMTP('your-smtp-server', 587)
server.starttls()
server.login('username', 'password')
print('SMTP connection successful')
"
```

#### High Memory Usage
```bash
# Check log file sizes
du -sh logs/*

# Cleanup old logs
python init_monitoring.py --cleanup-logs --days=7

# Reduce metrics retention
# Set MONITORING_METRICS_RETENTION=500 in .env
```

### Performance Tuning

#### For High-Traffic Systems
```bash
# Increase monitoring interval
MONITORING_INTERVAL_SECONDS=60

# Reduce metrics retention
MONITORING_METRICS_RETENTION=500

# Disable console logging in production
LOG_ENABLE_CONSOLE=false
```

#### For Development
```bash
# Enable debug logging
LOG_LEVEL=DEBUG

# Shorter monitoring interval
MONITORING_INTERVAL_SECONDS=15

# Enable all monitoring features
MONITORING_ENABLE_SYSTEM=true
MONITORING_ENABLE_DATABASE=true
MONITORING_ENABLE_APPLICATION=true
```

## Integration with Existing Code

### Adding Monitoring to New Endpoints

```python
from monitoring_middleware import monitor_medical_consultation
from logging_system import get_medical_logger, LogContext

logger = get_medical_logger("my_module")

@monitor_medical_consultation
async def my_medical_endpoint():
    # Your endpoint code here
    pass

# Manual logging with context
context = LogContext(
    user_id="user123",
    endpoint="/my-endpoint",
    request_id="req456"
)

logger.info("Processing request", context=context)
```

### Database Operation Monitoring

```python
from monitoring_middleware import monitor_db_operation

@monitor_db_operation("select", "users")
def get_user(user_id: str):
    # Database operation
    pass
```

## Support

For issues or questions about the monitoring system:

1. Check the logs in the configured log directory
2. Run the validation: `python init_monitoring.py --validate-only`
3. Generate a status report: `python init_monitoring.py --status-report`
4. Review the configuration in your `.env` file

## Security Considerations

- Log files contain sensitive information - ensure proper file permissions
- Use secure SMTP credentials for email alerts
- Webhook URLs should use HTTPS
- Consider log encryption for highly sensitive environments
- Regularly rotate and cleanup old log files
- Monitor access to the health dashboard endpoint