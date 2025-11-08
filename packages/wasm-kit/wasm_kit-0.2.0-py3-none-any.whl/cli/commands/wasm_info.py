# wasm-kit info command - Show system information.

import click
from rich.console import Console

from utils import check_command_available, check_docker_available

console = Console()


@click.command(name="info")
def info():
    # Show system information and available tools.
    console.print("wasm-kit v0.1.0")
    console.print("WebAssembly build tool\n")

    console.print("Available Tools:\n")

    tools = {
        "Rust": ["rustc", "cargo", "cargo-component"],
        "JavaScript/TypeScript": ["node", "npm", "jco", "componentize-js"],
        "Python": ["python", "pip", "componentize-py"],
        "WASM Tools": ["wasmtime", "wasm-tools"],
        "Docker": ["docker"],
    }

    for category, commands in tools.items():
        console.print(f"{category}:")
        for cmd in commands:
            available = check_command_available(cmd)
            status = "[OK]" if available else "[--]"
            console.print(f"  {status} {cmd}")
        console.print()

    # Docker status
    docker_available = check_docker_available()
    status = "Available" if docker_available else "Not available"
    console.print(f"Docker Runtime: {status}")

    console.print("\nNote: Missing tools can be replaced with Docker builds")
