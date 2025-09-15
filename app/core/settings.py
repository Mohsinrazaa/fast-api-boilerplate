from functools import lru_cache
from typing import List, Optional
from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)
    # App
    ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    APP_NAME: str = Field(default="FastAPI Boilerplate")

    # CORS
    CORS_ALLOW_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_HEADERS: List[str] = Field(default_factory=lambda: ["*"])

    # Security / Auth
    SECRET_KEY: str = Field(default="change-me")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24)  # 24h
    JWT_ALGORITHM: str = Field(default="HS256")

    # Database
    DATABASE_URL: Optional[AnyUrl] = None

    # External
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    return Settings()


