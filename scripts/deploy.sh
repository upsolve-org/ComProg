#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/srv/comprog"
CONTAINER="comprog-web"
IMAGE="node:24-alpine"
TARGET_REF="${1:-origin/feat/course-site}"

echo "==> Deploying ComProg (${TARGET_REF}) in ${APP_DIR}"

OLD_LOCK_HASH=""
if [ -f "${APP_DIR}/package-lock.json" ]; then
  OLD_LOCK_HASH="$(sha256sum "${APP_DIR}/package-lock.json" | awk '{print $1}')"
fi

git -C "${APP_DIR}" fetch --prune origin
git -C "${APP_DIR}" reset --hard "${TARGET_REF}"

NEW_LOCK_HASH="$(sha256sum "${APP_DIR}/package-lock.json" | awk '{print $1}')"

if [ ! -d "${APP_DIR}/node_modules" ] || [ "${OLD_LOCK_HASH}" != "${NEW_LOCK_HASH}" ]; then
  echo "==> package-lock.json changed â€” running npm ci"
  docker run --rm -v "${APP_DIR}:/app" -w /app "${IMAGE}" npm ci --no-audit --no-fund
else
  echo "==> Dependencies unchanged â€” skipping npm ci"
fi

echo "==> Building dist/ bundle"
docker run --rm -v "${APP_DIR}:/app" -w /app "${IMAGE}" npm run build

mkdir -p "${APP_DIR}/data"
chmod 775 "${APP_DIR}/data"

# Ensure container has writable /app/data bind mount for leaderboard persistence
HAS_DATA_MOUNT="$(docker inspect "${CONTAINER}" --format '{{range .Mounts}}{{.Destination}} {{end}}' 2>/dev/null || true)"
if [[ "${HAS_DATA_MOUNT}" == *"/app/data"* ]]; then
  echo "==> Restarting ${CONTAINER}"
  docker restart "${CONTAINER}"
else
  echo "==> Recreating ${CONTAINER} with persistent /app/data mount"
  docker rm -f "${CONTAINER}" >/dev/null 2>&1 || true
  ENV_FLAG=()
  if [ -f "${APP_DIR}/.env" ]; then
    ENV_FLAG=(--env-file "${APP_DIR}/.env")
  fi
  docker run -d \
    --name "${CONTAINER}" \
    --restart unless-stopped \
    -p 127.0.0.1:8790:3000 \
    -e HOST=0.0.0.0 \
    -e PORT=3000 \
    "${ENV_FLAG[@]}" \
    -v "${APP_DIR}:/app:ro" \
    -v "${APP_DIR}/data:/app/data:rw" \
    -w /app \
    "${IMAGE}" \
    node site/server.mjs
fi

echo "==> Running local health checks on 127.0.0.1:8790"
for attempt in $(seq 1 15); do
  if curl -fsS http://127.0.0.1:8790/ >/dev/null && curl -fsS http://127.0.0.1:8790/api/codeforces/leaderboard >/dev/null; then
    echo "==> Deploy healthy on attempt ${attempt}!"
    exit 0
  fi
  sleep 1
done

echo "ERROR: ${CONTAINER} failed health check!" >&2
docker logs --tail 30 "${CONTAINER}" >&2 || true
exit 1
