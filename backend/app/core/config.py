from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_SECRET_KEY: str
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/clone_platform"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_URL: str = "http://localhost:8000"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 25 * 1024 * 1024  # 25MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
