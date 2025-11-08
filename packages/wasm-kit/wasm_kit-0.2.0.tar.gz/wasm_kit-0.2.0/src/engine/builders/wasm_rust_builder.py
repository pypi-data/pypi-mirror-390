# Rust WASM builder using cargo-component

import os
import platform
import shutil
import subprocess
from pathlib import Path

from utils import BuildError
from utils.wasm_detect import get_project_name

from .base import WasmBuilder


class RustWasmBuilder(WasmBuilder):

    def build(
        self,
        project_dir: Path,
        wit_dir: Path,
        world: str,
        entry: Path,
        wasm_type: str = "component",
    ) -> Path:
        user_args = self._get_user_mapping_args()

        project_name = get_project_name(project_dir)
        output_ext = "wasm" if wasm_type == "standalone" else "wcmp"
        output_name = f"{project_name}.{output_ext}"

        if wasm_type == "standalone":
            # Use wasm32-wasip1 instead of wasm32-wasi (newer Rust versions don't support wasm32-wasi)
            build_cmd = (
                "mkdir -p /src/.cargo /src/target/wasm32-wasip1/release && "
                "cargo build --release --target wasm32-wasip1 && "
                "chmod -R u+w /src/target /src/.cargo 2>/dev/null || true"
            )
        else:
            build_cmd = (
                "mkdir -p /src/.cargo /src/target/wasm32-wasip1/release /src/target/wasm32-wasi/release && "
                "cargo component build --release && "
                "chmod -R u+w /src/target /src/.cargo 2>/dev/null || true"
            )

        docker_cmd = [
            "docker",
            "run",
            "--rm",
            *user_args,
            "-v",
            f"{project_dir}:/src",
            "-e",
            "CARGO_HOME=/src/.cargo",
            "-e",
            "HOME=/tmp",
            self.get_image_name(),
            "sh",
            "-c",
            build_cmd,
        ]

        try:
            subprocess.run(docker_cmd, check=True, cwd=project_dir)
        except subprocess.CalledProcessError as e:
            raise BuildError(f"Rust build failed: {e}")
        except FileNotFoundError:
            raise BuildError("Docker not found. Install Docker or use local build.")

        compiled_wasm = self._find_compiled_wasm(project_dir, wasm_type)
        output_path = project_dir / output_name
        self._copy_file_with_permissions(compiled_wasm, output_path)

        return output_path

    def _get_user_mapping_args(self) -> list:
        if platform.system() == "Windows":
            return []
        try:
            return ["--user", f"{os.getuid()}:{os.getgid()}"]
        except AttributeError:
            return []

    def _find_compiled_wasm(self, project_dir: Path, wasm_type: str = "component") -> Path:
        if wasm_type == "standalone":
            # Try wasm32-wasip1 first (newer Rust), then fallback to wasm32-wasi (older Rust)
            targets = ["wasm32-wasip1", "wasm32-wasi"]
            for target in targets:
                release_dir = project_dir / "target" / target / "release"
                wasm_files = list(release_dir.glob("*.wasm"))
                if wasm_files:
                    return wasm_files[0]
        else:
            targets = ["wasm32-wasip1", "wasm32-wasi"]
            for target in targets:
                release_dir = project_dir / "target" / target / "release"
                wasm_files = list(release_dir.glob("*.wasm"))
                if wasm_files:
                    return wasm_files[0]
        raise BuildError("No WASM file found in target directory")

    def _copy_file_with_permissions(self, src: Path, dst: Path) -> None:
        try:
            os.chmod(src, 0o644)
            shutil.copy(src, dst)
            os.chmod(dst, 0o644)
        except PermissionError as e:
            try:
                os.chmod(src, 0o644)
                shutil.copy(src, dst)
                os.chmod(dst, 0o644)
            except Exception:
                raise BuildError(f"Permission denied: {e}")

    def get_dockerfile(self) -> str:
        return "wasm_rust.Dockerfile"
