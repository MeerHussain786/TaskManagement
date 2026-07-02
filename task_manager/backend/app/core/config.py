"""
Application Configuration Module.

Centralizes all application configuration using Pydantic Settings.
Supports environment variables, .env files, and sensible defaults.
Configuration is validated at startup — fail fast on misconfiguration.
"""

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Application environment enumeration."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Supports .env file loading with validation. All sensitive values
    must be provided via environment variables in production.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────
    APP_NAME: str = "TaskManager"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # ── Server ───────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"  # noqa: S104
    PORT: int = 8000
    WORKERS: int = 1

    # ── Database ─────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./task_manager.db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False

    # ── Redis ────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""
    CACHE_TTL_SECONDS: int = 300
    CACHE_ENABLED: bool = True

    # ── JWT Authentication ───────────────────────────────────────────────
    JWT_SECRET_KEY: str = Field(
        default="INSECURE-DEV-KEY-CHANGE-IN-PRODUCTION",
        min_length=32,
        description="JWT signing secret. Must be at least 32 characters.",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Security ─────────────────────────────────────────────────────────
    FRONTEND_PORT: int = 3000
    ALLOWED_ORIGINS: str | list[str] = ["http://localhost:3000", "http://localhost:8000"]

    RATE_LIMIT_LOGIN: int = 5
    RATE_LIMIT_REGISTER: int = 20
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    BCRYPT_ROUNDS: int = 12

    # ── Observability ────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    OTLP_ENDPOINT: str = "http://localhost:4317"
    ENABLE_TRACING: bool = False
    ENABLE_METRICS: bool = True

    # ── Sentry ───────────────────────────────────────────────────────────
    SENTRY_DSN: str = ""

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse comma-separated CORS origins string into list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid_levels:
            msg = f"Invalid log level: {v}. Must be one of {valid_levels}"
            raise ValueError(msg)
        return upper

    @model_validator(mode="after")
    def add_frontend_port_origin(self) -> "Settings":
        """Add frontend port origin to allowed origins if not present."""
        origins = self.ALLOWED_ORIGINS
        if isinstance(origins, str):
            origins = [origin.strip() for origin in origins.split(",") if origin.strip()]
        elif isinstance(origins, list):
            origins = list(origins)
        else:
            origins = []

        frontend_origin = f"http://localhost:{self.FRONTEND_PORT}"
        frontend_origin_ip = f"http://127.0.0.1:{self.FRONTEND_PORT}"

        if frontend_origin not in origins:
            origins.append(frontend_origin)
        if frontend_origin_ip not in origins:
            origins.append(frontend_origin_ip)

        self.ALLOWED_ORIGINS = origins
        return self

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Enforce stricter validation in production."""
        if self.ENVIRONMENT == Environment.PRODUCTION:
            if "INSECURE" in self.JWT_SECRET_KEY or "CHANGE" in self.JWT_SECRET_KEY:
                msg = "JWT_SECRET_KEY must be changed from default in production"
                raise ValueError(msg)
            if self.DEBUG:
                msg = "DEBUG must be disabled in production"
                raise ValueError(msg)
            if self.DB_ECHO:
                msg = "DB_ECHO must be disabled in production"
                raise ValueError(msg)
        return self

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.ENVIRONMENT == Environment.TESTING

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return "sqlite" in self.DATABASE_URL

    @property
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).resolve().parent.parent.parent


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get cached application settings singleton.

    Uses lru_cache to ensure settings are loaded once and reused.
    Call get_settings.cache_clear() to reload in tests.
    """
    return Settings()
