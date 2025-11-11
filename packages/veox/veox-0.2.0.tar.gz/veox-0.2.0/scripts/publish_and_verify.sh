#!/usr/bin/env bash
# Build, publish to PyPI, wait for propagation, and verify install.
set -euo pipefail

LOG_PREFIX="[veox][release]"

log() {
  printf '%s %s\n' "$LOG_PREFIX" "$*" >&2
}

abort() {
  log "ERROR: $*"
  exit 1
}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f ".env" ]]; then
  # shellcheck disable=SC1090
  source ".env"
  log "loaded environment variables from .env"
fi

: "${TWINE_USERNAME:?TWINE_USERNAME is required (set to __token__ for PyPI tokens)}"
: "${TWINE_PASSWORD:?TWINE_PASSWORD is required}"

PYPI_REPOSITORY="${PYPI_REPOSITORY:-pypi}"
PYPI_WAIT_SECONDS="${PYPI_WAIT_SECONDS:-180}"
VERIFY_VENV=".release_venv"

log "release configuration:"
log "  repository      : ${PYPI_REPOSITORY}"
log "  wait seconds    : ${PYPI_WAIT_SECONDS}"
log "  verify venv     : ${VERIFY_VENV}"

python3 -m pip install --upgrade pip >/dev/null
python3 -m pip install build twine >/dev/null

log "cleaning previous build artifacts..."
rm -rf dist/

log "building distribution..."
python3 -m build

log "publishing artifacts via twine..."
declare -a TWINE_ARGS=()
if [[ "${PYPI_REPOSITORY}" != "pypi" ]]; then
  TWINE_ARGS+=(--repository "${PYPI_REPOSITORY}")
fi
if [[ ${#TWINE_ARGS[@]} -gt 0 ]]; then
  twine upload "${TWINE_ARGS[@]}" dist/*
else
  twine upload dist/*
fi

log "publish complete, sleeping ${PYPI_WAIT_SECONDS}s for index propagation..."
sleep "${PYPI_WAIT_SECONDS}"

log "preparing fresh verification environment..."
rm -rf "${VERIFY_VENV}"
python3 -m venv "${VERIFY_VENV}"
# shellcheck disable=SC1091
source "${VERIFY_VENV}/bin/activate"

pip install --upgrade pip >/dev/null

PACKAGE_VERSION="$(python -c 'import importlib.metadata as m; print(m.version("veox"))' 2>/dev/null || true)"
if [[ -n "$PACKAGE_VERSION" ]]; then
  log "INFO: veox appears installed in verification venv unexpectedly (version=$PACKAGE_VERSION); removing..."
  pip uninstall -y veox >/dev/null || true
fi

VERSION="$(python - <<'PY'
from pathlib import Path
import re

init_path = Path("src/veox/__init__.py").read_text(encoding="utf-8")
match = re.search(r'__version__\s*=\s*"([^"]+)"', init_path)
if not match:
    raise SystemExit("Unable to find __version__ in src/veox/__init__.py")
print(match.group(1))
PY
)"

log "installing veox==${VERSION} from ${PYPI_REPOSITORY}..."
pip install "veox==${VERSION}"

log "verifying import and status..."
python - <<'PY'
from veox import Veox, __version__
model = Veox()
print(f"veox.__version__={__version__}")
print("status() ->", model.status())
PY

log "release verification succeeded."

