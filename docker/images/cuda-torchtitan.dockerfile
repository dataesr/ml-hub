# syntax=docker/dockerfile:1
FROM pytorch/pytorch:2.9.1-cuda12.8-cudnn9-devel

# System deps for TorchTitan
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clone TorchTitan
RUN git clone https://github.com/pytorch/torchtitan.git /opt/torchtitan

WORKDIR /opt/torchtitan

# Install TorchTitan deps + mlflow
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir mlflow

# Entrypoint
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

NGPU=${NGPU:-1}

echo "[entrypoint] Launching TorchTitan training with ${CONFIG_PATH} on ${NGPU} GPU(s)"

torchrun --standalone --nproc_per_node=${NGPU} \
  train.py --job.config_file "$CONFIG_PATH"
EOF

RUN chmod +x /entrypoint.sh

USER 42420:42420

WORKDIR /workspace
ENV HOME=/workspace
ENV HF_HOME=/workspace/.cache/huggingface

ENTRYPOINT ["/entrypoint.sh"]