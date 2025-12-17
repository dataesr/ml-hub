#!/usr/bin/env bash
set -e

echo "🔧 Bootstrapping dev environment..."

# Create venv if missing
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo "✅ Virtualenv created"
fi

source .venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install ty
pip install -e ai_core
pip install -r app/backend/requirements.txt

echo "🎉 Dev environment ready!"
echo "➡️  Activate with: source .venv/bin/activate"
echo "➡️  Run type checks with: ty check"