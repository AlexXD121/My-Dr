# Production Database Infrastructure - My Dr AI Medical Assistant

This document provides comprehensive guidance for setting up and managing the production database infrastructure for the My Dr AI Medical Assistant application.

## 🏗️ Architecture Overview

The production database infrastructure includes:

- **PostgreSQL Database** with optimized configuration for medical data
- **Connection Pooling** with SQLAlchemy and asyncpg
- **Comprehensive Monitoring** with real-time health checks
- **Automated Backup System** with retention policies
- **Performance Optimization** with query analysis and indexing
- **Security Features** with SSL/TLS encryption and access controls

## 📁 File Structure

```
backend/
├── production_database.py      # Core database manager with connection pooling
├── production_config.py        # Production configuration settings
├── database_monitoring.py      # Monitoring and alerting system
├── init_production_db.py      # Database initialization script
├── setup_production_db.py     # Complete setup orchestrator
├── db_health_check.py         # Health check and diagnostics
├── db_maintenance.py          # Maintenance and optimization tasks
├── create_production_env.py   # Environment configuration generator
└── PRODUCTION_DATABASE_README.md  # This documentation
```

## 🚀 Quick Start

### 1. Environment Setup

Create production environment configuration:

```bash
# Interactive setup (recommended)
python backend/create_production_env.py --interactive

# Or create basic template
python backend/create_production_env.py --env-only
```

### 2. Database Setup

Run the complete production database setup:

```bash
python backend/setup_production_db.py
```

### 3. Health Check

Verify database health:

```bash
python backend/db_health_check.py
```

## 📋 Detailed Setup Guide

### Prerequisites

1. **PostgreSQL 13+** installed and running
2. **Python 3.8+** with required packages
3. **Redis** (optional, for caching)
4. **System user** with appropriate permissions

### Required Python Packages

```bash
pip install -r requirements.txt
```

Key dependencies:
- `sqlalchemy[asyncio]>=2.0`
- `asyncpg>=0.28`
- `psycopg2-binary>=2.9`
- `pydantic-settings>=2.0`
- `psutil>=5.9`

### Environment Configuration

The production environment requires the following key variables:

#### Database Configuration
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydoc_production
DB_USER=mydoc_user
DB_PASSWORD=your_secure_password
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_SSL_MODE=require
```

#### Security Configuration
```env
JWT_SECRET_KEY=your_64_character_secret_key
JAN_API_KEY=your_jan_api_key
```

#### Firebase Configuration
```env
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=service-account@project.iam.gserviceaccount.com
```

### Database User Setup

Create a dedicated database user:

```sql
-- Connect as postgres superuser
CREATE USER mydoc_user WITH PASSWORD 'your_secure_password';
CREATE DATABASE mydoc_production OWNER mydoc_user;
GRANT ALL PRIVILEGES ON DATABASE mydoc_production TO mydoc_user;

-- Connect to mydoc_production database
GRANT ALL ON SCHEMA public TO mydoc_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mydoc_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mydoc_user;
```

## 🔧 Configuration Details

### Database Configuration (`DatabaseConfig`)

```python
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "mydoc_production"
    username: str = "mydoc_user"
    password: str = "secure_password"
    
    # Connection pool settings
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # Performance settings
    statement_timeout: int = 300
    idle_in_transaction_timeout: int = 60
    
    # SSL settings
    ssl_mode: str = "require"
```

### Connection Pool Optimization

The production setup includes optimized connection pooling:

- **Pool Size**: 20 connections (adjustable based on load)
- **Max Overflow**: 30 additional connections during peak load
- **Pool Timeout**: 30 seconds for connection acquisition
- **Pool Recycle**: 1 hour connection lifetime
- **Pre-ping**: Validates connections before use

### PostgreSQL Optimizations

The setup automatically applies PostgreSQL optimizations:

```sql
-- Memory settings
SET work_mem = '256MB';
SET maintenance_work_mem = '512MB';
SET effective_cache_size = '4GB';

-- I/O settings (for SSD)
SET random_page_cost = 1.1;
SET seq_page_cost = 1.0;

-- Query planner settings
SET enable_hashjoin = on;
SET enable_mergejoin = on;
SET enable_nestloop = on;
```

## 📊 Monitoring and Health Checks

### Health Check System

The health check system monitors:

- **Connection Health**: Sync and async connection tests
- **Performance Metrics**: Query times, cache hit ratios
- **Connection Pool**: Utilization and overflow status
- **Storage Health**: Database size and disk usage
- **Backup Status**: Backup age and availability
- **Monitoring System**: Active monitoring status

### Running Health Checks

```bash
# Basic health check
python backend/db_health_check.py

# JSON output
python backend/db_health_check.py --json

# Save report
python backend/db_health_check.py --save-report /var/log/mydoc/health_report.json

