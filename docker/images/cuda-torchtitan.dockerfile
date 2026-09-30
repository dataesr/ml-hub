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

# Create python virtual environment
RUN curl -LsSf https://astral.sh/uv/install.sh | UV_INSTALL_DIR=/usr/local/bin sh
ENV VIRTUAL_ENV=/opt/venv
RUN uv venv $VIRTUAL_ENV --python 3.12 --seed
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install TorchTitan
ARG TORCHTITAN_REF="f36852b60c8154718985f07d6778cb411c470516"
RUN git init /torchtitan \
 && git -C /torchtitan fetch --depth 1 https://github.com/dataesr/torchtitan.git ${TORCHTITAN_REF} \
 && git -C /torchtitan checkout FETCH_HEAD \
 && git -C /torchtitan rev-parse HEAD > /torchtitan.sha
RUN uv pip install --no-cache-dir -e /torchtitan

# Set HOME directory
WORKDIR /workspace
ENV HOME=/workspace

# Add generic entrypoint
COPY --chmod=755 docker/scripts/core-configs-run.sh /run.sh

# Allow OVH user
RUN chown 42420:42420 /workspace
USER 42420:42420