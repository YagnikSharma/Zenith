"""Configuration settings for the Zenith Wellness Platform"""

import os
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # Application Settings
    APP_NAME: str = "Zenith Mental Wellness Platform"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-powered mental wellness platform for youth in India"
    APP_SECRET_KEY: str = os.getenv("APP_SECRET_KEY", "default-secret-key-change-in-production")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_DEBUG: bool = os.getenv("APP_DEBUG", "True").lower() == "true"
    
    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Firebase Configuration
    FIREBASE_SERVICE_ACCOUNT_KEY_PATH: Optional[str] = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
    FIREBASE_API_KEY: Optional[str] = os.getenv("FIREBASE_API_KEY")
    FIREBASE_AUTH_DOMAIN: Optional[str] = os.getenv("FIREBASE_AUTH_DOMAIN")
    FIREBASE_PROJECT_ID: Optional[str] = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_STORAGE_BUCKET: Optional[str] = os.getenv("FIREBASE_STORAGE_BUCKET")
    FIREBASE_MESSAGING_SENDER_ID: Optional[str] = os.getenv("FIREBASE_MESSAGING_SENDER_ID")
    FIREBASE_APP_ID: Optional[str] = os.getenv("FIREBASE_APP_ID")
    
    # Google AI Configuration
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GEMINI_CUSTOM_MODEL_ID: Optional[str] = os.getenv("GEMINI_CUSTOM_MODEL_ID")
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GOOGLE_CLOUD_PROJECT: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT")
    
    # Supported Languages
    SUPPORTED_LANGUAGES: list = [
        "en",  # English
        "hi",  # Hindi
        "bn",  # Bengali
        "te",  # Telugu
        "mr",  # Marathi
        "ta",  # Tamil
        "ur",  # Urdu
        "gu",  # Gujarati
        "kn",  # Kannada
        "ml",  # Malayalam
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS Settings
    CORS_ORIGINS: list = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",  # For development
    ]
    
    # JWT Settings
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Crisis Detection Settings
    CRISIS_KEYWORDS: list = [
        "suicide", "kill myself", "end my life", "want to die",
        "self harm", "hurt myself", "no reason to live",
        "better off dead", "can't go on", "worthless"
    ]
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Validate critical settings
def validate_settings():
    """Validate that critical settings are configured"""
    warnings = []
    
    if settings.APP_ENV == "production":
        if settings.APP_SECRET_KEY == "default-secret-key-change-in-production":
            warnings.append("APP_SECRET_KEY must be changed for production")
        
        if not settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH:
            warnings.append("Firebase service account key is required")
        
        if not settings.GOOGLE_API_KEY:
            warnings.append("Google API key is required")
            
        if not settings.GEMINI_CUSTOM_MODEL_ID:
            warnings.append("Gemini custom model ID is required")
    
    return warnings