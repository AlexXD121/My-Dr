import os
import secrets
import logging
from typing import List, Optional
from pydantic import validator, Field
from pydantic_settings import BaseSettings
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Application environment types"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Simplified application settings"""
    # Application metadata
    app_name: str = Field("MyDoc AI Medical Assistant API", description="Application name")
    app_version: str = Field("1.0.0", description="Application version")
    app_description: str = Field("A secure AI-powered medical assistant API", description="App description")
    
    # Environment
    environment: Environment = Field(Environment.DEVELOPMENT, description="Application environment")
    debug: bool = Field(True, description="Debug mode")
    
    # Server configuration
    host: str = Field("0.0.0.0", description="Server host")
    port: int = Field(8000, description="Server port")
    
    # Security Configuration
    jwt_secret_key: str = Field(..., description="JWT secret key")
    jwt_algorithm: str = Field("HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(24, description="JWT expiration in hours")
    allowed_origins: str = Field("http://localhost:5173,http://localhost:3000", description="Allowed CORS origins")
    
    # AI Configuration
    use_local_ai: bool = Field(True, description="Use local AI models (Jan AI)")
    jan_url: str = Field("http://localhost:1337", description="Jan AI API URL")
    jan_model: str = Field("Llama-3_2-3B-Instruct-IQ4_XS", description="Jan AI model name")
    jan_api_key: str = Field("mydoc-ai-key", description="Jan AI API key")
    
    # Fallback API providers
    perplexity_api_key: str = Field("", description="Perplexity API key (fallback)")
    huggingface_api_key: str = Field("", description="Hugging Face API key (fallback)")
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./mydoc.db", 
        description="Database URL - will use DATABASE_URL env var if available"
    )
    
    def __init__(self, **kwargs):
        # Override database_url with environment variable if available
        if 'DATABASE_URL' in os.environ:
            kwargs['database_url'] = os.environ['DATABASE_URL']
        super().__init__(**kwargs)
    
    @validator('jwt_secret_key')
    def validate_jwt_secret(cls, v):
        if not v:
            # Generate a secure random key if not provided
            logger.warning("JWT_SECRET_KEY not provided, generating random key")
            return secrets.token_urlsafe(32)
        
        if len(v) < 32:
            raise ValueError('JWT_SECRET_KEY must be at least 32 characters long')
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        if isinstance(v, str):
            try:
                return Environment(v.lower())
            except ValueError:
                raise ValueError(f'Invalid environment: {v}. Must be one of: {list(Environment)}')
        return v
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == Environment.DEVELOPMENT
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def load_settings() -> Settings:
    """Load and validate settings"""
    try:
        settings = Settings()
        
        # Log configuration summary (without sensitive data)
        logger.info(f"Loaded configuration for environment: {settings.environment}")
        logger.info(f"Debug mode: {settings.debug}")
        logger.info(f"Local AI enabled: {settings.use_local_ai}")
        
        return settings
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise


# Global settings instance
settings = load_settings()

# Legacy compatibility - expose commonly used settings at module level
jwt_secret_key = settings.jwt_secret_key
jwt_algorithm = settings.jwt_algorithm
jwt_expiration_hours = settings.jwt_expiration_hours
allowed_origins = settings.allowed_origins
environment = settings.environment
debug = settings.debug