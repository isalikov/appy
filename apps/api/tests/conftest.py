import os

import pytest

from appy_api.settings import Settings


def _settings(**values: str) -> Settings:
    # model_validate goes through the same coercion as the environment does.
    return Settings.model_validate(
        {
            "APP_ENV": "test",
            "log_json": False,
            "PUBLIC_LANDING_URL": "http://localhost:5174",
            "PUBLIC_WEB_URL": "http://localhost:5173",
            "PUBLIC_API_URL": "http://localhost:8000",
            **values,
        }
    )


@pytest.fixture
def settings() -> Settings:
    """Settings that never touch real services; unit tests override probes."""
    return _settings(
        postgres_dsn="postgresql+asyncpg://test:test@localhost:5432/test",
        mongo_dsn="mongodb://localhost:27017",
        mongo_db="test",
        redis_dsn="redis://localhost:6379/15",
        tasks_redis_dsn="redis://localhost:6379/15",
    )


@pytest.fixture
def integration_settings() -> Settings:
    """Settings pointing at the services from `mise run infra:up`."""
    names = ("API_TEST_POSTGRES_DSN", "API_MONGO_DSN", "API_TEST_MONGO_DB", "API_TEST_REDIS_DSN")
    if missing := [name for name in names if not os.environ.get(name)]:
        pytest.skip(f"integration env not configured: {', '.join(missing)}")
    return _settings(
        postgres_dsn=os.environ["API_TEST_POSTGRES_DSN"],
        mongo_dsn=os.environ["API_MONGO_DSN"],
        mongo_db=os.environ["API_TEST_MONGO_DB"],
        redis_dsn=os.environ["API_TEST_REDIS_DSN"],
        tasks_redis_dsn=os.environ["API_TEST_REDIS_DSN"],
    )
