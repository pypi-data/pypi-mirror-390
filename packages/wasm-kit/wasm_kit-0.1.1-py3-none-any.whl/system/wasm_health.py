"""
Health check and environment diagnostics for wasm-kit.
"""

from typing import Any, Dict

from utils import check_command_available, check_docker_available


def check_environment() -> Dict[str, Any]:
    """
    Check the environment for available build tools.

    Returns:
        dict: Dictionary of tool availability

    Example:
        >>> from wasmkit.system.wasm_health import check_environment
        >>> env = check_environment()
        >>> if env['docker']:
        ...     print("Docker is available!")
    """
    return {
        "docker": check_docker_available(),
        "rust": {
            "rustc": check_command_available("rustc"),
            "cargo": check_command_available("cargo"),
            "cargo_component": check_command_available("cargo-component"),
        },
        "javascript": {
            "node": check_command_available("node"),
            "npm": check_command_available("npm"),
            "jco": check_command_available("jco"),
            "componentize_js": check_command_available("componentize-js"),
        },
        "python": {
            "python": check_command_available("python") or check_command_available("python3"),
            "pip": check_command_available("pip") or check_command_available("pip3"),
            "componentize_py": check_command_available("componentize-py"),
        },
        "wasm_tools": {
            "wasmtime": check_command_available("wasmtime"),
            "wasm_tools": check_command_available("wasm-tools"),
        },
    }
