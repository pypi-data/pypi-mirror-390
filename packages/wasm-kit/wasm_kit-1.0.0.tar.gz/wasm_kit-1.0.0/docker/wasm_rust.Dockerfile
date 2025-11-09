# syntax=docker/dockerfile:1.4
FROM rust:latest

LABEL maintainer="wasm-kit"
LABEL description="Rust WebAssembly builder - auto-installs tools based on project requirements"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install wasm32 targets - wasm32-wasip1 is the modern target
# wasm32-wasi is deprecated in newer Rust versions, so we only install wasm32-wasip1
RUN rustup target add wasm32-wasip1

# Ensure cargo bin directory exists and is in PATH
# cargo install puts binaries in ~/.cargo/bin which is /root/.cargo/bin for root user
RUN mkdir -p /root/.cargo/bin
ENV PATH="/root/.cargo/bin:/usr/local/cargo/bin:${PATH}"

# Install cargo-component globally with BuildKit caching
# This cache mount significantly speeds up subsequent builds
# Try installation without --locked first (to avoid yanked package issues), then with --locked
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/usr/local/cargo/git \
    --mount=type=cache,target=/root/.cargo/registry \
    --mount=type=cache,target=/root/.cargo/git \
    echo "Installing cargo-component..." && \
    (cargo install cargo-component 2>&1 || \
     cargo install --git https://github.com/bytecodealliance/cargo-component --locked 2>&1 || \
     cargo install cargo-component --locked 2>&1) && \
    echo "Verifying cargo-component installation..." && \
    (cargo component --version 2>&1 || cargo-component --version 2>&1 || (echo "ERROR: cargo-component not found" && ls -la /root/.cargo/bin/ && exit 1))

# Install wasm-tools globally with BuildKit caching
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/usr/local/cargo/git \
    --mount=type=cache,target=/root/.cargo/registry \
    --mount=type=cache,target=/root/.cargo/git \
    cargo install wasm-tools --locked || (echo "Warning: wasm-tools installation failed" && exit 0)

# Verify wasm-tools is installed (optional)
RUN wasm-tools --version || echo "wasm-tools not found (optional tool)"

WORKDIR /src
CMD ["cargo", "--version"]
