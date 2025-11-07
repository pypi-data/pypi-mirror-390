# Utilities for wasm-kit

import shutil

from rich.console import Console

from .wasm_detect import (
    detect_entry,
    detect_language,
    detect_wit,
    get_project_name,
    parse_world_name,
)
from .wasm_errors import print_error
from .wasm_logger import BuildLogger, Logger, get_logger, set_logger
from .wasm_script import generate_both_scripts, generate_run_script, generate_serve_script
from .wasm_welcome import is_first_run, mark_first_run_complete, show_welcome
from .wasm_wit import find_wit_files, generate_wit_file, parse_wit_file

console = Console()


class WasmKitError(Exception):
    pass


class LanguageNotDetectedError(WasmKitError):
    pass


class BuildError(WasmKitError):
    pass


def check_command_available(command: str) -> bool:
    return shutil.which(command) is not None


def check_docker_available() -> bool:
    try:
        import docker

        docker_client = docker.from_env()  # type: ignore[attr-defined]
        docker_client.ping()
        return True
    except Exception:
        return False


def format_size(size_bytes: int) -> str:
    size_float = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size_float < 1024.0:
            return f"{size_float:.2f} {unit}"
        size_float /= 1024.0
    return f"{size_float:.2f} TB"


__all__ = [
    "detect_language",
    "detect_entry",
    "detect_wit",
    "get_project_name",
    "parse_world_name",
    "generate_run_script",
    "generate_serve_script",
    "generate_both_scripts",
    "parse_wit_file",
    "generate_wit_file",
    "find_wit_files",
    "Logger",
    "get_logger",
    "set_logger",
    "BuildLogger",
    "WasmKitError",
    "LanguageNotDetectedError",
    "BuildError",
    "check_command_available",
    "check_docker_available",
    "format_size",
    "print_error",
    "show_welcome",
    "is_first_run",
    "mark_first_run_complete",
    "console",
]
