#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/dataesr/ml-hub.git"
CORE_BRANCH=${CORE_BRANCH:-main}
CONFIGS_DIR="/workspace/configs"
TMP_DIR=$(mktemp -d)

echo "[runner] Installing core (branch=${CORE_BRANCH})..."
uv pip install --no-cache "git+${REPO_URL}@${CORE_BRANCH}#subdirectory=core"

echo "[runner] Fetching configs folder (branch=${CORE_BRANCH})..."
git clone --quiet --depth 1 --branch "${core_BRANCH}" --filter=blob:none --sparse \
  "$REPO_URL" "$TMP_DIR"
git -C "$TMP_DIR" sparse-checkout set configs
rm -rf "$CONFIGS_DIR"
cp -r "$TMP_DIR/configs" "$CONFIGS_DIR"
rm -rf "$TMP_DIR"
export PYTHONPATH="$CONFIGS_DIR:${PYTHONPATH:-}"

echo "[runner] Running command: $*"

exec "$@"