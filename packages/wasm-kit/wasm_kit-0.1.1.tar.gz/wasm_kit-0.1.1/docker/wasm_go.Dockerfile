# syntax=docker/dockerfile:1.4
FROM tinygo/tinygo:latest

LABEL maintainer="wasm-kit"
LABEL description="Go WebAssembly builder using TinyGo"

WORKDIR /src
CMD ["tinygo", "version"]

