# Detection utilities for language, WIT files, entry points, and runtime versions

import re
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple


def get_project_name(project_dir: Path) -> str:
    """Get the project name from the directory name."""
    project_path = Path(project_dir).resolve()
    return project_path.name


def detect_language(project_dir: Path) -> str:
    project_path = Path(project_dir).resolve()

    if (project_path / "pyproject.toml").exists() or (project_path / "requirements.txt").exists():
        return "python"

    if (project_path / "package.json").exists():
        return "typescript" if (project_path / "tsconfig.json").exists() else "javascript"

    if (project_path / "Cargo.toml").exists():
        return "rust"

    if (project_path / "go.mod").exists() or any(project_path.glob("*.go")):
        return "go"

    cpp_files = (
        list(project_path.glob("*.cpp"))
        + list(project_path.glob("*.cc"))
        + list(project_path.glob("*.cxx"))
        + list(project_path.glob("*.c++"))
    )
    c_files = list(project_path.glob("*.c"))
    if (
        cpp_files
        or c_files
        or (project_path / "CMakeLists.txt").exists()
        or (project_path / "Makefile").exists()
    ):
        if cpp_files:
            return "cpp"
        elif c_files:
            return "c"
        else:
            return "cpp"

    raise ValueError(
        f"No supported language detected in {project_path}. "
        "Supported: Python (pyproject.toml/requirements.txt), "
        "JavaScript/TypeScript (package.json), Rust (Cargo.toml), Go (go.mod), C/C++ (.c/.cpp)"
    )


def detect_wit(project_dir: Path) -> Tuple[Path, str]:
    project_path = Path(project_dir).resolve()

    wit_file_path = next(project_path.rglob("*.wit"), None)

    if wit_file_path:
        wit_directory = wit_file_path.parent
        world_name = parse_world_name(wit_file_path)
        return wit_directory, world_name or "app"

    wit_directory = project_path / "wit"
    wit_directory.mkdir(exist_ok=True)
    default_wit_file = wit_directory / "world.wit"

    if not default_wit_file.exists():
        default_wit_file.write_text(
            "package example:component;\n\n"
            "world app {\n"
            "  export run: func() -> string;\n"
            "}\n"
        )

    return wit_directory, "app"


def parse_world_name(wit_file: Path) -> Optional[str]:
    try:
        wit_content = wit_file.read_text()
        world_match = re.search(r"world\s+([a-zA-Z0-9_-]+)\s*\{", wit_content)
        return world_match.group(1) if world_match else None
    except Exception:
        return None


def detect_entry(project_dir: Path) -> Path:
    project_path = Path(project_dir).resolve()
    detected_language = detect_language(project_path)

    if detected_language == "python":
        entry_candidates = ["app.py", "main.py", "__main__.py", "src/app.py", "src/main.py"]
        for candidate_path in entry_candidates:
            candidate_file = project_path / candidate_path
            if candidate_file.exists():
                return candidate_file

        python_files = list(project_path.glob("*.py"))
        if python_files:
            return python_files[0]

        src_python_files = (
            list((project_path / "src").glob("*.py")) if (project_path / "src").exists() else []
        )
        if src_python_files:
            return src_python_files[0]

        return project_path / "app.py"

    elif detected_language in ["javascript", "typescript"]:
        entry_candidates = ["index.js", "index.ts", "main.js", "main.ts", "app.js", "app.ts"]
        for candidate_path in entry_candidates:
            candidate_file = project_path / candidate_path
            if candidate_file.exists():
                return candidate_file

        js_files = list(project_path.glob("*.js")) + list(project_path.glob("*.ts"))
        if js_files:
            return js_files[0]

        return project_path / "index.js"

    elif detected_language == "rust":
        entry_candidates = ["src/lib.rs", "src/main.rs"]
        for candidate_path in entry_candidates:
            candidate_file = project_path / candidate_path
            if candidate_file.exists():
                return candidate_file

        return project_path / "src/lib.rs"

    elif detected_language == "go":
        entry_candidates = ["main.go", "cmd/main.go", "app.go"]
        for candidate_path in entry_candidates:
            candidate_file = project_path / candidate_path
            if candidate_file.exists():
                return candidate_file

        go_files = list(project_path.glob("*.go"))
        if go_files:
            return go_files[0]

        cmd_go_files = (
            list((project_path / "cmd").glob("*.go")) if (project_path / "cmd").exists() else []
        )
        if cmd_go_files:
            return cmd_go_files[0]

        return project_path / "main.go"

    elif detected_language in ("c", "cpp"):
        entry_candidates = ["main.c", "main.cpp", "app.c", "app.cpp", "src/main.c", "src/main.cpp"]
        for candidate_path in entry_candidates:
            candidate_file = project_path / candidate_path
            if candidate_file.exists():
                return candidate_file

        c_files = list(project_path.glob("*.c"))
        cpp_files = list(project_path.glob("*.cpp")) + list(project_path.glob("*.cc"))
        if cpp_files:
            return cpp_files[0]
        elif c_files:
            return c_files[0]

        return project_path / "main.cpp"

    raise ValueError(f"Could not detect entry point for language: {detected_language}")


