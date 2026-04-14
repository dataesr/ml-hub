#!/bin/bash
# Generic entrypoint for ai-hub Docker images
# Installs ai_core from git at runtime so images don't need rebuilding on code changes
set -e

AI_CORE_BRANCH=${AI_CORE_BRANCH:-main}
echo "[entrypoint] Installing ai_core from git (branch=${AI_CORE_BRANCH})..."
pip install --no-deps --quiet "git+https://github.com/dataesr/ml-hub.git@${AI_CORE_BRANCH}#subdirectory=libs" 2>/dev/null \
  || echo "[entrypoint] WARNING: Failed to install ai_core from git, using pre-installed version if available"

exec "$@"
