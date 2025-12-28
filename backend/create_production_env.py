#!/usr/bin/env python3
"""
Production Environment Setup Script for My Dr AI Medical Assistant
Creates production environment configuration and validates setup
"""
import os
import sys
import secrets
import logging
import argparse
from typing import Dict, Any
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionEnvironmentSetup:
    """Production environment configuration setup"""
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.project_root = self.backend_dir.parent
        self.env_file = self.project_root / ".env.production"
        
    def generate_secure_keys(self) -> Dict[str, str]:
        """Generate secure keys for production"""
        return {
            "JWT_SECRET_KEY": secrets.token_urlsafe(64),
            "JAN_API_KEY": f"mydoc-{secrets.token_urlsafe(32)}",
            "SESSION_SECRET": secrets.token_urlsafe(32)
        }
    
    def create_production_env_file(self, config: Dict[str, Any]) -> bool:
        """Create production environment file"""
        try:
            env_content = f"""# Production Environment Configuration for MyDoc AI Medical Assistant
# Generated on {config.get('timestamp', 'unknown')}

# Application Environment
ENVIRONMENT=production
DEBUG=false

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Security Configuration
JWT_SECRET_KEY={config['security']['jwt_secret_key']}
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Database Configuration (PostgreSQL)
DB_HOST={config['database']['host']}
DB_PORT={config['database']['port']}
DB_NAME={config['database']['name']}
DB_USER={config['database']['user']}
DB_PASSWORD={config['database']['password']}
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Database SSL Configuration
DB_SSL_MODE=require
# DB_SSL_CERT=/path/to/client-cert.pem
# DB_SSL_KEY=/path/to/client-key.pem
# DB_SSL_CA=/path/to/ca-cert.pem

# Redis Configuration
REDIS_HOST={config['redis']['host']}
REDIS_PORT={config['redis']['port']}
REDIS_DB=0
REDIS_SSL=false
# REDIS_PASSWORD=your-redis-password

# AI Configuration
USE_LOCAL_AI=true
JAN_URL={config['ai']['jan_url']}
JAN_MODEL=Llama-3_2-3B-Instruct-IQ4_XS
JAN_API_KEY={config['security']['jan_api_key']}
JAN_TIMEOUT=30
JAN_MAX_RETRIES=3

# Fallback AI Providers (Optional)
# PERPLEXITY_API_KEY=your-perplexity-api-key
# HUGGINGFACE_API_KEY=your-huggingface-api-key
# OPENAI_API_KEY=your-openai-api-key

# Firebase Configuration
FIREBASE_PROJECT_ID={config['firebase']['project_id']}
FIREBASE_PRIVATE_KEY_ID={config['firebase']['private_key_id']}
FIREBASE_PRIVATE_KEY="{config['firebase']['private_key']}"
FIREBASE_CLIENT_EMAIL={config['firebase']['client_email']}
FIREBASE_CLIENT_ID={config['firebase']['client_id']}
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token

# CORS Configuration
ALLOWED_ORIGINS={config['cors']['allowed_origins']}

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/mydoc/app.log
LOG_MAX_SIZE=104857600
LOG_BACKUP_COUNT=5

# Monitoring Configuration
ENABLE_MONITORING=true
MONITORING_INTERVAL=60

# Email Configuration for Alerts
SMTP_SERVER={config['email']['smtp_server']}
SMTP_PORT={config['email']['smtp_port']}
SMTP_USE_TLS=true
# SMTP_USERNAME=your-email@domain.com
# SMTP_PASSWORD=your-email-password
ALERT_EMAIL_FROM=alerts@{config['email']['domain']}
ALERT_EMAIL_TO=admin@{config['email']['domain']}

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_DIRECTORY=/var/backups/mydoc
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE_FULL="0 2 * * *"
BACKUP_SCHEDULE_INCREMENTAL="0 * * * *"

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# File Upload Configuration
MAX_FILE_SIZE=10485760
UPLOAD_DIRECTORY=/var/uploads/mydoc

# Session Configuration
SESSION_TIMEOUT=3600
SESSION_CLEANUP_INTERVAL=300

# Health Check Configuration
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10

# Performance Configuration
REQUEST_TIMEOUT=30
MAX_CONCURRENT_REQUESTS=1000
"""
            
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            
            # Set appropriate permissions
            os.chmod(self.env_file, 0o600)
            
            logger.info(f"Production environment file created: {self.env_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create production environment file: {e}")
            return False
    
    def create_systemd_service(self, config: Dict[str, Any]) -> bool:
        """Create systemd service file for production deployment"""
        try:
            service_content = f"""[Unit]
Description=MyDoc AI Medical Assistant API
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=exec
User=mydoc
Group=mydoc
WorkingDirectory={self.project_root}
Environment=PATH=/usr/local/bin:/usr/bin:/bin
EnvironmentFile={self.env_file}
ExecStart=/usr/local/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/mydoc /var/backups/mydoc /var/uploads/mydoc /tmp
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

[Install]
WantedBy=multi-user.target
"""
            
            service_file = Path("/etc/systemd/system/mydoc-api.service")
            
            # Note: This would require sudo privileges in production
            logger.info("Systemd service configuration:")
            print(service_content)
            logger.info(f"Save this content to: {service_file}")
            logger.info("Then run: sudo systemctl daemon-reload && sudo systemctl enable mydoc-api")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create systemd service: {e}")
            return False
    
    def create_nginx_config(self, config: Dict[str, Any]) -> bool:
        """Create nginx configuration for production"""
        try:
            nginx_content = f"""# MyDoc AI Medical Assistant - Nginx Configuration
server {{
    listen 80;
    listen [::]:80;
    server_name {config['domain']['api_domain']};
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {config['domain']['api_domain']};
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/{config['domain']['api_domain']}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{config['domain']['api_domain']}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' wss:";
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    # Client Settings
    client_max_body_size 10M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Logging
    access_log /var/log/nginx/mydoc-api.access.log;
    error_log /var/log/nginx/mydoc-api.error.log;
    
    # API Proxy
    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}
    
    # WebSocket Support
    location /ws {{
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # Health Check
    location /health {{
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }}
    
    # Static Files (if any)
    location /static {{
        alias /var/www/mydoc/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}

# Frontend Configuration
server {{
    listen 80;
    listen [::]:80;
    server_name {config['domain']['frontend_domain']};
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {config['domain']['frontend_domain']};
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/{config['domain']['frontend_domain']}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{config['domain']['frontend_domain']}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Document Root
    root /var/www/mydoc/frontend;
    index index.html;
    
    # Logging
    access_log /var/log/nginx/mydoc-frontend.access.log;
    error_log /var/log/nginx/mydoc-frontend.error.log;
    
    # Frontend Routes
    location / {{
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public";
    }}
    
    # Static Assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}
"""
            
            logger.info("Nginx configuration:")
            print(nginx_content)
            logger.info("Save this content to: /etc/nginx/sites-available/mydoc")
            logger.info("Then run: sudo ln -s /etc/nginx/sites-available/mydoc /etc/nginx/sites-enabled/")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create nginx configuration: {e}")
            return False
    
    def create_logrotate_config(self) -> bool:
        """Create logrotate configuration for log management"""
        try:
            logrotate_content = """/var/log/mydoc/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 mydoc mydoc
    postrotate
        systemctl reload mydoc-api
    endscript
}

/var/log/nginx/mydoc-*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload nginx
    endscript
}
"""
            
            logger.info("Logrotate configuration:")
            print(logrotate_content)
            logger.info("Save this content to: /etc/logrotate.d/mydoc")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create logrotate configuration: {e}")
            return False
    
    def create_cron_jobs(self) -> bool:
        """Create cron jobs for automated tasks"""
        try:
            cron_content = """# MyDoc AI Medical Assistant - Automated Tasks
# Database backups
0 2 * * * /usr/bin/python3 /opt/mydoc/backend/db_maintenance.py --tasks backup > /var/log/mydoc/backup.log 2>&1

# Database maintenance (weekly)
0 3 * * 0 /usr/bin/python3 /opt/mydoc/backend/db_maintenance.py --tasks vacuum_analyze update_statistics > /var/log/mydoc/maintenance.log 2>&1

# Health checks (every 5 minutes)
*/5 * * * * /usr/bin/python3 /opt/mydoc/backend/db_health_check.py --json > /var/log/mydoc/health_check.log 2>&1

# Log cleanup (monthly)
0 4 1 * * find /var/log/mydoc -name "*.log" -mtime +30 -delete

# Backup cleanup (keep 30 days)
0 5 * * * find /var/backups/mydoc -name "*.sql" -mtime +30 -delete
"""
            
            logger.info("Cron jobs configuration:")
            print(cron_content)
            logger.info("Add these entries to the mydoc user's crontab: sudo crontab -u mydoc -e")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create cron jobs: {e}")
            return False
    
    def interactive_setup(self) -> Dict[str, Any]:
        """Interactive setup for production configuration"""
        print("MyDoc AI Medical Assistant - Production Environment Setup")
        print("=" * 60)
        
        config = {
            "timestamp": "2024-01-01T00:00:00Z",
            "security": self.generate_secure_keys(),
            "database": {},
            "redis": {},
            "ai": {},
            "firebase": {},
            "cors": {},
            "email": {},
            "domain": {}
        }
        
        # Database configuration
        print("\n📊 Database Configuration (PostgreSQL)")
        config["database"]["host"] = input("Database host [localhost]: ").strip() or "localhost"
        config["database"]["port"] = input("Database port [5432]: ").strip() or "5432"
        config["database"]["name"] = input("Database name [mydoc_production]: ").strip() or "mydoc_production"
        config["database"]["user"] = input("Database user [mydoc_user]: ").strip() or "mydoc_user"
        config["database"]["password"] = input("Database password: ").strip()
        
        # Redis configuration
        print("\n🔄 Redis Configuration")
        config["redis"]["host"] = input("Redis host [localhost]: ").strip() or "localhost"
        config["redis"]["port"] = input("Redis port [6379]: ").strip() or "6379"
        
        # AI configuration
        print("\n🤖 AI Configuration")
        config["ai"]["jan_url"] = input("Jan AI URL [http://localhost:1337]: ").strip() or "http://localhost:1337"
        
        # Firebase configuration
        print("\n🔥 Firebase Configuration")
        config["firebase"]["project_id"] = input("Firebase project ID: ").strip()
        config["firebase"]["private_key_id"] = input("Firebase private key ID: ").strip()
        config["firebase"]["private_key"] = input("Firebase private key (paste full key): ").strip()
        config["firebase"]["client_email"] = input("Firebase client email: ").strip()
        config["firebase"]["client_id"] = input("Firebase client ID: ").strip()
        
        # Domain configuration
        print("\n🌐 Domain Configuration")
        config["domain"]["api_domain"] = input("API domain [api.mydoc.ai]: ").strip() or "api.mydoc.ai"
        config["domain"]["frontend_domain"] = input("Frontend domain [app.mydoc.ai]: ").strip() or "app.mydoc.ai"
        
        # CORS configuration
        config["cors"]["allowed_origins"] = f"https://{config['domain']['frontend_domain']}"
        
        # Email configuration
        print("\n📧 Email Configuration")
        config["email"]["smtp_server"] = input("SMTP server [smtp.gmail.com]: ").strip() or "smtp.gmail.com"
        config["email"]["smtp_port"] = input("SMTP port [587]: ").strip() or "587"
        config["email"]["domain"] = input("Email domain [mydoc.ai]: ").strip() or "mydoc.ai"
        
        return config


