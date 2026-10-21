# syntax=docker/dockerfile:1
# Build context: repository root.
# Runtime env: API_* (DSNs, CORS) and PUBLIC_*_URL of every app (see .env.example).
# The same image runs the API (default), migrations and the task worker:
#   docker run IMAGE                                    -> HTTP API on :8000
#   docker run IMAGE alembic upgrade head               -> apply migrations
#   docker run IMAGE taskiq worker appy_api.tasks.broker:broker appy_api.tasks.jobs

ARG PYTHON_VERSION=3.14

FROM ghcr.io/astral-sh/uv:0.13.3 AS uv

FROM python:${PYTHON_VERSION}-slim AS build
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /repo

# Dependencies first for layer caching. Every workspace member's pyproject must
# be present for uv to resolve the workspace: add new members here.
COPY pyproject.toml uv.lock ./
COPY apps/api/pyproject.toml apps/api/pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-workspace --package appy-api

COPY apps/api apps/api
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --package appy-api

FROM python:${PYTHON_VERSION}-slim
RUN groupadd --system --gid 10001 app && useradd --system --uid 10001 --gid app app
ENV PATH=/app/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY --from=build /app/.venv /app/.venv
COPY apps/api/alembic.ini ./alembic.ini
COPY apps/api/migrations ./migrations
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)"
CMD ["uvicorn", "--factory", "appy_api.main:create_app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*", "--no-server-header"]
