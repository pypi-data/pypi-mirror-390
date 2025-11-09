# wasm-kit run command - Execute WASM components instantly.

import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from utils.wasm_component_runner import run_component_function, run_component_interactive
from utils.wasm_detect import get_component_exports, get_project_name
from utils.wasm_security import SecurityError, validate_project_path

console = Console()


@click.command(name="run")
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--invoke", "invoke_func", help="Invoke specific export (components)")
@click.argument("args", nargs=-1)
def run(path: str, invoke_func: Optional[str], args: tuple):
    """Run a WASM file instantly."""
    try:
        project_path = validate_project_path(Path(path), allow_parent=True)
    except SecurityError as e:
        console.print(f"Security error: {e}")
        sys.exit(1)

    # Find WASM file
    project_name = get_project_name(project_path)
    wasm_files = list(project_path.glob("*.wasm"))
    wasm_files.extend(list(project_path.glob("*.wcmp")))
    wasm_files.extend(list(project_path.glob("target/**/*.wasm")))

    if not wasm_files:
        console.print("Error: No WASM file found. Run wasm-kit build first.")
        sys.exit(1)

    wasm_file = wasm_files[0]
    if len(wasm_files) > 1:
        # Prefer project-named file, then out.wasm, then any in root
        for wf in wasm_files:
            if wf.name.startswith(f"{project_name}.") and wf.parent == project_path:
                wasm_file = wf
                break
        else:
            for wf in wasm_files:
                if wf.name == "out.wasm" and wf.parent == project_path:
                    wasm_file = wf
                    break
            else:
                for wf in wasm_files:
                    if wf.parent == project_path:
                        wasm_file = wf
                        break

    # Check for wasmtime
    try:
        subprocess.run(["wasmtime", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        console.print("Error: wasmtime not found.")
        console.print("Install: curl https://wasmtime.dev/install.sh | bash")
        sys.exit(1)

    # Determine if this is a component or standalone WASM
    # Heuristic 1: extension .wcmp
    is_component = wasm_file.suffix == ".wcmp" or wasm_file.name.endswith(".wcmp")
    # Heuristic 2: probe with wasm-tools (works for .wasm symlink pointing to component)
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
            pass

    # For components with --invoke, check if it's a library component first
    # Library components don't have wasi:cli/run, so wasmtime CLI --invoke won't work
    if is_component and invoke_func:
        # Check if it exports wasi:cli/run
        exports = get_component_exports(wasm_file)
        is_library_component = exports and "wasi:cli/run" not in exports

        if is_library_component:
            # Use wasmtime-py runner directly for library components
            console.print(
                f"[yellow]→[/yellow] Component '{wasm_file.name}' is a library component\n"
            )
            console.print(f"[dim]Calling function:[/dim] {invoke_func}({', '.join(args)})\n")
            exit_code = run_component_function(wasm_file, invoke_func, list(args))
            sys.exit(exit_code)

    # Run selection
    # If --invoke is provided, respect it regardless of extension
    if invoke_func:
        # Respect explicit function invocation for components
        cmd = ["wasmtime", "run", "--invoke", invoke_func, str(wasm_file)] + list(args)
    else:
        # Default execution path
        cmd = ["wasmtime", "run", str(wasm_file)] + list(args)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            # Check if it's the specific error about missing wasi:cli/run
            error_output = result.stderr.lower()
            if is_component and (
                ("no exported instance named" in error_output and "wasi:cli/run" in error_output)
                or "component" in error_output
            ):
                # Library component detected - use wasmtime-py runner
                console.print(
                    f"[yellow]→[/yellow] Component '{wasm_file.name}' is a library component\n"
                )

                # Check if specific function was requested with --invoke
                if invoke_func:
                    console.print(
                        f"[dim]Calling function:[/dim] {invoke_func}({', '.join(args)})\n"
                    )
                    exit_code = run_component_function(wasm_file, invoke_func, list(args))
                    sys.exit(exit_code)

                # Launch interactive component runner
                console.print("[dim]Launching interactive mode...[/dim]\n")
                exit_code = run_component_interactive(wasm_file)
                sys.exit(exit_code)
            else:
                # Print the actual error
                if result.stderr:
                    console.print(result.stderr, end="")
                if result.stdout:
                    console.print(result.stdout, end="")
                console.print(f"Error: Component execution failed (exit code {result.returncode})")
                sys.exit(result.returncode)
        else:
            # Print output if successful
            if result.stdout:
                console.print(result.stdout, end="")
            if result.stderr:
                console.print(result.stderr, end="")
    except KeyboardInterrupt:
        console.print("\nInterrupted")
        sys.exit(130)
