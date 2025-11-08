import subprocess
from pathlib import Path

from utils import BuildError
from utils.wasm_detect import get_project_name

from .base import WasmBuilder


class PythonWasmBuilder(WasmBuilder):

    def build(
        self,
        project_dir: Path,
        wit_dir: Path,
        world: str,
        entry: Path,
        wasm_type: str = "component",
    ) -> Path:
        if wasm_type == "standalone":
            raise BuildError("Python does not support standalone WASM. Use component type instead.")

        project_name = get_project_name(project_dir)
        output_ext = "wcmp"
        output_path = project_dir / f"{project_name}.{output_ext}"

        wit_file = next(wit_dir.glob("*.wit"), None)
        if not wit_file:
            raise BuildError(f"No WIT file found in {wit_dir}")

        module_name = entry.stem
        module_parent_dir = entry.parent if entry.parent != project_dir else None
        cleanup_wrapper = False
        wrapper_file = None

        # componentize-py requires the module name to be different from world name
        # If they conflict, we need to use a wrapper module or rename
        # The simplest solution: if module name == world name, create a wrapper
        if module_name.lower() == world.lower():
            # Create a temporary wrapper module that imports from the original
            wrapper_name = f"{module_name}_component"
            wrapper_file = project_dir / f"{wrapper_name}.py"
            try:
                # Create wrapper that imports and re-exports from the original module
                wrapper_content = f"""# Auto-generated wrapper to avoid name conflict with world '{world}'
from {module_name} import *
"""
                wrapper_file.write_text(wrapper_content)
                module_name = wrapper_name
                # Clean up wrapper after build
                cleanup_wrapper = True
            except Exception:
                cleanup_wrapper = False
                wrapper_file = None
                # Fallback: try using project name
                module_name = project_name.replace("-", "_").replace(" ", "_")

        cmd = ["componentize-py", "-d", f"/wit/{wit_file.name}", "-w", world, "componentize"]

        if module_parent_dir:
            rel_path = module_parent_dir.relative_to(project_dir)
            cmd.extend(["-p", str(rel_path)])

        cmd.extend([module_name, "-o", f"/src/{project_name}.{output_ext}"])

        requirements_file = project_dir / "requirements.txt"
        install_deps = False
        if requirements_file.exists():
            content = requirements_file.read_text()
            install_deps = "componentize-py" in content or "wasmtime" in content

        if install_deps:
            full_cmd = f"pip install --no-cache-dir -r /src/requirements.txt 2>/dev/null || true && {' '.join(cmd)}"
            docker_cmd = [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{project_dir}:/src",
                "-v",
                f"{wit_dir}:/wit",
                self.get_image_name(),
                "sh",
                "-c",
                full_cmd,
            ]
        else:
            docker_cmd = [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{project_dir}:/src",
                "-v",
                f"{wit_dir}:/wit",
                self.get_image_name(),
                *cmd,
            ]

        try:
            subprocess.run(docker_cmd, check=True, cwd=project_dir)
        except subprocess.CalledProcessError as e:
            # Clean up wrapper if it was created
            if cleanup_wrapper and wrapper_file and wrapper_file.exists():
                wrapper_file.unlink()
            raise BuildError(f"Python build failed: {e}")
        except FileNotFoundError:
            # Clean up wrapper if it was created
            if cleanup_wrapper and wrapper_file and wrapper_file.exists():
                wrapper_file.unlink()
            raise BuildError("Docker not found. Install Docker or use local build.")

        # Clean up wrapper file if it was created
        if cleanup_wrapper and wrapper_file and wrapper_file.exists():
            wrapper_file.unlink()

        if not output_path.exists():
            raise BuildError(f"Output file not found: {output_path}")

        return output_path

    def get_dockerfile(self) -> str:
        return "wasm_python.Dockerfile"
