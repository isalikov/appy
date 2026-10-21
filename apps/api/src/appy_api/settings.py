from enum import StrEnum
from functools import lru_cache
from typing import Annotated

from pydantic import AnyHttpUrl, Field, MongoDsn, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Environment(StrEnum):
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """API configuration, read from `API_*` environment variables.

    Locally mise loads the root `.env`; in deployed environments the platform
    injects the variables. There are no defaults for connection strings on
    purpose: a missing DSN must fail at startup, not at the first request.
    """

    model_config = SettingsConfigDict(env_prefix="API_", extra="ignore", frozen=True)

    env: Environment = Field(default=Environment.LOCAL, validation_alias="APP_ENV")
    title: str = "Appy API"
    version: str = "0.1.0"
    log_level: str = "INFO"
    log_json: bool = True
    # Public URL of every app (shared PUBLIC_* variables, no API_ prefix).
    # Build redirects and links from these, never from hard-coded hosts:
    # e.g. the OAuth callback redirects to `public_web_url`.
    public_landing_url: AnyHttpUrl = Field(validation_alias="PUBLIC_LANDING_URL")
    public_web_url: AnyHttpUrl = Field(validation_alias="PUBLIC_WEB_URL")
    public_api_url: AnyHttpUrl = Field(validation_alias="PUBLIC_API_URL")

    # Comma-separated in the environment: API_CORS_ORIGINS=https://a.com,https://b.com
    cors_origins: Annotated[list[str], NoDecode] = []
    root_path: str = ""

    postgres_dsn: PostgresDsn
    postgres_pool_size: int = 10
    postgres_max_overflow: int = 10
    postgres_echo: bool = False

    mongo_dsn: MongoDsn
    mongo_db: str

    redis_dsn: RedisDsn
    tasks_redis_dsn: RedisDsn

    health_timeout_seconds: Annotated[float, Field(gt=0)] = 2.0

    docs_enabled: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()  # values come from the environment