# Set alert threshold
python backend/db_health_check.py --alert-threshold 80
```

### Monitoring Metrics

The monitoring system collects:

- Connection pool utilization
- Query performance metrics
- Cache hit ratios
- Long-running queries
- Blocked queries
- Storage usage
- System resource usage

### Alert Thresholds

Default alert thresholds:
- **Pool Utilization**: Warning at 75%, Critical at 90%
- **Query Time**: Warning at 500ms, Critical at 1000ms
- **Cache Hit Ratio**: Warning below 90%, Critical below 80%
- **Long Queries**: Warning at 5, Critical at 10
- **CPU Usage**: Warning at 75%, Critical at 90%
- **Memory Usage**: Warning at 80%, Critical at 90%

## 💾 Backup System

### Automated Backups

The backup system provides:

- **Full Backups**: Complete database dump (daily at 2 AM)
- **Incremental Backups**: Transaction log backups (hourly)
- **Schema Backups**: Structure-only backups (weekly)
- **Maintenance Backups**: Pre-maintenance snapshots

### Backup Configuration

```python
# Backup schedules (cron format)
BACKUP_SCHEDULE_FULL = "0 2 * * *"      # Daily at 2 AM
BACKUP_SCHEDULE_INCREMENTAL = "0 * * * *" # Hourly
BACKUP_SCHEDULE_SCHEMA = "0 1 * * 0"     # Weekly on Sunday
```

### Manual Backup Operations

```bash
# Create full backup
python -c "from backend.production_database import backup_manager; print(backup_manager.create_backup('full'))"

# Create schema backup
python -c "from backend.production_database import backup_manager; print(backup_manager.create_backup('schema_only'))"

# Restore from backup
python -c "from backend.production_database import backup_manager; print(backup_manager.restore_backup('/path/to/backup.sql'))"
```

### Backup Retention

- **Full Backups**: 30 days retention
- **Incremental Backups**: 7 days retention
- **Schema Backups**: 90 days retention
- **Maintenance Backups**: 14 days retention

## 🔧 Maintenance Tasks

### Automated Maintenance

The maintenance system includes:

- **VACUUM ANALYZE**: Remove dead tuples and update statistics
- **REINDEX**: Rebuild indexes for optimal performance
- **Statistics Update**: Refresh query planner statistics
- **Data Cleanup**: Remove old data based on retention policies
- **Index Optimization**: Identify unused and duplicate indexes
- **Bloat Analysis**: Detect table and index bloat

### Running Maintenance

```bash
# Full maintenance (recommended weekly)
python backend/db_maintenance.py

# Specific tasks
python backend/db_maintenance.py --tasks vacuum_analyze update_statistics

# Skip backup
python backend/db_maintenance.py --no-backup

# Custom retention period
python backend/db_maintenance.py --retention-days 60

# Save report
python backend/db_maintenance.py --save-report /var/log/mydoc/maintenance_report.json
```

### Maintenance Schedule

Recommended maintenance schedule:

```cron
# Daily backup
0 2 * * * python /opt/mydoc/backend/db_maintenance.py --tasks backup

# Weekly maintenance
0 3 * * 0 python /opt/mydoc/backend/db_maintenance.py --tasks vacuum_analyze update_statistics

# Monthly deep maintenance
0 4 1 * * python /opt/mydoc/backend/db_maintenance.py --tasks vacuum_analyze update_statistics optimize_indexes cleanup_old_data
```

## 🔒 Security Features

### SSL/TLS Configuration

```env
DB_SSL_MODE=require
DB_SSL_CERT=/path/to/client-cert.pem
DB_SSL_KEY=/path/to/client-key.pem
DB_SSL_CA=/path/to/ca-cert.pem
```

### Connection Security

- **SSL/TLS Encryption**: All connections encrypted
- **Certificate Validation**: Client certificate authentication
- **Connection Timeouts**: Prevent connection exhaustion
- **IP Restrictions**: Database-level IP filtering

### Data Protection

- **User Isolation**: Each user can only access their own data
- **Audit Logging**: All database operations logged
- **Backup Encryption**: Encrypted backup storage
- **Key Rotation**: Regular key rotation procedures

## 📈 Performance Optimization

### Query Optimization

The system includes automatic query optimization:

- **Index Analysis**: Identify missing and unused indexes
- **Query Plan Analysis**: Optimize slow queries
- **Statistics Updates**: Keep query planner statistics current
- **Connection Pooling**: Minimize connection overhead

### Performance Monitoring

Key performance metrics:

- **Query Response Time**: Average and 95th percentile
- **Cache Hit Ratio**: Buffer cache effectiveness
- **Connection Pool Utilization**: Resource usage
- **Index Usage**: Index effectiveness
- **Lock Contention**: Blocking and deadlocks

### Optimization Recommendations

Based on monitoring data, the system provides:

- Index creation suggestions
- Query optimization recommendations
- Configuration tuning advice
- Resource allocation guidance

## 🚨 Troubleshooting

### Common Issues

#### Connection Pool Exhaustion
```
Error: QueuePool limit of size 20 overflow 30 reached
```
**Solution**: Increase pool size or investigate connection leaks

#### Slow Query Performance
```
Warning: Query time 1500ms exceeds threshold
```
**Solution**: Run ANALYZE, check indexes, optimize queries

#### High Memory Usage
```
Alert: Memory usage 95% exceeds threshold
```
**Solution**: Adjust work_mem, shared_buffers, or add RAM

#### Backup Failures
```
Error: pg_dump failed with exit code 1
```
**Solution**: Check disk space, permissions, and PostgreSQL logs

### Diagnostic Commands

```bash
# Check database health
python backend/db_health_check.py

