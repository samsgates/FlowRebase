from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    app_secret: str = "dev-secret-change-me"
    database_url: str = "sqlite+aiosqlite:///./flowrebase.db"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] | str = ["http://localhost:3000"]

    auth_mode: Literal["dev", "oidc"] = "dev"
    dev_user_id: str = "local-admin"
    dev_user_email: str = "admin@flowrebase.local"
    oidc_issuer: str | None = None
    oidc_audience: str | None = None

    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    opa_url: str | None = None

    temporal_enabled: bool = False
    temporal_address: str = "localhost:7233"
    temporal_namespace: str = "default"

    otel_exporter_otlp_endpoint: str | None = None

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value):
        if isinstance(value, str):
            return [x.strip() for x in value.split(",") if x.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
