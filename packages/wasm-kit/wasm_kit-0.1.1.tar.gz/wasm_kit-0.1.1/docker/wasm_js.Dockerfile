# syntax=docker/dockerfile:1.4
FROM node:20-slim

LABEL maintainer="wasm-kit"
LABEL description="JavaScript/TypeScript WebAssembly builder - auto-installs tools based on project requirements"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install componentize-js and jco globally with BuildKit caching
# These will be available system-wide for all projects
# If projects need specific versions, they can be installed via package.json
# The cache mount speeds up npm installs on subsequent builds
# Install componentize-js and ensure all dependencies are available
RUN --mount=type=cache,target=/root/.npm \
    npm install -g @bytecodealliance/componentize-js@latest @bytecodealliance/jco@latest && \
    cd /usr/local/lib/node_modules/@bytecodealliance/componentize-js && \
    npm install --production --no-save || true && \
    npm cache clean --force

WORKDIR /src
CMD ["node", "--version"]
