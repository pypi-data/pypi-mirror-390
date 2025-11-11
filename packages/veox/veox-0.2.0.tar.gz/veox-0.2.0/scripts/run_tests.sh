#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f ".env" ]]; then
  # shellcheck disable=SC1090
  source ".env"
fi

python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest --maxfail=1 --disable-warnings -q

