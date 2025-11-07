import subprocess
from pathlib import Path

from utils import BuildError
from utils.wasm_detect import get_project_name

from .base import WasmBuilder


class JavaScriptWasmBuilder(WasmBuilder):

    def build(
        self,
        project_dir: Path,
        wit_dir: Path,
        world: str,
        entry: Path,
        wasm_type: str = "component",
    ) -> Path:
        if wasm_type == "standalone":
            raise BuildError(
                "JavaScript/TypeScript does not support standalone WASM. Use component type instead."
            )

        project_name = get_project_name(project_dir)
        output_ext = "wcmp"
        output_path = project_dir / f"{project_name}.{output_ext}"

        wit_file = next(wit_dir.glob("*.wit"), None)
        if not wit_file:
            raise BuildError(f"No WIT file found in {wit_dir}")

        entry_rel = str(entry.relative_to(project_dir))

        wit_target = "/wit" if (wit_dir / "deps").exists() else f"/wit/{wit_file.name}"

        cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{project_dir}:/src",
            "-v",
            f"{wit_dir}:/wit",
            self.get_image_name(),
            "npx",
            "componentize-js",
            f"/src/{entry_rel}",
            "-o",
            f"/src/{project_name}.{output_ext}",
            "--wit",
            wit_target,
        ]

        if world and world != "app":
            cmd.extend(["--world-name", world])

        try:
            subprocess.run(cmd, check=True, cwd=project_dir)
        except subprocess.CalledProcessError as e:
            raise BuildError(f"JavaScript build failed: {e}")
        except FileNotFoundError:
            raise BuildError("Docker not found. Install Docker or use local build.")

        if not output_path.exists():
            raise BuildError(f"Output file not found: {output_path}")

        return output_path

    def get_dockerfile(self) -> str:
        return "wasm_js.Dockerfile"
