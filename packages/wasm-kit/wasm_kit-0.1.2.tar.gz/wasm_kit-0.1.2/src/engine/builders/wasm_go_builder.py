import os
import platform
import subprocess
from pathlib import Path

from utils import BuildError
from utils.wasm_detect import get_project_name

from .base import WasmBuilder


class GoWasmBuilder(WasmBuilder):

    def build(
        self,
        project_dir: Path,
        wit_dir: Path,
        world: str,
        entry: Path,
        wasm_type: str = "standalone",
    ) -> Path:
        user_args = self._get_user_mapping_args()

        entry_rel = str(entry.relative_to(project_dir))

        project_name = get_project_name(project_dir)
        output_ext = "wasm" if wasm_type == "standalone" else "wcmp"
        output_name = f"{project_name}.{output_ext}"

        # Use wasip1 target for WASI Preview 1 compatibility (standalone WASM)
        # wasi target in newer TinyGo uses WASI Preview 2 (component model) which requires different runtime
        # Try wasip1 first, fallback to wasi if wasip1 is not available
        build_cmd = (
            f"cd /src && "
            f"(tinygo build -o /src/{output_name} -target wasip1 {entry_rel} || "
            f"tinygo build -o /src/{output_name} -target wasi {entry_rel}) && "
            f"chmod u+w /src/{output_name} 2>/dev/null || true"
        )

        docker_cmd = [
            "docker",
            "run",
            "--rm",
            *user_args,
            "-v",
            f"{project_dir}:/src",
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
            raise BuildError(f"Go build failed: {e}")
        except FileNotFoundError:
            raise BuildError("Docker not found. Install Docker or use local build.")

        output_path = project_dir / output_name
        if not output_path.exists():
            raise BuildError(f"Output file not found: {output_path}")

        try:
            os.chmod(output_path, 0o644)
        except Exception:
            pass

        return output_path

    def _get_user_mapping_args(self) -> list:
        if platform.system() == "Windows":
            return []
        try:
            return ["--user", f"{os.getuid()}:{os.getgid()}"]
        except AttributeError:
            return []

    def get_dockerfile(self) -> str:
        return "wasm_go.Dockerfile"
