"""
Configuration module for Loneliness Combat Engine.
Loads environment variables and provides app settings.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App Configuration
    app_name: str = "Loneliness Combat Engine"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # Database Configuration
    database_url: str = "sqlite:///./lce.db"
    database_echo: bool = False

    # Security & Auth
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://127.0.0.1:8000/api/v1/auth/google/callback"  # Backend callback URL

    # Google AI / Gemini
    google_api_key: str = ""
    gemini_model_flash: str = "gemini-2.5-flash"
    gemini_model_pro: str = "gemini-2.5-pro"

    # External APIs
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    spotify_redirect_uri: str = "http://127.0.0.1:8000/api/v1/auth/spotify/callback"  # Backend callback URL

    github_token: str = ""

    meetup_api_key: str = ""
    eventbrite_token: str = ""

    weather_api_key: str = ""

    # Risk Scoring Configuration
    baseline_period_days: int = 14
    risk_score_low_threshold: int = 25
    risk_score_moderate_threshold: int = 50
    risk_score_elevated_threshold: int = 75

    # CORS Configuration (comma-separated string from .env)
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to create a singleton pattern.
    """
    return Settings()
