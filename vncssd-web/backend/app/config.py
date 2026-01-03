"""
VNCSSDetector Web Service - Configuration
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "mysql+aiomysql://vncssd:password@localhost:3306/vncssd_web"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT Settings
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Server Settings
    debug: bool = False
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # File Storage
    recordings_path: str = "/var/lib/vncssd/recordings"
    max_upload_size_mb: int = 500
    
    # Logging
    log_level: str = "INFO"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
