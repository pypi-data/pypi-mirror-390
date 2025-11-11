#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f ".env" ]]; then
  # shellcheck disable=SC1090
  source ".env"
fi

: "${TWINE_USERNAME:?TWINE_USERNAME must be set (e.g. __token__)}"
: "${TWINE_PASSWORD:?TWINE_PASSWORD must be set (project-scoped token)}"

python -m pip install --upgrade pip
pip install build twine
python -m build
twine upload dist/*

