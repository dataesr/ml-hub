#!/usr/bin/env bash
set -euo pipefail

# export PATH="/workspace/.venv/bin:$PATH"

core_BRANCH=${core_BRANCH:-main}

echo "[runner] Installing core (branch=${core_BRANCH})..."

uv pip install --no-cache "git+https://github.com/dataesr/ml-hub.git@${core_BRANCH}#subdirectory=core"

echo "[runner] Running command: $@"

exec "$@"