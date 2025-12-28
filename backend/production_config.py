"""
Production Configuration for My Dr AI Medical Assistant
Environment-specific settings for production deployment
"""
import os
import secrets
import logging
from typing import List, Optional, Dict, Any
from pydantic import validator, Field
from pydantic_settings import BaseSettings
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Application environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ProductionSettings(BaseSettings):
    """Production-ready application settings"""
    
    # Application metadata
    app_name: str = Field("MyDoc AI Medical Assistant API", description="Application name")
    app_version: str = Field("1.0.0", description="Application version")
    app_description: str = Field("A secure AI-powered medical assistant API", description="App description")
    
    # Environment
    environment: Environment = Field(Environment.PRODUCTION, description="Application environment")
    debug: bool = Field(False, description="Debug mode (disabled in production)")
    
    # Server configuration
    host: str = Field("0.0.0.0", description="Server host")
    port: int = Field(8000, description="Server port")
    workers: int = Field(4, description="Number of worker processes")
    
    # Security Configuration
    jwt_secret_key: str = Field(..., description="JWT secret key")
    jwt_algorithm: str = Field("HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(24, description="JWT expiration in hours")
    
    # CORS Configuration
    allowed_origins: List[str] = Field(
        default_factory=lambda: ["https://mydoc.ai", "https://app.mydoc.ai"],
        description="Allowed CORS origins"
    )
    allowed_methods: List[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed HTTP methods"
    )
    allowed_headers: List[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed headers"
    )
    
    # Database Configuration (PostgreSQL)
    db_host: str = Field(..., description="Database host")
    db_port: int = Field(5432, description="Database port")
    db_name: str = Field(..., description="Database name")
    db_user: str = Field(..., description="Database user")
    db_password: str = Field(..., description="Database password")
    db_pool_size: int = Field(20, description="Database connection pool size")
    db_max_overflow: int = Field(30, description="Database max overflow connections")
    db_pool_timeout: int = Field(30, description="Database pool timeout")
    db_pool_recycle: int = Field(3600, description="Database pool recycle time")
    
    # SSL/TLS Configuration
    db_ssl_mode: str = Field("require", description="Database SSL mode")
    db_ssl_cert: Optional[str] = Field(None, description="Database SSL certificate")
    db_ssl_key: Optional[str] = Field(None, description="Database SSL key")
    db_ssl_ca: Optional[str] = Field(None, description="Database SSL CA")
    
    # Redis Configuration (for caching and sessions)
    redis_host: str = Field("localhost", description="Redis host")
    redis_port: int = Field(6379, description="Redis port")
    redis_password: Optional[str] = Field(None, description="Redis password")
    redis_db: int = Field(0, description="Redis database number")
    redis_ssl: bool = Field(False, description="Use SSL for Redis")
    
    # AI Configuration
    use_local_ai: bool = Field(True, description="Use local AI models")
    jan_url: str = Field("http://localhost:1337", description="Jan AI API URL")
    jan_model: str = Field("Llama-3_2-3B-Instruct-IQ4_XS", description="Jan AI model name")
    jan_api_key: str = Field(..., description="Jan AI API key")
    jan_timeout: int = Field(30, description="Jan AI request timeout")
    jan_max_retries: int = Field(3, description="Jan AI max retries")
    
    # Fallback AI providers
    perplexity_api_key: Optional[str] = Field(None, description="Perplexity API key")
    huggingface_api_key: Optional[str] = Field(None, description="Hugging Face API key")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    
    # Firebase Configuration
    firebase_project_id: str = Field(..., description="Firebase project ID")
    firebase_private_key_id: str = Field(..., description="Firebase private key ID")
    firebase_private_key: str = Field(..., description="Firebase private key")
    firebase_client_email: str = Field(..., description="Firebase client email")
    firebase_client_id: str = Field(..., description="Firebase client ID")
    firebase_auth_uri: str = Field("https://accounts.google.com/o/oauth2/auth", description="Firebase auth URI")
    firebase_token_uri: str = Field("https://oauth2.googleapis.com/token", description="Firebase token URI")
    
    # Logging Configuration
    log_level: LogLevel = Field(LogLevel.INFO, description="Logging level")
    log_format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    log_file: Optional[str] = Field("/var/log/mydoc/app.log", description="Log file path")
    log_max_size: int = Field(100 * 1024 * 1024, description="Max log file size (100MB)")
    log_backup_count: int = Field(5, description="Number of log backup files")
    
    # Monitoring Configuration
    enable_monitoring: bool = Field(True, description="Enable database monitoring")
    monitoring_interval: int = Field(60, description="Monitoring interval in seconds")
    
    # Alert Configuration
    smtp_server: str = Field("localhost", description="SMTP server")
    smtp_port: int = Field(587, description="SMTP port")
    smtp_username: Optional[str] = Field(None, description="SMTP username")
    smtp_password: Optional[str] = Field(None, description="SMTP password")
    smtp_use_tls: bool = Field(True, description="Use TLS for SMTP")
    alert_email_from: str = Field("alerts@mydoc.ai", description="Alert email sender")
    alert_email_to: List[str] = Field(
        default_factory=lambda: ["admin@mydoc.ai"],
        description="Alert email recipients"
    )
    
    # Backup Configuration
    backup_enabled: bool = Field(True, description="Enable automated backups")
    backup_directory: str = Field("/var/backups/mydoc", description="Backup directory")
    backup_retention_days: int = Field(30, description="Backup retention period")
    backup_schedule_full: str = Field("0 2 * * *", description="Full backup cron schedule")
    backup_schedule_incremental: str = Field("0 * * * *", description="Incremental backup cron schedule")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(True, description="Enable rate limiting")
    rate_limit_requests: int = Field(100, description="Requests per minute per IP")
    rate_limit_window: int = Field(60, description="Rate limit window in seconds")
    
    # File Upload Configuration
    max_file_size: int = Field(10 * 1024 * 1024, description="Max file upload size (10MB)")
    allowed_file_types: List[str] = Field(
        default_factory=lambda: [".pdf", ".jpg", ".jpeg", ".png", ".txt", ".doc", ".docx"],
        description="Allowed file types for upload"
    )
    upload_directory: str = Field("/var/uploads/mydoc", description="File upload directory")
    
    # Session Configuration
    session_timeout: int = Field(3600, description="Session timeout in seconds")
    session_cleanup_interval: int = Field(300, description="Session cleanup interval")
    
    # Health Check Configuration
    health_check_enabled: bool = Field(True, description="Enable health checks")
    health_check_interval: int = Field(30, description="Health check interval")
    health_check_timeout: int = Field(10, description="Health check timeout")
    
    # Performance Configuration
    request_timeout: int = Field(30, description="Request timeout in seconds")
    max_concurrent_requests: int = Field(1000, description="Max concurrent requests")
    
    @validator('jwt_secret_key')
    def validate_jwt_secret(cls, v):
        if not v:
            raise ValueError('JWT_SECRET_KEY is required in production')
        if len(v) < 32:
            raise ValueError('JWT_SECRET_KEY must be at least 32 characters long')
        return v
    
    @validator('db_host', 'db_name', 'db_user', 'db_password')
    def validate_database_config(cls, v, field):
        if not v:
            raise ValueError(f'{field.name} is required in production')
        return v
    
    @validator('firebase_project_id', 'firebase_private_key', 'firebase_client_email')
    def validate_firebase_config(cls, v, field):
        if not v:
            raise ValueError(f'{field.name} is required for Firebase authentication')
        return v
    
    @validator('allowed_origins')
    def validate_cors_origins(cls, v):
        if not v:
            raise ValueError('At least one CORS origin must be specified')
        # Ensure no localhost origins in production
        for origin in v:
            if 'localhost' in origin or '127.0.0.1' in origin:
                raise ValueError('Localhost origins not allowed in production')
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        if isinstance(v, str):
            try:
                return Environment(v.lower())
            except ValueError:
                raise ValueError(f'Invalid environment: {v}')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        if isinstance(v, str):
            try:
                return LogLevel(v.upper())
            except ValueError:
                raise ValueError(f'Invalid log level: {v}')
        return v
    
    def get_database_url(self) -> str:
        """Get complete database URL"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    def get_redis_url(self) -> str:
        """Get complete Redis URL"""
        protocol = "rediss" if self.redis_ssl else "redis"
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"{protocol}://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    def get_firebase_config(self) -> Dict[str, Any]:
        """Get Firebase configuration dictionary"""
        return {
            "type": "service_account",
            "project_id": self.firebase_project_id,
            "private_key_id": self.firebase_private_key_id,
            "private_key": self.firebase_private_key.replace('\\n', '\n'),
            "client_email": self.firebase_client_email,
            "client_id": self.firebase_client_id,
            "auth_uri": self.firebase_auth_uri,
            "token_uri": self.firebase_token_uri,
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{self.firebase_client_email}"
        }
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == Environment.PRODUCTION
    
    def is_staging(self) -> bool:
        """Check if running in staging"""
        return self.environment == Environment.STAGING
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == Environment.DEVELOPMENT
    
    class Config:
        env_file = ".env.production"
        case_sensitive = False
        # Map environment variables to field names
        fields = {
            'jwt_secret_key': {'env': 'JWT_SECRET_KEY'},
            'db_host': {'env': 'DB_HOST'},
            'db_port': {'env': 'DB_PORT'},
            'db_name': {'env': 'DB_NAME'},
            'db_user': {'env': 'DB_USER'},
            'db_password': {'env': 'DB_PASSWORD'},
            'firebase_project_id': {'env': 'FIREBASE_PROJECT_ID'},
            'firebase_private_key_id': {'env': 'FIREBASE_PRIVATE_KEY_ID'},
            'firebase_private_key': {'env': 'FIREBASE_PRIVATE_KEY'},
            'firebase_client_email': {'env': 'FIREBASE_CLIENT_EMAIL'},
            'firebase_client_id': {'env': 'FIREBASE_CLIENT_ID'},
            'jan_api_key': {'env': 'JAN_API_KEY'},
            'perplexity_api_key': {'env': 'PERPLEXITY_API_KEY'},
            'huggingface_api_key': {'env': 'HUGGINGFACE_API_KEY'},
            'openai_api_key': {'env': 'OPENAI_API_KEY'},
            'smtp_username': {'env': 'SMTP_USERNAME'},
            'smtp_password': {'env': 'SMTP_PASSWORD'},
            'redis_password': {'env': 'REDIS_PASSWORD'}
        }


def load_production_settings() -> ProductionSettings:
    """Load and validate production settings"""
    try:
        settings = ProductionSettings()
        
        # Validate critical production requirements
        if settings.is_production():
            if settings.debug:
                logger.warning("Debug mode is enabled in production - this should be disabled")
            
            if not settings.db_ssl_mode or settings.db_ssl_mode == "disable":
                logger.warning("SSL is disabled for database connection in production")
        
        logger.info(f"Production configuration loaded for environment: {settings.environment}")
        logger.info(f"Database: {settings.db_host}:{settings.db_port}/{settings.db_name}")
        logger.info(f"Redis: {settings.redis_host}:{settings.redis_port}")
        logger.info(f"Monitoring enabled: {settings.enable_monitoring}")
        logger.info(f"Backup enabled: {settings.backup_enabled}")
        
        return settings
        
    except Exception as e:
        logger.error(f"Failed to load production configuration: {e}")
        raise


# Create production environment file template
def create_production_env_template():
    """Create .env.production template file"""
    template = """# Production Environment Configuration for MyDoc AI Medical Assistant

# Application Environment
ENVIRONMENT=production
DEBUG=false

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Security
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-here-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Database Configuration (PostgreSQL)
DB_HOST=your-database-host
DB_PORT=5432
DB_NAME=mydoc_production
DB_USER=mydoc_user
DB_PASSWORD=your-secure-database-password
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Database SSL
DB_SSL_MODE=require
# DB_SSL_CERT=/path/to/client-cert.pem
# DB_SSL_KEY=/path/to/client-key.pem
# DB_SSL_CA=/path/to/ca-cert.pem

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
# REDIS_PASSWORD=your-redis-password
REDIS_DB=0
REDIS_SSL=false

# AI Configuration
USE_LOCAL_AI=true
JAN_URL=http://localhost:1337
JAN_MODEL=Llama-3_2-3B-Instruct-IQ4_XS
JAN_API_KEY=your-jan-api-key
JAN_TIMEOUT=30
JAN_MAX_RETRIES=3

# Fallback AI Providers
# PERPLEXITY_API_KEY=your-perplexity-api-key
# HUGGINGFACE_API_KEY=your-huggingface-api-key
# OPENAI_API_KEY=your-openai-api-key

# Firebase Configuration
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY_ID=your-firebase-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\nYour Firebase private key here\\n-----END PRIVATE KEY-----\\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-firebase-client-id

# CORS Configuration
ALLOWED_ORIGINS=https://mydoc.ai,https://app.mydoc.ai

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/mydoc/app.log
LOG_MAX_SIZE=104857600
LOG_BACKUP_COUNT=5

# Monitoring Configuration
ENABLE_MONITORING=true
MONITORING_INTERVAL=60

# Email Alerts Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-email-password
SMTP_USE_TLS=true
ALERT_EMAIL_FROM=alerts@mydoc.ai
ALERT_EMAIL_TO=admin@mydoc.ai,ops@mydoc.ai

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
    
    with open('.env.production.template', 'w') as f:
        f.write(template)
    
    logger.info("Production environment template created: .env.production.template")
    logger.info("Copy this file to .env.production and update with your actual values")


if __name__ == "__main__":
    # Create production environment template
    create_production_env_template()
    
    # Test loading settings (will fail without proper .env.production file)
    try:
        settings = load_production_settings()
        print(f"Production settings loaded successfully for {settings.environment}")
    except Exception as e:
        print(f"Failed to load production settings: {e}")
        print("This is expected if .env.production file doesn't exist yet")