from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]

DEFAULT_JWT_SECRET = "dev-secret-replace-with-32-plus-char-key-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "postgresql+psycopg://postgres:changeme@localhost:5432/chefconnect"

    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str = DEFAULT_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_AUTH_MAX_REQUESTS: int = 5
    RATE_LIMIT_BOOKINGS_MAX_REQUESTS: int = 10
    RATE_LIMIT_CHEFS_MAX_REQUESTS: int = 60

    CHEFS_CACHE_TTL_SECONDS: int = 60

    N8N_BOOKING_CONFIRMED_WEBHOOK_URL: str = ""
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "onboarding@resend.dev"

    @model_validator(mode="after")
    def reject_insecure_production_secrets(self) -> "Settings":
        if self.ENVIRONMENT == "production":
            if self.JWT_SECRET_KEY == DEFAULT_JWT_SECRET:
                raise ValueError(
                    "JWT_SECRET_KEY must be set from the environment in production; "
                    "the development default is not allowed"
                )
            if len(self.JWT_SECRET_KEY) < 32:
                raise ValueError("JWT_SECRET_KEY must be at least 32 characters in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