def detect_runtime_version(language: str) -> Optional[str]:
    try:
        if language == "python":
            result = subprocess.run(
                ["python3", "--version"], capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                version_match = re.search(r"Python (\d+\.\d+)", result.stdout.strip())
                if version_match:
                    return version_match.group(1)

        elif language in ["javascript", "typescript"]:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                version_match = re.search(r"v(\d+)", result.stdout.strip())
                if version_match:
                    return version_match.group(1)

        elif language == "rust":
            result = subprocess.run(
                ["rustc", "--version"], capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                version_match = re.search(r"rustc (\d+\.\d+)", result.stdout.strip())
                if version_match:
                    return version_match.group(1)

    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    return None


def get_docker_base_version(language: str, project_dir: Optional[Path] = None) -> str:
    detected_version = detect_runtime_version(language)

    if language == "python":
        version_string = detected_version or "3.12"
        return f"python:{version_string}-slim"

    elif language in ["javascript", "typescript"]:
        version_string = detected_version or "20"
        return f"node:{version_string}-slim"

    elif language == "rust":
        version_string = detected_version or "latest"
        return f"rust:{version_string}"

    elif language == "go":
        return "tinygo/tinygo:latest"

    elif language in ("c", "cpp"):
        return "ubuntu:22.04"

    return "ubuntu:22.04"


def supports_wasi_http(wasm_file: Path) -> bool:
    """
    Check if a WASM component implements wasi:http interfaces.

    Components that implement wasi:http can be served via HTTP using wasmtime serve.
    Library components that only export functions cannot be served.

    Args:
        wasm_file: Path to the .wasm or .wcmp file

    Returns:
        True if the component implements wasi:http, False otherwise
    """
    try:
        # Use wasm-tools to inspect the component's WIT interface
        result = subprocess.run(
            ["wasm-tools", "component", "wit", str(wasm_file)],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        if result.returncode == 0:
            # Check if the component imports or exports wasi:http interfaces
            output = result.stdout.lower()
            return "wasi:http" in output

        return False
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.SubprocessError):
        # If wasm-tools is not available or fails, assume it doesn't support HTTP
        # This is a safe default - better to skip serve.sh than generate a broken one
        return False


def get_component_exports(wasm_file: Path) -> List[str]:
    """
    Extract exported function names from a WASM component.

    Args:
        wasm_file: Path to the .wasm or .wcmp file

    Returns:
        List of exported function names
    """
    try:
        result = subprocess.run(
            ["wasm-tools", "component", "wit", str(wasm_file)],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        if result.returncode != 0:
            return []

        exported_funcs = []
        lines = result.stdout.split("\n")
        in_world = False
        brace_depth = 0

        for line in lines:
            stripped = line.strip()

            # Track when we're inside a world definition
            if "world" in stripped and "{" in stripped:
                in_world = True
                brace_depth = stripped.count("{") - stripped.count("}")
            elif in_world:
                # Track brace depth
                brace_depth += stripped.count("{") - stripped.count("}")

                # Look for exports - both functions and interfaces
                if stripped.startswith("export"):
                    # Extract the export name
                    after_export = stripped[6:].strip()  # Skip "export"

                    # Handle function exports: "export name: func(...)"
                    if ": func(" in stripped:
                        if ":" in after_export:
                            func_name = after_export.split(":")[0].strip()

                            # Validate function name
                            if (
                                func_name
                                and func_name not in exported_funcs
                                and "<" not in func_name
                                and ">" not in func_name
                                and not func_name.startswith("interface")
                                and func_name.replace("-", "")
                                .replace("_", "")
                                .replace("/", "")
                                .replace(":", "")
                                .isalnum()
                            ):
                                exported_funcs.append(func_name)

                    # Handle interface exports: "export wasi:cli/run@0.2.0;"
                    elif ";" in stripped or (":" in after_export and "/" in after_export):
                        # Extract interface name (e.g., "wasi:cli/run@0.2.0" -> "wasi:cli/run")
                        interface_name = after_export.rstrip(";").strip()
                        # Remove version if present
                        if "@" in interface_name:
                            interface_name = interface_name.split("@")[0]
                        if interface_name and interface_name not in exported_funcs:
                            exported_funcs.append(interface_name)

                # Exit when we've closed all braces
                if brace_depth <= 0 and stripped == "}":
                    break

        return exported_funcs
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.SubprocessError):
        return []
