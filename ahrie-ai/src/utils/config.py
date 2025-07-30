"""Configuration management using Pydantic settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    APP_NAME: str = "Ahrie AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment (development, staging, production)")
    
    # API
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "https://t.me"],
        description="Allowed CORS origins"
    )
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram bot token")
    TELEGRAM_WEBHOOK_SECRET: str = Field(default="", description="Telegram webhook secret token")
    WEBHOOK_BASE_URL: str = Field(default="", description="Base URL for webhooks (e.g., https://your-domain.com)")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", description="OpenAI model to use")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")
    
    # OpenRouter
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, description="OpenRouter API key (optional, falls back to OPENAI_API_KEY)")
    
    # YouTube
    YOUTUBE_API_KEY: str = Field(..., description="YouTube Data API key")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/ahrie_ai",
        description="PostgreSQL connection URL"
    )
    DB_POOL_MIN_SIZE: int = Field(default=10, description="Database pool minimum size")
    DB_POOL_MAX_SIZE: int = Field(default=20, description="Database pool maximum size")
    DB_POOL_MAX_QUERIES: int = Field(default=50000, description="Database pool max queries")
    DB_POOL_MAX_INACTIVE_LIFETIME: float = Field(default=300.0, description="Max inactive connection lifetime")
    DB_COMMAND_TIMEOUT: float = Field(default=60.0, description="Database command timeout")
    
    # Ngrok (for development)
    NGROK_AUTHTOKEN: Optional[str] = Field(default=None, description="Ngrok auth token for development")
    NGROK_DOMAIN: Optional[str] = Field(default=None, description="Ngrok custom domain")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # Paths
    DATA_DIR: Path = Field(default=Path("./data"), description="Data directory")
    LOG_DIR: Path = Field(default=Path("./logs"), description="Logs directory")
    VECTOR_DB_PATH: Path = Field(default=Path("./data/lancedb"), description="Vector database path")
    
    # Features
    ENABLE_YOUTUBE_SCRAPING: bool = Field(default=True, description="Enable YouTube scraping")
    ENABLE_WEB_SCRAPING: bool = Field(default=True, description="Enable web scraping")
    ENABLE_VECTOR_SEARCH: bool = Field(default=True, description="Enable vector search")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=60, description="Rate limit requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")
    
    # Cache
    CACHE_TTL: int = Field(default=3600, description="Cache TTL in seconds")
    TRANSLATION_CACHE_TTL: int = Field(default=86400, description="Translation cache TTL in seconds")
    
    @validator("WEBHOOK_BASE_URL")
    def validate_webhook_url(cls, v: str, values: dict) -> str:
        """Validate and construct webhook URL."""
        if not v and values.get("ENVIRONMENT") == "production":
            raise ValueError("WEBHOOK_BASE_URL is required in production")
        
        # Remove trailing slash
        if v and v.endswith("/"):
            v = v[:-1]
            
        return v
    
    @validator("DATA_DIR", "LOG_DIR", "VECTOR_DB_PATH")
    def create_directories(cls, v: Path) -> Path:
        """Create directories if they don't exist."""
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"
    
    def get_webhook_url(self) -> str:
        """Get full webhook URL."""
        if not self.WEBHOOK_BASE_URL:
            raise ValueError("WEBHOOK_BASE_URL not configured")
        return f"{self.WEBHOOK_BASE_URL}/api/v1/webhook/telegram"
    
    def get_log_file_path(self, name: str = "app") -> Path:
        """Get log file path."""
        return self.LOG_DIR / f"{name}.log"


# Create global settings instance
settings = Settings()

# Export commonly used settings
DEBUG = settings.DEBUG
ENVIRONMENT = settings.ENVIRONMENT
DATABASE_URL = settings.DATABASE_URL