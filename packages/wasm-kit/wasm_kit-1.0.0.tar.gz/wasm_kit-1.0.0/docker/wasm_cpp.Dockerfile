# syntax=docker/dockerfile:1.4
FROM ubuntu:22.04

LABEL maintainer="wasm-kit"
LABEL description="C/C++ WebAssembly builder using clang and wasi-libc"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    clang \
    lld \
    wget \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install wasi-libc - try multiple methods for reliability
RUN mkdir -p /wasi-libc && \
    cd /wasi-libc && \
    (wget -q https://github.com/WebAssembly/wasi-libc/releases/download/wasi-sdk-21/wasi-libc-21.0.tar.gz -O wasi-libc.tar.gz && tar -xzf wasi-libc.tar.gz --strip-components=1 && rm wasi-libc.tar.gz) || \
    (wget -q https://github.com/WebAssembly/wasi-libc/releases/download/wasi-sdk-20/wasi-libc-20.0.tar.gz -O wasi-libc.tar.gz && tar -xzf wasi-libc.tar.gz --strip-components=1 && rm wasi-libc.tar.gz) || \
    (wget -q https://github.com/WebAssembly/wasi-libc/releases/download/wasi-sdk-19/wasi-libc-19.0.tar.gz -O wasi-libc.tar.gz && tar -xzf wasi-libc.tar.gz --strip-components=1 && rm wasi-libc.tar.gz) || \
    (git clone --depth 1 https://github.com/WebAssembly/wasi-libc.git /tmp/wasi-libc && \
     cp -r /tmp/wasi-libc/* /wasi-libc/ && \
     rm -rf /tmp/wasi-libc) || \
    (echo "ERROR: Failed to install wasi-libc" && exit 1)

ENV WASI_SDK_PATH=/usr
ENV PATH="${PATH}:/usr/bin"

WORKDIR /src
CMD ["clang", "--version"]

