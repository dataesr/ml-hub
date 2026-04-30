#!/usr/bin/env bash
set -euo pipefail

# export PATH="/workspace/.venv/bin:$PATH"

AI_CORE_BRANCH=${AI_CORE_BRANCH:-main}

echo "[runner] Installing ai_core (branch=${AI_CORE_BRANCH})..."

uv pip install --no-cache "git+https://github.com/dataesr/ml-hub.git@${AI_CORE_BRANCH}#subdirectory=libs"

echo "[runner] Running command: $@"

exec "$@"