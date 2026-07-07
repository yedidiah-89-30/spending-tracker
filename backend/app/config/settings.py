from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Single source of truth for all environment-derived configuration.

    Kept in its own `config/` package (rather than inside `core/`) per the
    project's feature-based layout, so configuration is easy to find and
    has zero dependencies on the rest of the app.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Spending Tracker API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql+psycopg2://spendtracker:change-me@db:5432/spending_tracker"

    JWT_SECRET_KEY: str = "change-me-to-a-long-random-string"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached so the environment is parsed exactly once per process, and so
    `get_settings` can be used as a FastAPI dependency for DI in routes/services."""
    return Settings()
