import pytest
from httpx import ASGITransport, AsyncClient

from appy_api.main import create_app
from appy_api.settings import Settings

pytestmark = pytest.mark.integration


async def test_health_against_real_services(integration_settings: Settings) -> None:
    app = create_app(integration_settings)

    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        response = await client.get("/health")

    assert response.status_code == 200, response.text
    assert {name: check["status"] for name, check in response.json()["checks"].items()} == {
        "postgres": "ok",
        "mongo": "ok",
        "redis": "ok",
    }
