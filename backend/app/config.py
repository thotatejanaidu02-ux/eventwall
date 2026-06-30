import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App Configuration
    APP_NAME: str = "EventWall"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "eventwall-project")
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-key.json")
    
    # API Keys
    REPLICATE_API_KEY: str = os.getenv("REPLICATE_API_KEY", "")
    GOOGLE_VERTEX_AI_API_KEY: str = os.getenv("GOOGLE_VERTEX_AI_API_KEY", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./eventwall.db")
    
    # Redis (for background tasks)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Join Code Configuration
    JOIN_CODE_LENGTH: int = 6
    JOIN_CODE_EXPIRATION_HOURS: int = 24
    
    # Wallpaper Configuration
    MIN_ROTATION_INTERVAL: int = 5  # minutes
    MAX_ROTATION_INTERVAL: int = 1440  # 24 hours
    DEFAULT_ROTATION_INTERVAL: int = 60  # 1 hour
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_IMAGE_FORMATS: list = ["jpg", "jpeg", "png", "webp"]
    
    # Background Tasks
    BACKGROUND_TASK_INTERVAL: int = 15  # minutes
    
    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
