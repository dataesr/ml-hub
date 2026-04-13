# syntax=docker/dockerfile:1
FROM axolotlai/axolotl:main-py3.11-cu128-2.9.1

# Install mlflow
RUN pip install --no-cache-dir mlflow

# Entry point script 
RUN cat <<'EOF' > /entrypoint.sh
#!/bin/bash
set -e

if [ -z "$CONFIG_FILE" ]; then
  echo "[entrypoint] ERROR: CONFIG_FILE environment variable is not set."
  exit 1
fi

CONFIG_PATH="./configs/${CONFIG_FILE}"

if [ ! -f "$CONFIG_PATH" ]; then
  echo "[entrypoint] ERROR: config file not found at ${CONFIG_PATH}"
  exit 1
fi

echo "[entrypoint] Launching training with ${CONFIG_PATH}"
accelerate launch -m axolotl.cli.train "$CONFIG_PATH"
EOF

RUN chmod +x /entrypoint.sh

# Give the OVHcloud user (42420:42420) access  
USER 42420:42420

# Create and set the HOME directory
WORKDIR /workspace
ENV HOME=/workspace
ENV HF_HOME=/workspace/.cache/huggingface
# Give the OVHcloud user (42420:42420) access to this directory
# RUN chown -R 42420:42420 /workspace

ENTRYPOINT ["/entrypoint.sh"]