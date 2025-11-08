# wasm-kit dev - Development server with auto-build and hot-reload

import sys
from pathlib import Path

import click
from rich.console import Console

from utils.wasm_security import SecurityError, validate_project_path

console = Console()


@click.command(name="dev")
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--port", "-p", default=8080, help="HTTP port to serve on")
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option(
    "--build-only",
    is_flag=True,
    help="Only watch and build, don't serve",
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    help="Enable debug mode with verbose output",
)
def dev(path: str, port: int, host: str, build_only: bool, debug: bool):
    """Start development server with auto-build and hot-reload."""
    try:
        project_path = validate_project_path(Path(path), allow_parent=True)
    except SecurityError as e:
        console.print(f"  [red]error:[/red] {e}")
        sys.exit(1)

    try:
        from engine.wasm_dev_server import WasmDevServer

        # Create and start dev server
        dev_server = WasmDevServer(
            project_path=project_path,
            port=port,
            host=host,
            build_only=build_only,
            debug=debug,
        )

        dev_server.start()

    except ImportError:
        console.print("  [yellow]error:[/yellow] dev server not available")
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        console.print(f"\n  [red]error:[/red] {e}")
        sys.exit(1)
