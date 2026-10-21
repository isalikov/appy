from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from appy_api.api.deps import get_probes
from appy_api.main import create_app
from appy_api.resources import Probe
from appy_api.settings import Settings


async def _ok() -> None:
    return None


async def _fail() -> None:
    raise ConnectionError


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    return create_app(settings)


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    # ASGITransport does not run the lifespan, so no real connections are made.
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


def _use_probes(app: FastAPI, probes: dict[str, Probe]) -> None:
    app.dependency_overrides[get_probes] = lambda: probes


async def test_health_ok(app: FastAPI, client: AsyncClient) -> None:
    _use_probes(app, {"postgres": _ok, "mongo": _ok, "redis": _ok})

    response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert set(body["checks"]) == {"postgres", "mongo", "redis"}


async def test_health_reports_failed_dependency(app: FastAPI, client: AsyncClient) -> None:
    _use_probes(app, {"postgres": _ok, "mongo": _fail, "redis": _ok})

    response = await client.get("/health")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "error"
    assert body["checks"]["mongo"] == {
        "status": "error",
        "latency_ms": body["checks"]["mongo"]["latency_ms"],
        "error": "ConnectionError",
    }


def test_openapi_exposes_health(app: FastAPI) -> None:
    schema = app.openapi()

    assert schema["paths"]["/health"]["get"]["operationId"] == "health_health"
