# syntax=docker/dockerfile:1
FROM nvidia/cuda:12.8.1-cudnn-runtime-ubuntu24.04

WORKDIR /

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  curl \
  unzip \
  git \
  python3 \
  python3-dev \
  python3-pip \
  python3-venv \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Give the OVHcloud user (42420:42420) access  
USER 42420:42420

# Create and set the HOME directory
WORKDIR /workspace
ENV HOME=/workspace
# Give the OVHcloud user (42420:42420) access to this directory
# RUN chown -R 42420:42420 /workspace

# Create python virtual environment
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="$HOME/.local/bin/:$PATH"
RUN uv venv --python 3.12 --seed
ENV PATH="$HOME/.venv/bin:$PATH"

# Install PyTorch for cuda 12.8
RUN uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128 --trusted-host download.pytorch.org

# Install python packages (ML dependencies)
RUN uv pip install \
  bitsandbytes==0.47.0 \
  peft==0.17.1 \
  transformers==4.56.2 \
  trl==0.23.0 \
  unsloth==2025.11.1

# Clean cache
RUN uv cache clean

# Generic entrypoint: installs ai_core from git at boot
COPY --chown=42420:42420 docker/scripts/run.sh /run.sh
USER root
RUN chmod +x /run.sh
USER 42420:42420