#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="obs-platform"

# Resolve project root based on this script's location:
# bin/run_local.sh -> project root is one directory up.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_CMD=(docker compose -f "${ROOT_DIR}/docker-compose.yml")

cd "${ROOT_DIR}"

echo "=== [$PROJECT_NAME] Starting local stack from ${ROOT_DIR} ==="

# 1. Optional: load environment files if present.
# Supports both root files (.env/.env.local) and a dedicated .env folder.
load_env_file() {
  local env_file="$1"
  if [ -f "${env_file}" ]; then
    echo "Loading environment from ${env_file#${ROOT_DIR}/}"
    set -a
    # shellcheck disable=SC1090
    . "${env_file}"
    set +a
  fi
}

load_env_file "${ROOT_DIR}/.env"
load_env_file "${ROOT_DIR}/.env/.env"
load_env_file "${ROOT_DIR}/.env.local"
load_env_file "${ROOT_DIR}/.env/.env.local"

# docker-compose.yml requires backend/.env to exist. Create it if missing.
BACKEND_ENV_FILE="${ROOT_DIR}/backend/.env"
if [ ! -f "${BACKEND_ENV_FILE}" ]; then
  BACKEND_ENV_SOURCE=""
  for candidate in \
    "${ROOT_DIR}/.env/.env.local" \
    "${ROOT_DIR}/.env.local" \
    "${ROOT_DIR}/.env/.env" \
    "${ROOT_DIR}/.env"; do
    if [ -f "${candidate}" ]; then
      BACKEND_ENV_SOURCE="${candidate}"
      break
    fi
  done

  if [ -n "${BACKEND_ENV_SOURCE}" ]; then
    cp "${BACKEND_ENV_SOURCE}" "${BACKEND_ENV_FILE}"
    echo "Created backend/.env from ${BACKEND_ENV_SOURCE#${ROOT_DIR}/}"
  else
    : > "${BACKEND_ENV_FILE}"
    echo "Created empty backend/.env (no env source files found)."
  fi
fi

echo "=== Step 1: Building images and starting containers ==="
"${COMPOSE_CMD[@]}" up -d --build

echo "=== Step 2: Waiting for Postgres to become ready ==="
# Service name "db" must match your docker-compose.yml
MAX_RETRIES=30
SLEEP_SECONDS=2
COUNTER=0

until "${COMPOSE_CMD[@]}" exec -T db pg_isready -U "${POSTGRES_USER:-obs_user}" >/dev/null 2>&1; do
  COUNTER=$((COUNTER + 1))
  if [ "$COUNTER" -ge "$MAX_RETRIES" ]; then
    echo "Postgres did not become ready in time. Aborting."
    exit 1
  fi
  echo "Postgres not ready yet... retrying ($COUNTER/$MAX_RETRIES)"
  sleep "$SLEEP_SECONDS"
done

echo "Postgres is ready."

echo "=== Step 3: Applying Django migrations ==="
# "backend" must match the Django service name in docker-compose.yml
"${COMPOSE_CMD[@]}" exec -T backend python manage.py migrate --noinput

echo "=== Step 4: Collecting static files ==="
"${COMPOSE_CMD[@]}" exec -T backend python manage.py collectstatic --noinput || {
  echo "collectstatic failed (maybe not configured yet). Continuing..."
}

echo "=== Step 5: Optional Django superuser creation ==="
# If you set these (in .env/.env.local), we'll try to create a superuser:
#   DJANGO_SUPERUSER_USERNAME
#   DJANGO_SUPERUSER_EMAIL
#   DJANGO_SUPERUSER_PASSWORD
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] &&
  [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] &&
  [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  echo "Creating Django superuser '${DJANGO_SUPERUSER_USERNAME}' (if it does not already exist)..."
  "${COMPOSE_CMD[@]}" exec -T \
    -e DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME}" \
    -e DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL}" \
    -e DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD}" \
    backend \
    python manage.py createsuperuser \
    --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "$DJANGO_SUPERUSER_EMAIL" || {
    echo "Superuser may already exist. Skipping error."
  }
else
  echo "No superuser env vars set; skipping superuser creation."
fi

echo "=== Step 6: Showing container status ==="
"${COMPOSE_CMD[@]}" ps

echo "=== [$PROJECT_NAME] Local stack is up and initialized. ==="
echo "Backend: http://localhost:8000"
