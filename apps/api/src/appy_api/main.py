from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from appy_api.api.routes import health
from appy_api.logging import configure_logging
from appy_api.resources import Resources
from appy_api.settings import Settings, get_settings

log = structlog.get_logger(__name__)


def _operation_id(route: APIRoute) -> str:
    # Stable, readable operation ids give the generated TS client clean names.
    return f"{route.tags[0]}_{route.name}" if route.tags else route.name


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    resources = Resources.create(settings)
    app.state.resources = resources
    log.info("api_started", env=settings.env, version=settings.version)
    try:
        yield
    finally:
        await resources.close()
        log.info("api_stopped")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Application factory: `uvicorn --factory appy_api.main:create_app`."""
    settings = settings or get_settings()
    configure_logging(settings.log_level, json=settings.log_json)

    app = FastAPI(
        title=settings.title,
        version=settings.version,
        root_path=settings.root_path,
        lifespan=lifespan,
        generate_unique_id_function=_operation_id,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )
    app.state.settings = settings

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(health.router)
    return app
