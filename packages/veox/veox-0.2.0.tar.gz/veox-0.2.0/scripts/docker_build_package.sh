#!/usr/bin/env bash
# Build source and wheel distributions inside a container with logging.
set -euo pipefail

log() {
  printf '[veox][docker-build] %s\n' "$*" >&2
}

select_runtime() {
  if command -v podman >/dev/null 2>&1; then
    echo "podman"
  elif command -v docker >/dev/null 2>&1; then
    echo "docker"
  else
    log "ERROR: neither podman nor docker is available"
    return 1
  fi
}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${IMAGE:-python:3.11-slim}"
RUNTIME="$(select_runtime)"

log "using runtime: $RUNTIME"
log "working directory: $ROOT_DIR"
log "container image: $IMAGE"

ENV_FLAGS=(
  "--env" "PIP_DISABLE_PIP_VERSION_CHECK=1"
  "--env" "PIP_NO_CACHE_DIR=1"
)

VOLUME_FLAGS=(
  "-v" "${ROOT_DIR}:/workspace:Z"
)

ENTRYPOINT_CMD=$'set -euo pipefail\n'
ENTRYPOINT_CMD+=$'python -m pip install --upgrade pip\n'
ENTRYPOINT_CMD+=$'pip install build\n'
ENTRYPOINT_CMD+=$'python -m build\n'

log "starting containerized build..."
"$RUNTIME" run --rm "${ENV_FLAGS[@]}" "${VOLUME_FLAGS[@]}" -w /workspace "$IMAGE" bash -c "$ENTRYPOINT_CMD"
log "build artifacts available under dist/"

