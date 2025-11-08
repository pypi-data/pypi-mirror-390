# wasm-kit serve command - Serve WASM components via HTTP.

import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console

from utils.wasm_detect import get_component_exports, get_project_name, supports_wasi_http
from utils.wasm_security import SecurityError, validate_project_path

console = Console()


@click.command(name="serve")
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--port", "-p", default=8080, help="HTTP port to serve on")
@click.option("--host", default="0.0.0.0", help="Host to bind to")
def serve(path: str, port: int, host: str):
    """
    Serve a WASM component via HTTP.

    Auto-detects and serves the built .wasm file in the project directory.

    Examples:
      wasm-kit serve
      wasm-kit serve ./my-project
      wasm-kit serve --port 3000
    """
    try:
        # Validate project path for security
        project_path = validate_project_path(Path(path), allow_parent=True)
    except SecurityError as e:
        console.print(f"Security error: {e}")
        sys.exit(1)

    # Find WASM file - prefer project_name.wasm, fallback to out.wasm for backward compatibility
    project_name = get_project_name(project_path)
    wasm_files = list(project_path.glob("*.wasm"))
    wasm_files.extend(list(project_path.glob("*.wcmp")))

    if not wasm_files:
        console.print("Error: No WASM file found. Run: wasm-kit build .")
        sys.exit(1)

    # Prefer project_name.wasm, then out.wasm (backward compatibility), then any other file
    wasm_file = wasm_files[0]
    for wf in wasm_files:
        if wf.name.startswith(f"{project_name}.") and wf.parent == project_path:
            wasm_file = wf
            break
    else:
        for wf in wasm_files:
            if wf.name == "out.wasm" and wf.parent == project_path:
                wasm_file = wf
                break

    # Check for wasmtime
    try:
        subprocess.run(["wasmtime", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        console.print("Error: wasmtime not found.")
        console.print("Install: curl https://wasmtime.dev/install.sh | bash")
        sys.exit(1)

    # Only component model with wasi-http proxy is supported by wasmtime serve
    # Detect component both by extension and by probing with wasm-tools (for .wasm symlink)
    is_component = wasm_file.suffix == ".wcmp" or wasm_file.name.endswith(".wcmp")
    if not is_component:
        try:
            probe = subprocess.run(
                ["wasm-tools", "component", "wit", str(wasm_file)],
                capture_output=True,
                text=True,
                timeout=3,
            )
            is_component = probe.returncode == 0
        except Exception:
            is_component = False
    if not is_component:
        console.print(
            "Error: The serve command requires a component. Rebuild without --type standalone (default)."
        )
        sys.exit(1)

    # Validate that the component supports wasi:http before attempting to serve
    if not supports_wasi_http(wasm_file):
        console.print(f"[red]Error:[/red] Component '{wasm_file.name}' doesn't implement wasi:http")
        console.print("\n[yellow]Why this fails:[/yellow]")
        console.print(
            "  • [bold]wasmtime serve[/bold] only works with components that implement the wasi:http interface"
        )
        console.print("  • Your component is a library component that exports functions")
        console.print("  • It cannot handle HTTP requests directly")

        # Show available exports
        exports = get_component_exports(wasm_file)
        if exports:
            console.print(f"\n[bold]Available functions:[/bold] {', '.join(exports)}")

        console.print("\n[bold]How to use this component:[/bold]")
        console.print("\n1. [bold]Call from a host program[/bold] (Recommended)")
        console.print("   Create a program that instantiates the component and calls its functions")
        console.print("\n2. [bold]Use jco (JavaScript bindings)[/bold]")
        console.print(f"   jco transpile {wasm_file.name} -o ./js-component")
        console.print("   npm install -g @bytecodealliance/jco")
        console.print("\n3. [bold]Wrap in a wasi:http component[/bold]")
        console.print(
            "   Create a new component that implements wasi:http and calls your functions"
        )
        console.print("\n4. [bold]See component interface:[/bold]")
        console.print(f"   wasm-tools component wit {wasm_file.name}")

        sys.exit(1)

    console.print(f"Serving {wasm_file.name} on http://{host}:{port}")
    console.print("Press Ctrl+C to stop\n")

    cmd = ["wasmtime", "serve", str(wasm_file), "--addr", f"{host}:{port}"]

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        console.print("\nServer stopped")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        console.print(f"Error: Server failed to start (exit code {e.returncode})")
        sys.exit(e.returncode)
