"""
Configuration settings for MedObsMind backend.
Uses pydantic-settings for environment variable management.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "MedObsMind"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://medobsmind:password@localhost/medobsmind"
    DATABASE_ECHO: bool = False  # SQL query logging
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Web landing page
        "http://localhost:19006", # React Native dev
    ]
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # Medical Safety Settings
    REQUIRE_DOCTOR_CONFIRMATION: bool = True
    AUDIT_LOG_ENABLED: bool = True
    
    # Alert Thresholds (NEWS2 defaults)
    NEWS2_LOW_RISK_THRESHOLD: int = 0
    NEWS2_MEDIUM_RISK_THRESHOLD: int = 5
    NEWS2_HIGH_RISK_THRESHOLD: int = 7
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
