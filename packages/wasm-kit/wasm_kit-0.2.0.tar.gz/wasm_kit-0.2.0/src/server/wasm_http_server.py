"""
Custom HTTP server for serving WASM components.

This server can serve ANY WASM component by:
1. Auto-discovering exported functions
2. Creating REST API endpoints for each function
3. Providing Swagger UI for API documentation
4. Supporting hot-reload when WASM file changes
"""

import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS
from rich.console import Console
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

console = Console()


class WasmComponentInstance:
    """Wrapper around a WASM component instance using wasmtime-py."""

    def __init__(self, wasm_file: Path):
        self.wasm_file = wasm_file
        self.store = None
        self.instance = None
        self.exports = []
        self._load_component()

    def _load_component(self):
        """Load and instantiate the WASM component."""
        try:
            from wasmtime import Config, Engine, Linker, Store

            # Try multiple import paths for Component (API changed across versions)
            Component = None
            component_model_supported = False

            # Try all known locations for Component API
            import_attempts = [
                lambda: __import__(
                    "wasmtime", fromlist=["Component"]
                ).Component,  # wasmtime.Component
                lambda: __import__(
                    "wasmtime._component", fromlist=["Component"]
                ).Component,  # wasmtime._component.Component
                lambda: __import__(
                    "wasmtime.loader", fromlist=["Component"]
                ).Component,  # wasmtime.loader.Component
            ]

            for attempt in import_attempts:
                try:
                    Component = attempt()
                    component_model_supported = True
                    break
                except (ImportError, AttributeError):
                    continue

            if not component_model_supported or Component is None:
                # Check wasmtime version
                import wasmtime

                version = getattr(wasmtime, "__version__", "unknown")
                raise ImportError(
                    f"wasmtime Component Model support not available (version: {version}).\n"
                    "The Component API location may have changed.\n"
                    "Try: pip install --upgrade wasmtime\n"
                    "Or check: https://github.com/bytecodealliance/wasmtime-py"
                )

            # Setup wasmtime
            config = Config()
            try:
                config.wasm_component_model = True  # type: ignore[attr-defined]
            except AttributeError:
                # Older wasmtime version, try alternative
                try:
                    config.component_model = True  # type: ignore[attr-defined]
                except AttributeError:
                    raise ImportError("wasmtime version does not support Component Model")

            engine = Engine(config)
            linker = Linker(engine)

            # Add WASI support
            try:
                import wasmtime_wasi

                wasmtime_wasi.add_to_linker_sync(linker)

                wasi_ctx = wasmtime_wasi.WasiCtxBuilder()
                wasi_ctx.inherit_stdio()
                wasi_ctx.inherit_env()
                wasi_ctx.preopened_dir(".", ".", dir_perms=wasmtime_wasi.DirPerms.all())

                self.store = Store(engine)
                self.store.set_wasi(wasi_ctx.build())
            except (ImportError, AttributeError):
                self.store = Store(engine)

            # Load component
            with open(self.wasm_file, "rb") as f:
                component = Component(engine, f.read())

            # Instantiate
            self.instance = linker.instantiate(self.store, component)
            instance_exports = self.instance.exports(self.store)

            # Get exported function names (filter out internal functions)
            self.exports = [
                name for name in instance_exports.keys() if not name.startswith("cabi_")
            ]

        except Exception as e:
            console.print(f"[red]Error loading component:[/red] {e}")
            raise

    def call_function(self, function_name: str, args: List[Any]) -> Any:
        """Call a function on the component."""
        if not self.instance or not self.store:
            raise RuntimeError("Component not loaded")

        instance_exports = self.instance.exports(self.store)

        if function_name not in instance_exports:
            raise ValueError(f"Function '{function_name}' not found")

        func = instance_exports[function_name]
        result = func(self.store, *args)  # type: ignore[operator]

        return result

    def reload(self):
        """Reload the component from disk."""
        self._load_component()


