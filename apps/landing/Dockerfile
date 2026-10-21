# syntax=docker/dockerfile:1
# Build context: repository root.
# Runtime env: PUBLIC_LANDING_URL, PUBLIC_WEB_URL, PUBLIC_API_URL (see .env.example).

# The build output is static and architecture-independent: build on the host's
# native platform, never under emulation (e.g. `--platform linux/amd64` on an
# Apple Silicon Mac). Only the final Caddy stage is per-platform.
FROM --platform=$BUILDPLATFORM node:24-alpine AS build
ENV PNPM_HOME=/pnpm PATH=/pnpm:$PATH CI=true
RUN corepack enable
WORKDIR /repo

COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm fetch

COPY . .
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --offline --frozen-lockfile --filter @appy/landing...
# PUBLIC_* URLs are environment-specific, so the bundle gets Caddy placeholders
# and the real values are rendered at request time from the container env.
ENV PUBLIC_LANDING_URL='{{env `PUBLIC_LANDING_URL`}}' \
    PUBLIC_WEB_URL='{{env `PUBLIC_WEB_URL`}}' \
    PUBLIC_API_URL='{{env `PUBLIC_API_URL`}}'
RUN pnpm --filter @appy/landing build

FROM caddy:2-alpine
COPY apps/landing/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /repo/apps/landing/dist /srv
COPY infra/caddy/env.js /srv/env.js
ENV XDG_CONFIG_HOME=/tmp/caddy/config XDG_DATA_HOME=/tmp/caddy/data
USER nobody
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
