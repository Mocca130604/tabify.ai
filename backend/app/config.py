"""Configuration settings for Tabify.ai backend."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment or defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["*"]
    MAX_UPLOAD_SIZE_MB: int = 10

    # TabPFN hardware target: 'auto', 'cpu', 'cuda', 'mps'
    TABPFN_DEVICE: str = "auto"
    TABPFN_MODEL_CACHE_DIR: str | None = None
    TABPFN_TOKEN: str | None = None
    TABPFN_NO_BROWSER: str = "1"

    # TabPFN context bounds
    MAX_RECOMMENDED_SAMPLES: int = 5000
    MAX_CPU_SAMPLES: int = 1500
    MAX_RECOMMENDED_FEATURES: int = 500


settings = Settings()
