# syntax=docker/dockerfile:1.4
FROM python:3.12-slim

LABEL maintainer="wasm-kit"
LABEL description="Python WebAssembly builder - auto-installs tools based on project requirements"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install componentize-py and wasmtime globally with BuildKit caching
# These will be available system-wide for all projects
# If projects need specific versions, they can be installed via requirements.txt
# The cache mount speeds up pip installs on subsequent builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir componentize-py wasmtime

WORKDIR /src
CMD ["componentize-py", "--help"]
