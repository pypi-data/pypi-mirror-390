# Enhanced error messages with actionable suggestions for wasm-kit.

from typing import Dict, Optional

from rich.console import Console

console = Console()


def print_error(error_type: str, context: Optional[Dict] = None) -> None:
    # Print enhanced error message with actionable fixes.
    error_lower = error_type.lower()

    if "docker" in error_lower and ("not found" in error_lower or "not running" in error_lower):
        console.print("\n[bold red]Error:[/bold red] Docker is not installed or not running")
        console.print("\n[cyan]Fix:[/cyan] Install Docker from https://docs.docker.com/get-docker/")
        console.print(
            "  [dim]# Ubuntu/Debian: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh[/dim]"
        )
        console.print("  [dim]# macOS: brew install --cask docker[/dim]")
        console.print("  [dim]# Then start Docker Desktop[/dim]")

    elif "language" in error_lower and "not detected" in error_lower:
        console.print("\n[bold red]Error:[/bold red] Could not detect project language")
        console.print(
            "\n[cyan]Fix:[/cyan] Make sure you're in the project directory with the right config file:"
        )
        console.print("  [dim]# Python: pyproject.toml or requirements.txt[/dim]")
        console.print("  [dim]# JavaScript: package.json[/dim]")
        console.print("  [dim]# Rust: Cargo.toml[/dim]")
        console.print("  [dim]# Go: go.mod[/dim]")
        console.print("  [dim]# C/C++: .c or .cpp files[/dim]")
        console.print("\n  [dim]Or initialize a new project: wasm-kit init python[/dim]")

    elif "wit" in error_lower and "not found" in error_lower:
        console.print(
            "\n[bold red]Error:[/bold red] WIT file not found (required for component builds)"
        )
        console.print("\n[cyan]Fix:[/cyan] Create a WIT file:")
        console.print("  [dim]wasm-kit init wit[/dim]")
        console.print("\n  [dim]Or create wit/world.wit manually[/dim]")

    elif "permission" in error_lower or "denied" in error_lower:
        console.print("\n[bold red]Error:[/bold red] Permission denied when writing files")
        console.print("\n[cyan]Fix:[/cyan] Docker may have created files as root:")
        console.print("  [dim]sudo chown -R $USER:$USER .[/dim]")

    elif "build failed" in error_lower:
        console.print("\n[bold red]Error:[/bold red] Build process failed")
        console.print("\n[cyan]Fix:[/cyan] Check the error output above for specific issues")
        console.print(
            "  [dim]Common fixes: check dependencies, verify Docker is running, check file permissions[/dim]"
        )
        console.print("  [dim]Try: wasm-kit build . --verbose[/dim]")

    else:
        console.print(f"\n[bold red]Error:[/bold red] {error_type}")
        if context:
            for key, value in context.items():
                console.print(f"  [dim]{key}: {value}[/dim]")
