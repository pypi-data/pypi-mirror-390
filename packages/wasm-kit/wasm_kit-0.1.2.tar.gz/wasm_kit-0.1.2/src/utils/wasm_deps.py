import json
import re
from pathlib import Path
from typing import Dict

try:
    import tomli  # type: ignore
except ImportError:
    try:
        import tomllib as tomli  # type: ignore
    except ImportError:
        tomli = None  # type: ignore


def get_python_deps(project_dir: Path) -> Dict[str, str]:
    dependency_versions = {}
    project_path = Path(project_dir).resolve()

    pyproject_file = project_path / "pyproject.toml"
    if pyproject_file.exists() and tomli:
        try:
            with open(pyproject_file, "rb") as f:
                pyproject_data = tomli.load(f)

            project_dependencies = pyproject_data.get("project", {}).get("dependencies", [])
            for dependency_spec in project_dependencies:
                dependency_lower = dependency_spec.lower()
                if "componentize-py" in dependency_lower:
                    dependency_versions["componentize_py"] = _extract_version(dependency_spec)
                elif "wasmtime" in dependency_lower:
                    dependency_versions["wasmtime"] = _extract_version(dependency_spec)

            optional_dependencies = pyproject_data.get("project", {}).get(
                "optional-dependencies", {}
            )
            for group_name, group_dependencies in optional_dependencies.items():
                for dependency_spec in group_dependencies:
                    dependency_lower = dependency_spec.lower()
                    if "componentize-py" in dependency_lower:
                        dependency_versions["componentize_py"] = _extract_version(dependency_spec)
                    elif "wasmtime" in dependency_lower:
                        dependency_versions["wasmtime"] = _extract_version(dependency_spec)
        except Exception:
            pass

    if not dependency_versions:
        requirements_file = project_path / "requirements.txt"
        if requirements_file.exists():
            try:
                with open(requirements_file) as f:
                    for line in f:
                        line_stripped = line.strip()
                        if not line_stripped or line_stripped.startswith("#"):
                            continue
                        line_lower = line_stripped.lower()
                        if "componentize-py" in line_lower:
                            dependency_versions["componentize_py"] = _extract_version(line_stripped)
                        elif "wasmtime" in line_lower:
                            dependency_versions["wasmtime"] = _extract_version(line_stripped)
            except Exception:
                pass

    return dependency_versions


def get_js_deps(project_dir: Path) -> Dict[str, str]:
    dependency_versions = {}
    project_path = Path(project_dir).resolve()

    package_json_file = project_path / "package.json"
    if package_json_file.exists():
        try:
            with open(package_json_file) as f:
                package_data = json.load(f)

            all_dependencies = {}
            all_dependencies.update(package_data.get("dependencies", {}))
            all_dependencies.update(package_data.get("devDependencies", {}))
            all_dependencies.update(package_data.get("optionalDependencies", {}))

            for package_name, version_spec in all_dependencies.items():
                package_lower = package_name.lower()
                if (
                    "componentize-js" in package_lower
                    or package_name == "@bytecodealliance/componentize-js"
                ):
                    dependency_versions["componentize_js"] = _normalize_npm_version(version_spec)
                elif "jco" in package_lower or package_name == "@bytecodealliance/jco":
                    dependency_versions["jco"] = _normalize_npm_version(version_spec)
        except Exception:
            pass

    return dependency_versions


def get_rust_deps(project_dir: Path) -> Dict[str, str]:
    dependency_versions = {}
    project_path = Path(project_dir).resolve()

    cargo_toml_file = project_path / "Cargo.toml"
    if cargo_toml_file.exists() and tomli:
        try:
            with open(cargo_toml_file, "rb") as f:
                tomli.load(f)  # Validate file is parseable
            dependency_versions["cargo_component"] = "*"
            dependency_versions["wasm_tools"] = "*"
        except Exception:
            pass

    return (
        dependency_versions if dependency_versions else {"cargo_component": "*", "wasm_tools": "*"}
    )


def _extract_version(dependency_string: str) -> str:
    exact_match = re.search(r"==\s*([^\s,\]]+)", dependency_string)
    if exact_match:
        return exact_match.group(1).strip()

    comparison_match = re.search(r"(>=|<=|~=|>|<)\s*([^\s,\]]+)", dependency_string)
    if comparison_match:
        return comparison_match.group(2).strip()

    return "*"


def _normalize_npm_version(version_string: str) -> str:
    cleaned_version = re.sub(r"^[\^~>=<]+", "", version_string).strip()
    return cleaned_version if cleaned_version and cleaned_version != "*" else "*"


def get_dependencies(project_dir: Path, language: str) -> Dict[str, str]:
    project_path = Path(project_dir).resolve()

    if language == "python":
        return get_python_deps(project_path)
    elif language in ("javascript", "typescript"):
        return get_js_deps(project_path)
    elif language == "rust":
        return get_rust_deps(project_path)
    else:
        return {}