# View connection pool status
python -c "from backend.production_database import production_db_manager; print(production_db_manager.comprehensive_health_check())"

# Check for long-running queries
python -c "from backend.production_database import production_db_manager; stats = production_db_manager.get_database_statistics(); print(stats)"

# Monitor real-time metrics
python -c "from backend.database_monitoring import get_monitoring_status; print(get_monitoring_status())"
```

### Log Analysis

Important log locations:

- **Application Logs**: `/var/log/mydoc/app.log`
- **Database Logs**: PostgreSQL log directory
- **Backup Logs**: `/var/log/mydoc/backup.log`
- **Maintenance Logs**: `/var/log/mydoc/maintenance.log`
- **Health Check Logs**: `/var/log/mydoc/health_check.log`

## 🔄 Deployment Integration

### Systemd Service

The production setup includes systemd integration:

```ini
[Unit]
Description=MyDoc AI Medical Assistant API
After=network.target postgresql.service

[Service]
Type=exec
User=mydoc
WorkingDirectory=/opt/mydoc
EnvironmentFile=/opt/mydoc/.env.production
ExecStart=/usr/local/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Docker Integration

For containerized deployment:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Setup database
RUN python backend/setup_production_db.py

# Start application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Deploy Production Database

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run database setup
        run: python backend/setup_production_db.py --test-only
        env:
          DB_HOST: ${{ secrets.DB_HOST }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
      
      - name: Health check
        run: python backend/db_health_check.py --json
```

## 📚 API Reference

### Core Classes

#### `ProductionDatabaseManager`
Main database manager with connection pooling and monitoring.

```python
from backend.production_database import production_db_manager

# Test connection
success, error = production_db_manager.test_connection()

# Get health check
health = production_db_manager.comprehensive_health_check()

# Get statistics
stats = production_db_manager.get_database_statistics()
```

#### `DatabaseBackupManager`
Handles automated backups and recovery.

```python
from backend.production_database import backup_manager

# Create backup
result = backup_manager.create_backup("full")

# Restore backup
result = backup_manager.restore_backup("/path/to/backup.sql")

# Schedule backups
schedule = backup_manager.schedule_automated_backups()
```

#### `DatabaseMonitor`
Real-time monitoring and alerting.

```python
from backend.database_monitoring import database_monitor

# Start monitoring
database_monitor.start_monitoring()

# Get current status
status = database_monitor.get_current_status()

# Get health dashboard
dashboard = database_monitor.get_health_dashboard()
```

### Configuration Classes

#### `ProductionSettings`
Complete production configuration with validation.

```python
from backend.production_config import load_production_settings

settings = load_production_settings()
print(f"Database URL: {settings.get_database_url()}")
print(f"Environment: {settings.environment}")
```

## 🆘 Support and Maintenance

### Regular Maintenance Tasks

**Daily**:
- Monitor health check results
- Review backup status
- Check error logs

**Weekly**:
- Run database maintenance
- Review performance metrics
- Update statistics

**Monthly**:
- Deep maintenance with cleanup
- Review and optimize indexes
- Update configuration as needed

**Quarterly**:
- Security audit
- Performance review
- Capacity planning

### Getting Help

For issues with the production database setup:

1. **Check Health Status**: Run `python backend/db_health_check.py`
2. **Review Logs**: Check application and database logs
3. **Run Diagnostics**: Use maintenance and monitoring tools
4. **Consult Documentation**: Review this README and code comments

### Contributing

When modifying the production database infrastructure:

1. **Test Thoroughly**: Use development environment first
2. **Document Changes**: Update this README
3. **Monitor Impact**: Watch metrics after deployment
4. **Backup First**: Always create backups before changes

---

## 📄 License

This production database infrastructure is part of the My Dr AI Medical Assistant project and follows the same licensing terms.

---

**Last Updated**: January 2024
**Version**: 1.0.0
**Maintainer**: My Dr AI Development Team