def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Production Environment Setup for MyDoc AI")
    parser.add_argument("--interactive", action="store_true", help="Interactive configuration setup")
    parser.add_argument("--create-configs", action="store_true", help="Create all configuration files")
    parser.add_argument("--env-only", action="store_true", help="Create environment file only")
    
    args = parser.parse_args()
    
    setup = ProductionEnvironmentSetup()
    
    if args.interactive:
        config = setup.interactive_setup()
        
        print("\n🔧 Creating production environment file...")
        if setup.create_production_env_file(config):
            print("✓ Environment file created successfully")
        else:
            print("✗ Failed to create environment file")
            sys.exit(1)
        
        if args.create_configs:
            print("\n🔧 Creating additional configuration files...")
            setup.create_systemd_service(config)
            setup.create_nginx_config(config)
            setup.create_logrotate_config()
            setup.create_cron_jobs()
    
    elif args.env_only:
        # Create basic environment file with placeholders
        config = {
            "timestamp": "2024-01-01T00:00:00Z",
            "security": setup.generate_secure_keys(),
            "database": {
                "host": "localhost",
                "port": "5432",
                "name": "mydoc_production",
                "user": "mydoc_user",
                "password": "CHANGE_ME"
            },
            "redis": {"host": "localhost", "port": "6379"},
            "ai": {"jan_url": "http://localhost:1337"},
            "firebase": {
                "project_id": "CHANGE_ME",
                "private_key_id": "CHANGE_ME",
                "private_key": "CHANGE_ME",
                "client_email": "CHANGE_ME",
                "client_id": "CHANGE_ME"
            },
            "cors": {"allowed_origins": "https://app.mydoc.ai"},
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": "587",
                "domain": "mydoc.ai"
            },
            "domain": {
                "api_domain": "api.mydoc.ai",
                "frontend_domain": "app.mydoc.ai"
            }
        }
        
        if setup.create_production_env_file(config):
            print("✓ Basic environment file created")
            print("⚠ Please update the CHANGE_ME values in .env.production")
        else:
            sys.exit(1)
    
    else:
        print("Use --interactive for guided setup or --env-only for basic environment file")
        print("Run with --help for more options")


if __name__ == "__main__":
    main()