class WasmFileChangeHandler(FileSystemEventHandler):
    """Watch for changes to WASM files and trigger reload."""

    def __init__(self, wasm_file: Path, on_change_callback):
        self.wasm_file = wasm_file
        self.on_change_callback = on_change_callback
        self.last_modified = 0

    def on_modified(self, event):
        if event.src_path == str(self.wasm_file):
            # Debounce rapid changes
            current_time = time.time()
            if current_time - self.last_modified > 1:
                self.last_modified = current_time
                console.print("\n[yellow]WASM file changed, reloading...[/yellow]")
                self.on_change_callback()


class WasmHttpServer:
    """HTTP server for WASM components with auto-generated API."""

    def __init__(self, wasm_file: Path, host: str = "0.0.0.0", port: int = 8080):
        self.wasm_file = wasm_file
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend integration

        self.component: Optional[WasmComponentInstance] = None
        self.function_signatures: Dict[str, Dict[str, Any]] = {}

        self._setup_routes()
        self._load_component()
        self._parse_function_signatures()

    def _load_component(self):
        """Load or reload the WASM component."""
        try:
            self.component = WasmComponentInstance(self.wasm_file)
            console.print(f"[green]✓[/green] Component loaded: {self.wasm_file.name}")
        except Exception as e:
            console.print(f"[red]Failed to load component:[/red] {e}")
            raise

    def _parse_function_signatures(self):
        """Parse WIT to extract function signatures."""
        try:
            result = subprocess.run(
                ["wasm-tools", "component", "wit", str(self.wasm_file)],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return

            # Parse WIT output to extract function signatures
            lines = result.stdout.split("\n")
            in_world = False

            for line in lines:
                stripped = line.strip()

                if "world" in stripped and "{" in stripped:
                    in_world = True
                elif in_world and stripped.startswith("export") and ": func(" in stripped:
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

                            self.function_signatures[func_name] = {
                                "params": params,
                                "returns": returns,
                                "signature": stripped,
                            }
                    except Exception:
                        pass

        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Could not parse function signatures: {e}")

    def _setup_routes(self):
        """Setup Flask routes."""

        @self.app.route("/")
        def index():
            """API homepage with links to documentation."""
            return jsonify(
                {
                    "service": "WASM Component API",
                    "component": self.wasm_file.name,
                    "docs": "/docs",
                    "api": "/api",
                    "openapi": "/openapi.json",
                }
            )

        @self.app.route("/api", methods=["GET"])
        def list_functions():
            """List all available functions."""
            if not self.component:
                return jsonify({"error": "Component not loaded"}), 500

            functions = []
            for func_name in self.component.exports:
                sig = self.function_signatures.get(func_name, {})
                functions.append(
                    {
                        "name": func_name,
                        "endpoint": f"/api/{func_name}",
                        "method": "POST",
                        "params": sig.get("params", []),
                        "returns": sig.get("returns", "unknown"),
                    }
                )

            return jsonify({"functions": functions})

        @self.app.route("/api/<function_name>", methods=["POST"])
        def call_function(function_name: str):
            """Call a function on the component."""
            if not self.component:
                return jsonify({"error": "Component not loaded"}), 500

            # Get request data
            data = request.get_json() or {}
            args = data.get("args", [])

            # Ensure args is a list
            if not isinstance(args, list):
                return jsonify({"error": "args must be a list"}), 400

            try:
                result = self.component.call_function(function_name, args)

                # Handle Result<T, E> types
                if isinstance(result, dict):
                    if "ok" in result:
                        return jsonify({"status": "ok", "result": result["ok"]})
                    elif "err" in result:
                        return jsonify({"status": "error", "error": result["err"]}), 400

                return jsonify({"status": "ok", "result": result})

            except ValueError as e:
                return jsonify({"error": str(e)}), 404
            except Exception as e:
                return jsonify({"error": f"Execution error: {str(e)}"}), 500

        @self.app.route("/openapi.json")
        def openapi_spec():
            """Generate OpenAPI specification."""
            paths = {}

            for func_name in self.component.exports if self.component else []:
                sig = self.function_signatures.get(func_name, {})
                params = sig.get("params", [])

                # Build request schema
                properties = {}
                for param in params:
                    properties[param["name"]] = {
                        "type": self._wit_type_to_json_type(param["type"]),
                        "description": f"Parameter of type {param['type']}",
                    }

                paths[f"/api/{func_name}"] = {
                    "post": {
                        "summary": f"Call {func_name}",
                        "description": sig.get("signature", f"Call the {func_name} function"),
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "args": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                                "description": "Function arguments",
                                            }
                                        },
                                    }
                                }
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "status": {"type": "string"},
                                                "result": {"type": "string"},
                                            },
                                        }
                                    }
                                },
                            }
                        },
                    }
                }

            spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": f"WASM Component API - {self.wasm_file.name}",
                    "version": "1.0.0",
                    "description": "Auto-generated API for WASM component functions",
                },
                "servers": [{"url": f"http://{self.host}:{self.port}"}],
                "paths": paths,
            }

            return jsonify(spec)

        @self.app.route("/docs")
        def swagger_ui():
            """Serve Swagger UI for API documentation."""
            html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WASM Component API Documentation</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <style>
        body { margin: 0; padding: 0; }
        #swagger-ui { max-width: 1460px; margin: 0 auto; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: '/openapi.json',
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
        });
    </script>
