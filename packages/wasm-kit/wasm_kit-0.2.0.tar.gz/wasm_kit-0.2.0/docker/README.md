# Docker Images for wasm-kit

Pre-configured Docker images for building WebAssembly from different languages.

## Available Images

wasm-kit includes Docker images for all supported languages:

1. **wasm_python.Dockerfile** - Python + componentize-py
2. **wasm_js.Dockerfile** - Node.js + componentize-js
3. **wasm_rust.Dockerfile** - Rust + cargo-component
4. **wasm_go.Dockerfile** - TinyGo for WASI
5. **wasm_cpp.Dockerfile** - WASI-SDK (clang/clang++)

## Image Details

### Python (wasm_python.Dockerfile)

**Includes:**
- Python 3.12-slim (or auto-detected version)
- componentize-py
- pip and setuptools

**Usage:**
```bash
docker build -f docker/wasm_python.Dockerfile -t wasm-python-builder .
docker run --rm -v $(pwd):/src wasm-python-builder \
  componentize-py componentize app -o out.wasm
```

### JavaScript/TypeScript (wasm_js.Dockerfile)

**Includes:**
- Node.js 20-alpine (or auto-detected version)
- @bytecodealliance/componentize-js
- @bytecodealliance/jco
- npm and build tools

**Usage:**
```bash
docker build -f docker/wasm_js.Dockerfile -t wasm-js-builder .
docker run --rm -v $(pwd):/src wasm-js-builder \
  jco componentize index.js -o out.wasm
```

### Rust (wasm_rust.Dockerfile)

**Includes:**
- Rust 1.82-slim (or latest stable)
- cargo-component
- wasm32-wasip1 target
- wasm-tools

**Usage:**
```bash
docker build -f docker/wasm_rust.Dockerfile -t wasm-rust-builder .
docker run --rm -v $(pwd):/src wasm-rust-builder \
  cargo component build --release
```

### Go (wasm_go.Dockerfile)

**Includes:**
- TinyGo latest
- Go toolchain
- WASI support

**Usage:**
```bash
docker build -f docker/wasm_go.Dockerfile -t wasm-go-builder .
docker run --rm -v $(pwd):/src wasm-go-builder \
  tinygo build -o out.wasm -target wasi .
```

### C/C++ (wasm_cpp.Dockerfile)

**Includes:**
- WASI-SDK
- clang/clang++ with wasm32-wasi target
- wasi-libc

**Usage:**
```bash
docker build -f docker/wasm_cpp.Dockerfile -t wasm-cpp-builder .
docker run --rm -v $(pwd):/src wasm-cpp-builder \
  clang -target wasm32-wasi -o out.wasm main.c
```

## Building All Images

Use the automated script:

```bash
./scripts/docker-build-all.sh
```

Or build individually:

```bash
docker build -f docker/wasm_python.Dockerfile -t wasm-python-builder .
docker build -f docker/wasm_js.Dockerfile -t wasm-js-builder .
docker build -f docker/wasm_rust.Dockerfile -t wasm-rust-builder .
docker build -f docker/wasm_go.Dockerfile -t wasm-go-builder .
docker build -f docker/wasm_cpp.Dockerfile -t wasm-cpp-builder .
```

## Image Naming Convention

Images are named: `wasm-{language}-builder`

Examples:
- `wasm-python-builder`
- `wasm-js-builder`
- `wasm-rust-builder`
- `wasm-go-builder`
- `wasm-cpp-builder`

## Version Detection

wasm-kit automatically detects your system's runtime version and uses matching Docker images:

- Python: Matches your `python3 --version` (e.g., 3.11)
- Node.js: Matches your `node --version` (e.g., 20)
- Rust: Uses latest stable (1.82+)
- TinyGo: Uses latest stable
- WASI-SDK: Uses latest release

**Fallback versions:**
- Python: 3.12-slim
- Node.js: 20-alpine
- Rust: 1.82-slim

## Usage with wasm-kit CLI

These images are used automatically by wasm-kit:

```bash
# wasm-kit detects language and uses appropriate image
wasm-kit build .

# Images are built on first use and cached
# Subsequent builds are much faster
```

## Publishing to Registry

To publish images to Docker Hub:

```bash
# Tag images
docker tag wasm-python-builder username/wasm-python-builder:latest
docker tag wasm-js-builder username/wasm-js-builder:latest
docker tag wasm-rust-builder username/wasm-rust-builder:latest
docker tag wasm-go-builder username/wasm-go-builder:latest
docker tag wasm-cpp-builder username/wasm-cpp-builder:latest

# Push to registry
docker push username/wasm-python-builder:latest
docker push username/wasm-js-builder:latest
docker push username/wasm-rust-builder:latest
docker push username/wasm-go-builder:latest
docker push username/wasm-cpp-builder:latest
```

## Image Optimization

All images are optimized for:
- **Size**: Using slim/alpine base images
- **Build speed**: Layer caching for dependencies
- **Security**: Minimal attack surface
- **Reproducibility**: Pinned dependency versions

## Build Cache

Docker BuildKit caches layers for faster rebuilds:

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build with cache
docker build -f docker/wasm_rust.Dockerfile -t wasm-rust-builder .
```

## Troubleshooting

### Permission Issues

If Docker creates files as root:

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Or use user mapping (handled by wasm-kit)
docker run --user $(id -u):$(id -g) ...
```

### Build Failures

```bash
# Clear cache and rebuild
docker build --no-cache -f docker/wasm_python.Dockerfile -t wasm-python-builder .

# Check disk space
docker system df
docker system prune
```

### Image Size

```bash
# Check image sizes
docker images | grep wasm-

# Expected sizes (approximate):
# wasm-python-builder: 200-400 MB
# wasm-js-builder: 150-300 MB
# wasm-rust-builder: 1-2 GB (Rust toolchain is large)
# wasm-go-builder: 300-500 MB
# wasm-cpp-builder: 200-400 MB
```

## Development

### Testing Images Locally

```bash
# Build image
docker build -f docker/wasm_python.Dockerfile -t wasm-python-builder .

# Test interactively
docker run -it --rm -v $(pwd):/src wasm-python-builder sh

# Inside container:
cd /src
python --version
componentize-py --version
```

### Updating Dockerfiles

When updating Dockerfiles:

1. Test locally first
2. Update version comments
3. Rebuild and test
4. Update this README
5. Commit changes

## Multi-Architecture Support

To build for multiple platforms:

```bash
# Build for AMD64 and ARM64
docker buildx build --platform linux/amd64,linux/arm64 \
  -f docker/wasm_python.Dockerfile \
  -t wasm-python-builder .
```

## CI/CD Integration

Images can be built in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Build Docker Images
  run: ./scripts/docker-build-all.sh
```

## Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [WASI SDK](https://github.com/WebAssembly/wasi-sdk)
- [TinyGo](https://tinygo.org/)
- [cargo-component](https://github.com/bytecodealliance/cargo-component)
- [componentize-py](https://github.com/bytecodealliance/componentize-py)
- [componentize-js](https://github.com/bytecodealliance/componentize-js)

## Support

For Docker-related issues:
- Check [Troubleshooting Guide](../docs/TROUBLESHOOTING.md)
- Open an issue on GitHub
- Run `wasm-kit doctor` for diagnostics
