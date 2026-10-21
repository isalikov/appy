#!/usr/bin/env bash
# Prints what `mise run up` started and where, once every app listens on its
# port. Runs in parallel with the apps; never fails the stack (always exit 0).
set -uo pipefail

cd "$(dirname "$0")/.."

TIMEOUT="${UP_SUMMARY_TIMEOUT:-90}"

listening() {
  lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

wait_for_port() {
  local port="$1" waited=0
  until listening "$port"; do
    ((waited >= TIMEOUT)) && return 1
    sleep 1
    ((waited++))
  done
}

row() {
  printf '  %-2s %-10s %-34s %s\n' "$1" "$2" "$3" "$4"
}

# name | port variable | url variable | url suffix
apps=(
  "api|API_PORT|PUBLIC_API_URL|/docs"
  "web|WEB_PORT|PUBLIC_WEB_URL|"
  "landing|LANDING_PORT|PUBLIC_LANDING_URL|"
)

status=()
for entry in "${apps[@]}"; do
  IFS='|' read -r _ port_var _ _ <<<"$entry"
  if wait_for_port "${!port_var:-0}"; then status+=("✓"); else status+=("✗"); fi
done

api_health="unknown"
if [[ -n "${PUBLIC_API_URL:-}" ]]; then
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 "${PUBLIC_API_URL}/health" || true)"
  case "$code" in
    200) api_health="healthy" ;;
    503) api_health="degraded (see /health)" ;;
    *) api_health="no response" ;;
  esac
fi

worker="✗"
pgrep -f "taskiq worker appy_api.tasks.broker:broker" >/dev/null 2>&1 && worker="✓"

infra_status() {
  local state
  state="$(docker compose ps --format '{{.Health}}' "$1" 2>/dev/null | head -n1)"
  [[ "$state" == "healthy" ]] && echo "✓" || echo "✗"
}

echo
echo "  ─── appy is up ──────────────────────────────────────────────"
echo "  apps"
i=0
for entry in "${apps[@]}"; do
  IFS='|' read -r name port_var url_var suffix <<<"$entry"
  url="${!url_var:-http://localhost:${!port_var:-?}}${suffix}"
  note="localhost:${!port_var:-?}"
  [[ "$name" == "api" ]] && note="$note · $api_health"
  row "${status[$i]}" "$name" "$url" "$note"
  ((i++))
done
row "$worker" "worker" "taskiq" "no port · API_TASKS_REDIS_DSN"
echo "  infrastructure (docker)"
row "$(infra_status postgres)" "postgres" "localhost:${POSTGRES_PORT:-5432}" "db ${POSTGRES_DB:-appy}, pgvector"
row "$(infra_status mongo)" "mongo" "localhost:${MONGO_PORT:-27017}" "db ${API_MONGO_DB:-appy}"
row "$(infra_status redis)" "redis" "localhost:${REDIS_PORT:-6379}" "sessions, cache, queues"
echo "  ─────────────────────────────────────────────────────────────"
echo "  Ctrl+C stops the apps · \`mise run down\` stops docker (data is kept)"
echo

exit 0
