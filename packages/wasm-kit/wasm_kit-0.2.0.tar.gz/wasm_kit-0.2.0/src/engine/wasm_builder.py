import time
from pathlib import Path
from typing import Optional

from rich.console import Console

from system.wasm_docker import build_dynamic_image, ensure_image
from utils import BuildError
from utils.wasm_deps import get_dependencies
from utils.wasm_detect import detect_entry, detect_language, detect_wit, supports_wasi_http
from utils.wasm_script import generate_run_script, generate_serve_script

from .builders.wasm_builder_factory import get_builder
from .wasm_optimizer import optimize

console = Console()


def build_project(
    project_dir: Path, wasm_type: str = "component", output_path: Optional[str] = None
) -> dict:
    build_start = time.time()
    project_path = Path(project_dir).resolve()

    language = detect_language(project_path)

    if wasm_type not in ("component", "standalone"):
        wasm_type = "component"

    # Auto-correct unsupported combinations with clear messaging
    if language == "go" and wasm_type == "component":
        raise BuildError(
            "Go only supports standalone WASM (not components). "
            "Use: wasm-kit build --type standalone"
        )

    if language in ("c", "cpp") and wasm_type == "component":
        raise BuildError(
            "C/C++ only supports standalone WASM (not components). "
            "Use: wasm-kit build --type standalone"
        )

    dependencies = get_dependencies(project_path, language)
    needs_dynamic = any(v != "*" for v in dependencies.values()) if dependencies else False

    builder = get_builder(project_path)

    wit_dir, world = detect_wit(project_path) if wasm_type == "component" else (None, None)
    entry_file = detect_entry(project_path)

    if needs_dynamic:
        dynamic_image = build_dynamic_image(language, dependencies, project_path)
        builder.set_image_name(dynamic_image)
    else:
        ensure_image(builder.get_dockerfile())

    wasm_file = builder.build(project_path, wit_dir, world, entry_file, wasm_type)

    try:
        optimize(wasm_file)
    except Exception:
        pass

    # For .wcmp files, create a .wasm symlink for tool compatibility
    # Users see .wcmp (clear component extension), tools can use .wasm (standard)
    if wasm_file.suffix == ".wcmp":
        wasm_symlink = wasm_file.with_suffix(".wasm")
        try:
            # Remove existing symlink or file if it exists
            if wasm_symlink.exists() or wasm_symlink.is_symlink():
                wasm_symlink.unlink()
            # Create symlink to .wcmp file
            wasm_symlink.symlink_to(wasm_file.name)
        except (OSError, NotImplementedError):
            # If symlinks aren't supported (Windows), create a copy instead
            import shutil

            shutil.copy2(wasm_file, wasm_symlink)

    if output_path:
        import shutil

        output = Path(output_path).resolve()

        # Enforce correct extension based on WASM type
        expected_ext = ".wasm" if wasm_type == "standalone" else ".wcmp"
        if output.suffix not in (".wasm", ".wcmp"):
            # No extension or wrong extension - add correct one
            output = output.with_suffix(expected_ext)
        elif output.suffix != expected_ext:
            # Wrong extension - replace it
            output = output.with_suffix(expected_ext)

        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(wasm_file, output)
        wasm_file = output

    generate_run_script(wasm_file, project_path)

    # Only generate serve.sh for components that support wasi:http
    # Standalone .wasm files and library components cannot be served via HTTP
    if wasm_type == "component" and supports_wasi_http(wasm_file):
        generate_serve_script(wasm_file, project_path)
    elif wasm_type == "component":
        # Component exists but doesn't support HTTP - inform user
        console.print(
            "[dim]Note: Component doesn't implement wasi:http interface. "
            "Skipping serve.sh generation.[/dim]"
        )
        console.print(
            "[dim]This is a library component. "
            "Call its functions from a host program or use jco.[/dim]"
        )

    duration = round(time.time() - build_start, 2)
    return {"wasm_file": wasm_file, "time": duration, "wasm_type": wasm_type}
