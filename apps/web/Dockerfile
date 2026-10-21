# syntax=docker/dockerfile:1
# Build context: repository root.
# Runtime env: PUBLIC_LANDING_URL, PUBLIC_WEB_URL, PUBLIC_API_URL (see .env.example).

FROM node:24-alpine AS build
ENV PNPM_HOME=/pnpm PATH=/pnpm:$PATH CI=true
RUN corepack enable
WORKDIR /repo

COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm fetch

COPY . .
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --offline --frozen-lockfile --filter @appy/web...
# PUBLIC_* URLs are environment-specific, so the bundle gets Caddy placeholders
# and the real values are rendered at request time from the container env.
ENV PUBLIC_LANDING_URL='{{env `PUBLIC_LANDING_URL`}}' \
    PUBLIC_WEB_URL='{{env `PUBLIC_WEB_URL`}}' \
    PUBLIC_API_URL='{{env `PUBLIC_API_URL`}}'
RUN pnpm --filter @appy/web build

FROM caddy:2-alpine
COPY apps/web/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /repo/apps/web/dist /srv
COPY infra/caddy/env.js /srv/env.js
ENV XDG_CONFIG_HOME=/tmp/caddy/config XDG_DATA_HOME=/tmp/caddy/data
USER nobody
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