</body>
</html>
            """
            return html

        @self.app.route("/reload", methods=["POST"])
        def reload_component():
            """Manually trigger component reload."""
            try:
                self._load_component()
                self._parse_function_signatures()
                return jsonify({"status": "ok", "message": "Component reloaded"})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def _wit_type_to_json_type(self, wit_type: str) -> str:
        """Convert WIT type to JSON Schema type."""
        type_map = {
            "string": "string",
            "s8": "integer",
            "s16": "integer",
            "s32": "integer",
            "s64": "integer",
            "u8": "integer",
            "u16": "integer",
            "u32": "integer",
            "u64": "integer",
            "f32": "number",
            "f64": "number",
            "bool": "boolean",
        }
        return type_map.get(wit_type, "string")

    def start_with_watch(self, watch: bool = False):
        """Start the server with optional file watching."""
        if watch:
            # Setup file watcher
            event_handler = WasmFileChangeHandler(self.wasm_file, self._on_file_change)
            observer = Observer()
            observer.schedule(event_handler, str(self.wasm_file.parent), recursive=False)
            observer.start()

            console.print(f"[green]✓[/green] Watching for changes to {self.wasm_file.name}")

            try:
                self._start_server()
            finally:
                observer.stop()
                observer.join()
        else:
            self._start_server()

    def _on_file_change(self):
        """Handle file change event."""
        try:
            self._load_component()
            self._parse_function_signatures()
            console.print("[green]✓[/green] Component reloaded successfully")
        except Exception as e:
            console.print(f"[red]Failed to reload:[/red] {e}")

    def _start_server(self):
        """Start the Flask server."""
        console.print("\n[bold green]WASM Component Server Running[/bold green]")
        console.print(f"Component: [cyan]{self.wasm_file.name}[/cyan]")
        console.print(f"URL: [cyan]http://{self.host}:{self.port}[/cyan]")
        console.print(f"API Docs: [cyan]http://{self.host}:{self.port}/docs[/cyan]")
        console.print(f"API Endpoints: [cyan]http://{self.host}:{self.port}/api[/cyan]\n")

        if self.component:
            console.print("[bold]Available functions:[/bold]")
            for func_name in self.component.exports:
                sig = self.function_signatures.get(func_name, {})
                params = sig.get("params", [])
                params_str = ", ".join(f"{p['name']}: {p['type']}" for p in params)
                returns = sig.get("returns", "unknown")
                console.print(f"  • [cyan]{func_name}[/cyan]({params_str}) -> {returns}")

        console.print("\nPress Ctrl+C to stop\n")

        # Run Flask app
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
