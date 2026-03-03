"""Application configuration via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./metamemory.db"
    ENABLE_MEMORY_CONSTRUCTION: bool = True
    ENABLE_EVOLUTION: bool = True
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    PII_DETECTION_ENABLED: bool = True
    MAX_IMPORT_BYTES: int = 5_000_000
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 240

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
