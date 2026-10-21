#!/usr/bin/env bash
# Stops everything `mise run up` started and frees every app port.
# Data is kept: compose volumes are never removed here (use `mise run infra:reset`).
set -euo pipefail

cd "$(dirname "$0")/.."

echo "› stopping docker compose services"
docker compose down --remove-orphans

# Dev servers normally exit with Ctrl+C in `mise run up`; this catches
# leftovers (detached terminals, crashed parents) still holding the ports.
for var in LANDING_PORT WEB_PORT API_PORT; do
  port="${!var:-}"
  [[ -z "$port" ]] && continue
  pids="$(lsof -nP -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    echo "› freeing localhost:$port ($var): pid $(echo $pids | tr '\n' ' ')"
    kill $pids 2>/dev/null || true
    sleep 1
    still="$(lsof -nP -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)"
    [[ -n "$still" ]] && kill -9 $still 2>/dev/null || true
  fi
done

# The task worker has no port; stop it by its command line.
pkill -f "taskiq worker appy_api.tasks.broker:broker" 2>/dev/null || true

echo "✓ everything is down (database volumes kept)"
