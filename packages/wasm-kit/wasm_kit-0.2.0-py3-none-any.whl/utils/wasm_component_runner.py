# Component runner using wasmtime for executing WASM components

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()


def parse_wit_exports(wasm_file: Path) -> List[Dict[str, Any]]:
    import subprocess

    try:
        result = subprocess.run(
            ["wasm-tools", "component", "wit", str(wasm_file)],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            return []

        exports = []
        lines = result.stdout.split("\n")
        in_world = False
        brace_depth = 0

        for line in lines:
            stripped = line.strip()

            if "world" in stripped and "{" in stripped:
                in_world = True
                brace_depth = stripped.count("{") - stripped.count("}")
            elif in_world:
                brace_depth += stripped.count("{") - stripped.count("}")

                # Parse export line: "export name: func(params) -> return"
                if stripped.startswith("export") and ": func(" in stripped:
                    try:
                        # Extract function signature
                        after_export = stripped[6:].strip()  # Skip "export"
                        func_name = after_export.split(":")[0].strip()

                        # Extract params and return type
                        sig_part = after_export.split(":", 1)[1].strip()
                        if sig_part.startswith("func("):
                            # Parse parameters
                            params_str = sig_part[5 : sig_part.find(")")].strip()
                            params = []
                            if params_str:
                                for param in params_str.split(","):
                                    param = param.strip()
                                    if ":" in param:
                                        pname, ptype = param.split(":", 1)
                                        params.append(
                                            {"name": pname.strip(), "type": ptype.strip()}
                                        )

                            # Parse return type
                            returns = "unit"
                            if "->" in sig_part:
                                returns = sig_part.split("->", 1)[1].strip().rstrip(";")

                            exports.append(
                                {
                                    "name": func_name,
                                    "params": params,
                                    "returns": returns,
                                    "signature": stripped,
                                }
                            )
                    except Exception:
                        pass

                if brace_depth <= 0 and stripped == "}":
                    break

        return exports
    except Exception:
        return []


def run_component_interactive(wasm_file: Path) -> int:
    """
    Run a component in interactive mode, allowing function calls.

    Uses wasmtime-py to properly instantiate the component and call functions.
    """
    try:
        from wasmtime import Config, Engine, Linker, Store
    except ImportError:
        console.print("[red]Error:[/red] wasmtime package not installed")
        console.print("Install: pip install wasmtime")
        return 1

    # Try to import Component - may not be available in all versions
    try:
        # Try modern wasmtime API
        try:
            from wasmtime import Component  # type: ignore[attr-defined]
        except ImportError:
            # Try older API paths
            try:
                from wasmtime._component import Component  # type: ignore[import]
            except ImportError:
                # Component Model not supported
                console.print(
                    "[yellow]Error:[/yellow] Component Model not supported in installed wasmtime version"
                )
                console.print(
                    "\n[bold]Component Model support requires wasmtime-py with bindgen:[/bold]"
                )
                console.print("  pip install 'wasmtime[bindgen]'")
                console.print("\nOr use alternative approaches:")
                console.print(f"  1. Use jco: jco transpile {wasm_file.name} -o ./js-bindings")
                console.print("  2. Create a Rust/Python host program")
                console.print(f"  3. See: wasm-tools component wit {wasm_file.name}")
                return 1
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load Component API: {e}")
        return 1

    # Parse available functions
    exports = parse_wit_exports(wasm_file)
    if not exports:
        console.print(f"[red]Error:[/red] Could not parse exports from {wasm_file.name}")
        return 1

    # Display available functions
    console.print(f"\n[bold]Component:[/bold] {wasm_file.name}\n")

    table = Table(title="Available Functions", show_header=True)
    table.add_column("Function", style="cyan")
    table.add_column("Parameters", style="yellow")
    table.add_column("Returns", style="green")

    for export in exports:
        params_str = ", ".join(f"{p['name']}: {p['type']}" for p in export["params"])
        table.add_row(export["name"], params_str or "(none)", export["returns"])

    console.print(table)  # type: ignore[arg-type]
    console.print()

    # Setup wasmtime
    try:
        config = Config()
        config.wasm_component_model = True  # type: ignore[attr-defined]
        engine = Engine(config)

        linker = Linker(engine)

        # Add WASI support
        try:
            import wasmtime_wasi

            wasmtime_wasi.add_to_linker_sync(linker)

            # Create WASI context with filesystem access
            wasi_ctx = wasmtime_wasi.WasiCtxBuilder()
            wasi_ctx.inherit_stdio()
            wasi_ctx.inherit_env()

            # Allow filesystem access to current directory
            wasi_ctx.preopened_dir(".", ".", dir_perms=wasmtime_wasi.DirPerms.all())

            store = Store(engine)
            store.set_wasi(wasi_ctx.build())
        except (ImportError, AttributeError):
            # Fallback without WASI
            console.print(
                "[yellow]Warning:[/yellow] wasmtime-wasi not available, running without WASI support"
            )
            store = Store(engine)

        # Load component
        with open(wasm_file, "rb") as f:
            component = Component(engine, f.read())

        # Instantiate
        instance = linker.instantiate(store, component)
        instance_exports = instance.exports(store)

        console.print("[green]✓[/green] Component loaded successfully\n")
        console.print("[dim]Enter function calls in format: function-name arg1 arg2 ...[/dim]")
        console.print("[dim]Or type 'exit' to quit[/dim]\n")

        # Interactive loop
        while True:
            try:
                user_input = Prompt.ask("[bold cyan]>[/bold cyan]").strip()

                if user_input.lower() in ("exit", "quit", "q"):
                    break

                if not user_input:
                    continue

                # Parse command
                parts = user_input.split()
                func_name = parts[0]
                args = parts[1:] if len(parts) > 1 else []

                # Find function
                if func_name not in instance_exports:
                    console.print(f"[red]Error:[/red] Function '{func_name}' not found")
                    continue

                # Call function
                func = instance_exports[func_name]
                try:
                    result = func(store, *args)  # type: ignore[operator]

                    # Handle result types (ok/err for Result<T, E>)
                    if isinstance(result, dict):
                        if "ok" in result:
                            console.print(f"[green]✓ Ok:[/green] {result['ok']}")
                        elif "err" in result:
                            console.print(f"[red]✗ Error:[/red] {result['err']}")
                        else:
                            console.print(f"[blue]→[/blue] {result}")
                    elif isinstance(result, (list, tuple)):
                        console.print(f"[blue]→[/blue] {result}")
                    else:
                        console.print(f"[blue]→[/blue] {result}")

                except Exception as e:
                    console.print(f"[red]Error calling function:[/red] {e}")

            except KeyboardInterrupt:
                console.print("\n")
                break
            except EOFError:
                break

        console.print("\n[dim]Goodbye![/dim]")
        return 0

    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to load component: {e}")
        import traceback

        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return 1


def run_component_function(wasm_file: Path, function_name: str, args: List[str]) -> int:
    """
    Run a specific function from a component with arguments.
    """
    try:
        from wasmtime import Config, Engine, Linker, Store
        from wasmtime._component import Component  # type: ignore[import]
    except ImportError:
        console.print("[red]Error:[/red] wasmtime package not installed")
        console.print("Install: pip install wasmtime")
        return 1

    try:
        # Setup
        config = Config()
        config.wasm_component_model = True  # type: ignore[attr-defined]
        engine = Engine(config)
        linker = Linker(engine)

        # Add WASI
        try:
            import wasmtime_wasi

            wasmtime_wasi.add_to_linker_sync(linker)

            wasi_ctx = wasmtime_wasi.WasiCtxBuilder()
            wasi_ctx.inherit_stdio()
            wasi_ctx.inherit_env()
            wasi_ctx.preopened_dir(".", ".", dir_perms=wasmtime_wasi.DirPerms.all())

            store = Store(engine)
            store.set_wasi(wasi_ctx.build())
        except (ImportError, AttributeError):
            store = Store(engine)

        # Load and instantiate
        with open(wasm_file, "rb") as f:
            component = Component(engine, f.read())

        instance = linker.instantiate(store, component)
        exports = instance.exports(store)

        # Call function
        if function_name not in exports:
            console.print(f"[red]Error:[/red] Function '{function_name}' not found")
            available = [k for k in exports.keys() if not k.startswith("cabi_")]
            console.print(f"[dim]Available:[/dim] {', '.join(available)}")
            return 1

        func = exports[function_name]
        result = func(store, *args)  # type: ignore[operator]

        # Display result
        if isinstance(result, dict):
            if "ok" in result:
                value = result["ok"]
                if isinstance(value, list):
                    for item in value:
                        console.print(item)
                else:
                    console.print(value)
            elif "err" in result:
                console.print(f"[red]Error:[/red] {result['err']}")
                sys.stderr.write(f"Error: {result['err']}\n")
                return 1
            else:
                console.print(json.dumps(result, indent=2))
        else:
            console.print(result)

        return 0

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return 1
