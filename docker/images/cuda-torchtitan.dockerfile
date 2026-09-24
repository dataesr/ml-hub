# syntax=docker/dockerfile:1
FROM nvidia/cuda:13.0.3-cudnn-runtime-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Python + git
RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 \
  python3-dev \
  python3-pip \
  python3-venv \
  curl \
  zip \
  git \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create and set the HOME directory
WORKDIR /workspace
ENV HOME=/workspace

# Create python virtual environment
RUN curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/local/bin sh
RUN uv venv --python 3.12 --seed
ENV PATH="$HOME/.venv/bin:$PATH"

# # Install torchtitan + all deps using uv (faster than pip)
RUN uv pip install --no-cache-dir \
  "git+https://github.com/dataesr/torchtitan.git@main"

# Allow the runtime user to update the preinstalled virtualenv.
RUN chown -R 42420:42420 /workspace

# Generic entrypoint: installs core from git at boot
COPY --chown=42420:42420 docker/scripts/core-run.sh /run.sh
USER root
RUN chmod +x /run.sh
USER 42420:42420