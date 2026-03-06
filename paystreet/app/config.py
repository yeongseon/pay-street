"""Application configuration using pydantic-settings."""

# pyright: reportMissingImports=false
from functools import lru_cache
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = (
        "postgresql+asyncpg://paystreet:paystreet@localhost:5432/paystreet"
    )

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"

    # AI Providers
    openai_api_key: str = ""
    elevenlabs_api_key: str = ""
    llm_provider: str = "mock"  # "openai" | "mock"
    tts_provider: str = "mock"  # "openai" | "elevenlabs" | "mock"

    # LLM settings
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1024

    # App
    env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Video output
    output_dir: str = "paystreet/outputs"
    export_dir: str = "paystreet/exports"
    temp_dir: str = "paystreet/temp"
    assets_dir: str = "paystreet/assets"
    templates_dir: str = "paystreet/templates"


@lru_cache
def get_settings() -> Settings:
    return Settings()
