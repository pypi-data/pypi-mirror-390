import hashlib
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict

from utils import BuildError, check_docker_available
from utils.wasm_detect import get_docker_base_version


def _find_dockerfile_path(dockerfile_name: str) -> Path:
    dev_dockerfile_path = Path(__file__).parent.parent.parent / "docker" / dockerfile_name
    if dev_dockerfile_path.exists():
        return dev_dockerfile_path

    cwd_dockerfile_path = Path.cwd() / "docker" / dockerfile_name
    if cwd_dockerfile_path.exists():
        return cwd_dockerfile_path

    try:
        system_module_path = Path(__file__).parent
        for parent_dir in system_module_path.parents:
            docker_directory = parent_dir / "docker"
            candidate_path = docker_directory / dockerfile_name
            if docker_directory.exists() and candidate_path.exists():
                return candidate_path
    except Exception:
        pass

    raise BuildError(
        f"Dockerfile not found: {dockerfile_name}. "
        "Please ensure Dockerfiles are in the docker/ directory. "
        f"Tried: {dev_dockerfile_path}, {cwd_dockerfile_path}"
    )


def ensure_image(dockerfile_name: str) -> None:
    if not check_docker_available():
        raise BuildError(
            "Docker is not available. "
            "Install Docker from https://docker.com or use local build tools."
        )

    dockerfile_to_image_map = {
        "wasm_python.Dockerfile": "wasm-python-builder",
        "wasm_js.Dockerfile": "wasm-js-builder",
        "wasm_rust.Dockerfile": "wasm-rust-builder",
        "wasm_go.Dockerfile": "wasm-go-builder",
        "wasm_cpp.Dockerfile": "wasm-cpp-builder",
    }

    image_name = dockerfile_to_image_map.get(dockerfile_name)
    if not image_name:
        raise BuildError(f"Unknown Dockerfile: {dockerfile_name}")

    dockerfile_path = _find_dockerfile_path(dockerfile_name)

    # Check if Dockerfile has changed by comparing its hash with image label
    dockerfile_hash = _get_dockerfile_hash(dockerfile_path)
    needs_rebuild = True

    try:
        check_image_result = subprocess.run(
            ["docker", "images", "-q", image_name], capture_output=True, text=True, check=False
        )
        if check_image_result.stdout.strip():
            # Image exists, check if Dockerfile hash matches
            inspect_result = subprocess.run(
                ["docker", "inspect", "--format", "{{.Config.Labels.dockerfile_hash}}", image_name],
                capture_output=True,
                text=True,
                check=False,
            )
            existing_hash = inspect_result.stdout.strip()
            if existing_hash == dockerfile_hash:
                needs_rebuild = False
            else:
                # Dockerfile changed, remove old image to force rebuild
                subprocess.run(
                    ["docker", "rmi", "-f", image_name],
                    capture_output=True,
                    check=False,
                )
    except FileNotFoundError:
        raise BuildError("Docker command not found. Install Docker.")

    if not needs_rebuild:
        return

    build_context_path = (
        dockerfile_path.parent.parent
        if dockerfile_path.parent.name == "docker"
        else dockerfile_path.parent
    )

    try:
        build_env = {**os.environ, "DOCKER_BUILDKIT": "1"}
        # Build with label containing Dockerfile hash for future comparison
        subprocess.run(
            [
                "docker",
                "build",
                "-f",
                str(dockerfile_path),
                "-t",
                image_name,
                "--label",
                f"dockerfile_hash={dockerfile_hash}",
                str(build_context_path),
            ],
            env=build_env,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise BuildError(f"Failed to build Docker image {image_name}: {e}")


def _get_dockerfile_hash(dockerfile_path: Path) -> str:
    """Calculate SHA256 hash of Dockerfile content for change detection."""
    try:
        content = dockerfile_path.read_bytes()
        return hashlib.sha256(content).hexdigest()[:16]  # Use first 16 chars for label
    except Exception:
        return "unknown"


def generate_dynamic_dockerfile(language: str, deps: Dict[str, str], project_dir: Path) -> str:
    if language == "python":
        return _generate_python_dockerfile(deps)
    elif language in ("javascript", "typescript"):
        return _generate_js_dockerfile(deps)
    elif language == "rust":
        return _generate_rust_dockerfile(deps)
    elif language == "go":
        return _generate_go_dockerfile(deps)
    elif language in ("c", "cpp"):
        return _generate_cpp_dockerfile(deps)
    else:
        raise BuildError(f"Unsupported language for dynamic Dockerfile: {language}")


def _generate_python_dockerfile(deps: Dict[str, str]) -> str:
    docker_base_image = get_docker_base_version("python")

    dockerfile_content = "# syntax=docker/dockerfile:1.4\n"
    dockerfile_content += f"FROM {docker_base_image}\n\n"
    dockerfile_content += 'LABEL maintainer="wasm-kit"\n'
    dockerfile_content += (
        'LABEL description="Python WebAssembly builder - dynamic dependencies"\n\n'
    )

    dockerfile_content += "RUN apt-get update && apt-get install -y \\\n"
    dockerfile_content += "    git \\\n"
    dockerfile_content += "    && rm -rf /var/lib/apt/lists/*\n\n"

    pip_install_command = (
        "RUN --mount=type=cache,target=/root/.cache/pip \\\n    pip install --no-cache-dir"
    )

    componentize_py_version = deps.get("componentize_py", "*")
    if componentize_py_version != "*":
        pip_install_command += f" componentize-py=={componentize_py_version}"
    else:
        pip_install_command += " componentize-py"

    wasmtime_version = deps.get("wasmtime", "*")
    if wasmtime_version != "*":
        pip_install_command += f" wasmtime=={wasmtime_version}"
    else:
        pip_install_command += " wasmtime"

    dockerfile_content += pip_install_command + "\n\n"
    dockerfile_content += "WORKDIR /src\n"
    dockerfile_content += 'CMD ["componentize-py", "--help"]\n'

    return dockerfile_content


def _generate_js_dockerfile(deps: Dict[str, str]) -> str:
    docker_base_image = get_docker_base_version("javascript")

    dockerfile_content = "# syntax=docker/dockerfile:1.4\n"
    dockerfile_content += f"FROM {docker_base_image}\n\n"
    dockerfile_content += 'LABEL maintainer="wasm-kit"\n'
    dockerfile_content += (
        'LABEL description="JavaScript/TypeScript WebAssembly builder - dynamic dependencies"\n\n'
    )

    dockerfile_content += "RUN apt-get update && apt-get install -y \\\n"
    dockerfile_content += "    git \\\n"
    dockerfile_content += "    && rm -rf /var/lib/apt/lists/*\n\n"

    componentize_js_version = deps.get("componentize_js", "*")
    if componentize_js_version != "*":
        dockerfile_content += f"RUN --mount=type=cache,target=/root/.npm \\\n    npm install -g @bytecodealliance/componentize-js@{componentize_js_version}\n"
    else:
        dockerfile_content += "RUN --mount=type=cache,target=/root/.npm \\\n    npm install -g @bytecodealliance/componentize-js\n"

    jco_version = deps.get("jco", "*")
    if jco_version != "*":
        dockerfile_content += f"RUN --mount=type=cache,target=/root/.npm \\\n    npm install -g @bytecodealliance/jco@{jco_version}\n"
    else:
        dockerfile_content += "RUN --mount=type=cache,target=/root/.npm \\\n    npm install -g @bytecodealliance/jco\n"

    dockerfile_content += "\nWORKDIR /src\n"
    dockerfile_content += 'CMD ["node", "--version"]\n'

    return dockerfile_content


def _generate_rust_dockerfile(deps: Dict[str, str]) -> str:
    docker_base_image = get_docker_base_version("rust")

    dockerfile_content = "# syntax=docker/dockerfile:1.4\n"
    dockerfile_content += f"FROM {docker_base_image}\n\n"
    dockerfile_content += 'LABEL maintainer="wasm-kit"\n'
    dockerfile_content += 'LABEL description="Rust WebAssembly builder - dynamic dependencies"\n\n'

    dockerfile_content += "RUN apt-get update && apt-get install -y \\\n"
    dockerfile_content += "    git \\\n"
    dockerfile_content += "    pkg-config \\\n"
    dockerfile_content += "    libssl-dev \\\n"
    dockerfile_content += "    && rm -rf /var/lib/apt/lists/*\n\n"

    dockerfile_content += (
        "RUN rustup target add wasm32-wasip1 2>/dev/null || rustup target add wasm32-wasi\n\n"
    )

    dockerfile_content += "RUN mkdir -p /root/.cargo/bin\n"
    dockerfile_content += 'ENV PATH="/root/.cargo/bin:/usr/local/cargo/bin:${PATH}"\n\n'

    dockerfile_content += "RUN --mount=type=cache,target=/usr/local/cargo/registry \\\n"
    dockerfile_content += "    --mount=type=cache,target=/usr/local/cargo/git \\\n"
    dockerfile_content += "    --mount=type=cache,target=/root/.cargo/registry \\\n"
    dockerfile_content += "    --mount=type=cache,target=/root/.cargo/git \\\n"
    dockerfile_content += "    cargo install cargo-component || \\\n"
    dockerfile_content += "    cargo install --git https://github.com/bytecodealliance/cargo-component --locked || \\\n"
    dockerfile_content += "    cargo install cargo-component --locked\n\n"

    dockerfile_content += 'RUN cargo component --version 2>&1 || cargo-component --version 2>&1 || (echo "ERROR: cargo-component not found" && ls -la /root/.cargo/bin/ && exit 1)\n\n'

    dockerfile_content += "RUN --mount=type=cache,target=/usr/local/cargo/registry \\\n"
    dockerfile_content += "    --mount=type=cache,target=/usr/local/cargo/git \\\n"
    dockerfile_content += "    --mount=type=cache,target=/root/.cargo/registry \\\n"
    dockerfile_content += "    --mount=type=cache,target=/root/.cargo/git \\\n"
    dockerfile_content += (
        '    cargo install wasm-tools --locked || echo "wasm-tools installation failed"\n\n'
    )

    dockerfile_content += "WORKDIR /src\n"
    dockerfile_content += 'CMD ["cargo", "--version"]\n'

    return dockerfile_content


def _generate_go_dockerfile(deps: Dict[str, str]) -> str:
    dockerfile_content = "# syntax=docker/dockerfile:1.4\n"
    dockerfile_content += "FROM tinygo/tinygo:latest\n\n"
    dockerfile_content += 'LABEL maintainer="wasm-kit"\n'
    dockerfile_content += 'LABEL description="Go WebAssembly builder using TinyGo"\n\n'
    dockerfile_content += "WORKDIR /src\n"
    dockerfile_content += 'CMD ["tinygo", "version"]\n'

    return dockerfile_content


def _generate_cpp_dockerfile(deps: Dict[str, str]) -> str:
    dockerfile_content = "# syntax=docker/dockerfile:1.4\n"
    dockerfile_content += "FROM ubuntu:22.04\n\n"
    dockerfile_content += 'LABEL maintainer="wasm-kit"\n'
    dockerfile_content += (
        'LABEL description="C/C++ WebAssembly builder using clang and wasi-libc"\n\n'
    )
    dockerfile_content += "ENV DEBIAN_FRONTEND=noninteractive\n\n"
    dockerfile_content += "RUN apt-get update && apt-get install -y \\\n"
    dockerfile_content += "    clang \\\n"
    dockerfile_content += "    lld \\\n"
    dockerfile_content += "    wget \\\n"
    dockerfile_content += "    ca-certificates \\\n"
    dockerfile_content += "    && rm -rf /var/lib/apt/lists/*\n\n"
    dockerfile_content += "RUN mkdir -p /wasi-libc && \\\n"
    dockerfile_content += "    cd /wasi-libc && \\\n"
    dockerfile_content += "    wget -q https://github.com/WebAssembly/wasi-libc/releases/download/wasi-sdk-21/wasi-libc-21.0.tar.gz && \\\n"
    dockerfile_content += "    tar -xzf wasi-libc-21.0.tar.gz --strip-components=1 && \\\n"
    dockerfile_content += "    rm wasi-libc-21.0.tar.gz\n\n"
    dockerfile_content += "WORKDIR /src\n"
    dockerfile_content += 'CMD ["clang", "--version"]\n'

    return dockerfile_content


def build_dynamic_image(language: str, deps: Dict[str, str], project_dir: Path) -> str:
    if not check_docker_available():
        raise BuildError("Docker is not available.")

    dependencies_string = ",".join(f"{key}={value}" for key, value in sorted(deps.items()))
    dependencies_hash = hashlib.md5(dependencies_string.encode()).hexdigest()[:8]
    dynamic_image_name = f"wasmkit-{language}-{dependencies_hash}"

    try:
        check_image_result = subprocess.run(
            ["docker", "images", "-q", dynamic_image_name],
            capture_output=True,
            text=True,
            check=False,
        )
        if check_image_result.stdout.strip():
            return dynamic_image_name
    except FileNotFoundError:
        raise BuildError("Docker command not found. Install Docker.")

    dockerfile_content = generate_dynamic_dockerfile(language, deps, project_dir)

    # Use secure temporary file handling to prevent race conditions
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".Dockerfile", prefix=".wasmkit-", dir=project_dir, delete=False
    ) as temp_dockerfile:
        temp_dockerfile.write(dockerfile_content)
        temp_dockerfile_path = Path(temp_dockerfile.name)

    try:
        build_env = {**os.environ, "DOCKER_BUILDKIT": "1"}
        subprocess.run(
            [
                "docker",
                "build",
                "-f",
                str(temp_dockerfile_path),
                "-t",
                dynamic_image_name,
                str(project_dir),
            ],
            env=build_env,
            check=True,
            cwd=project_dir,
        )
    finally:
        # Always clean up the temporary Dockerfile
        if temp_dockerfile_path.exists():
            temp_dockerfile_path.unlink()

    return dynamic_image_name
