import os
from typing import Literal
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env manually
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Path ke direktori `config.py`
ENV_PATH = os.path.join(BASE_DIR, "..", "..", ".env")  # Sesuaikan jika path beda
load_dotenv(ENV_PATH)

# print(f"Trying to load .env from: {ENV_PATH}")  # Debugging path .env
# print(f"Loaded from dotenv: {os.getenv('DATABASE_URL')}")  # Debugging apakah DATABASE_URL terbaca

class Settings(BaseSettings):
    # Application Settings
    PROJECT_NAME: str = "ARGA-SSO-SERVICE"
    ENVIRONMENT: Literal["development", "production", "test"] = "development"
    DEBUG: bool = True

    # CORS Settings
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    
    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str
    
    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: Literal["HS256", "HS512", "RS256"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OAuth2
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()

# Debugging apakah nilai dari DATABASE_URL terbaca oleh Pydantic Settings
print(f"Loaded DATABASE_URL from Pydantic: {settings.DATABASE_URL}")
print(f"Loaded GOOGLE_CLIENT_ID from Pydantic: {settings.GOOGLE_CLIENT_ID}")
print(f"Loaded GOOGLE_CLIENT_SECRET from Pydantic: {settings.GOOGLE_CLIENT_SECRET}")
