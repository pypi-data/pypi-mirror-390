# HTTP server for WASM components with REST API

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, request
from flask_cors import CORS
from rich.console import Console

console = Console()


class WasmComponentCLI:
    def __init__(self, wasm_file: Path):
        self.wasm_file = wasm_file
        self.exports = []
        self._discover_exports()

    def _discover_exports(self):
        # Try wasm-tools first
        try:
            result = subprocess.run(
                ["wasm-tools", "component", "wit", str(self.wasm_file)],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                lines = result.stdout.split("\n")
                in_world = False

                for line in lines:
                    stripped = line.strip()

                    if "world" in stripped and "{" in stripped:
                        in_world = True
                    elif in_world and stripped.startswith("export") and ": func(" in stripped:
                        try:
                            after_export = stripped[6:].strip()
                            func_name = after_export.split(":")[0].strip()
                            self.exports.append(func_name)
                        except Exception:
                            pass
                return

        except FileNotFoundError:
            pass
        except Exception:
            pass

        # Fallback: parse WIT files directly
        try:
            wit_dir = self.wasm_file.parent / "wit"
            if wit_dir.exists():
                for wit_file in wit_dir.glob("*.wit"):
                    try:
                        content = wit_file.read_text()
                        lines = content.split("\n")

                        in_world = False
                        for line in lines:
                            stripped = line.strip()

                            if "world" in stripped and "{" in stripped:
                                in_world = True
                                continue

                            if in_world and stripped.startswith("export"):
                                parts = stripped.split(":")
                                if len(parts) >= 2 and "func(" in parts[1]:
                                    func_name = parts[0].replace("export", "").strip()
                                    if "-" in func_name:
                                        parts_name = func_name.split("-")
                                        func_name_camel = parts_name[0] + "".join(
                                            p.capitalize() for p in parts_name[1:]
                                        )
                                        self.exports.append(func_name)
                                        self.exports.append(func_name_camel)
                                    else:
                                        self.exports.append(func_name)

                            if in_world and stripped == "}":
                                in_world = False

                    except Exception as e:
                        console.print(
                            f"[yellow]Warning:[/yellow] Could not parse {wit_file.name}: {e}"
                        )

                self.exports = list(set(self.exports))

                if self.exports:
                    return

        except Exception:
            pass

        # Last resort: check Python source
        try:
            main_py = self.wasm_file.parent / "main.py"
            if main_py.exists():
                content = main_py.read_text()
                import re

                class_methods = re.findall(r"def\s+(\w+)\s*\(self", content)
                if class_methods:
                    self.exports = [m for m in class_methods if not m.startswith("_")]
                    if self.exports:
                        return

        except Exception:
            pass

        self.exports = []

    def call_function(self, function_name: str, args: List[Any]) -> Any:
        wasm_dir = self.wasm_file.parent

        # Python: direct execution
        main_py = wasm_dir / "main.py"
        if main_py.exists():
            try:
                import importlib.util
                import sys

                if str(wasm_dir) not in sys.path:
                    sys.path.insert(0, str(wasm_dir))

                spec = importlib.util.spec_from_file_location("wasm_component", main_py)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Try class methods first (componentize-py pattern)
                    for name in dir(module):
                        obj = getattr(module, name)
                        if isinstance(obj, type) and (
                            hasattr(obj, function_name)
                            or hasattr(obj, function_name.replace("-", "_"))
                        ):
                            instance = obj()
                            method_name = (
                                function_name
                                if hasattr(instance, function_name)
                                else function_name.replace("-", "_")
                            )
                            method = getattr(instance, method_name)
                            result = method(*args)

                            if isinstance(result, str):
                                return result
                            return str(result)

                    # Try module-level function
                    method_name = (
                        function_name
                        if hasattr(module, function_name)
                        else function_name.replace("-", "_")
                    )
                    if hasattr(module, method_name):
                        func = getattr(module, method_name)
                        result = func(*args)
                        return str(result)

            except Exception:
                pass

        # Rust/Go: try wasmtime
        try:
            version_check = subprocess.run(
                ["wasmtime", "--version"],
                capture_output=True,
                timeout=2,
            )

            if version_check.returncode == 0:
                result = subprocess.run(
                    [
                        "wasmtime",
                        "run",
                        str(self.wasm_file),
                        "--invoke",
                        function_name,
                        "--",
                    ]
                    + [str(arg) for arg in args],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    return result.stdout.strip()

        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # JavaScript: try node
        js_files = list(wasm_dir.glob("*.js")) + list(wasm_dir.glob("*.mjs"))
        if js_files:
            try:
                node_check = subprocess.run(
                    ["node", "--version"],
                    capture_output=True,
                    timeout=2,
                )

                if node_check.returncode == 0:
                    runner_script = f"""
const component = require('./{js_files[0].name}');
const args = {json.dumps(args)};
const result = component.{function_name}(...args);
console.log(JSON.stringify(result));
"""
                    runner_path = wasm_dir / "_temp_runner.js"
                    runner_path.write_text(runner_script)

                    try:
                        result = subprocess.run(
                            ["node", str(runner_path)],
                            capture_output=True,
                            text=True,
                            timeout=10,
                            cwd=wasm_dir,
                        )

                        if result.returncode == 0:
                            return json.loads(result.stdout.strip())
                    finally:
                        if runner_path.exists():
                            runner_path.unlink()

            except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
                pass

        # Error message
        component_type = "unknown"
        if main_py.exists():
            component_type = "Python"
        elif (wasm_dir / "Cargo.toml").exists():
            component_type = "Rust"
        elif (wasm_dir / "go.mod").exists():
            component_type = "Go"
        elif js_files:
            component_type = "JavaScript"

        raise Exception(
            f"Unable to invoke function '{function_name}' on {component_type} component.\n\n"
            f"Troubleshooting:\n"
            f"  1. For Python: Ensure main.py exists with the function\n"
            f"  2. For Rust/Go: Install wasmtime: curl https://wasmtime.dev/install.sh -sSf | bash\n"
            f"  3. For JavaScript: Install Node.js and jco: npm install -g @bytecodealliance/jco\n\n"
            f"Manual test:\n"
            f"  wasmtime run {self.wasm_file.name} --invoke {function_name}"
        )

    def reload(self):
        self._discover_exports()


class WasmHttpServerCLI:
    def __init__(self, wasm_file: Path, host: str = "0.0.0.0", port: int = 8080):
        self.wasm_file = wasm_file
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)

        self.component: Optional[WasmComponentCLI] = None
        self.function_signatures: Dict[str, Dict[str, Any]] = {}

        self._setup_routes()
        self._load_component()
        self._parse_function_signatures()

    def _load_component(self):
        try:
            self.component = WasmComponentCLI(self.wasm_file)
        except Exception:
            raise

    def _parse_function_signatures(self):
        try:
            result = subprocess.run(
                ["wasm-tools", "component", "wit", str(self.wasm_file)],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return

            # Parse WIT output
            lines = result.stdout.split("\n")
            in_world = False

            for line in lines:
                stripped = line.strip()

                if "world" in stripped and "{" in stripped:
                    in_world = True
                elif in_world and stripped.startswith("export") and ": func(" in stripped:
                    try:
                        after_export = stripped[6:].strip()
                        func_name = after_export.split(":")[0].strip()

                        # Extract params and return type
                        sig_part = after_export.split(":", 1)[1].strip()
                        if sig_part.startswith("func("):
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
        @self.app.route("/")
        def index():
            return jsonify(
                {
                    "service": "WASM Component API (CLI-based)",
                    "component": self.wasm_file.name,
                    "status": "ready",
                    "docs": "/docs",
                    "api": "/api",
                    "openapi": "/openapi.json",
                    "invocation": "Uses wasmtime CLI for function execution",
                    "functions": len(self.component.exports) if self.component else 0,
                }
            )

        @self.app.route("/api", methods=["GET"])
        def list_functions():
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
                        "note": "Uses wasmtime CLI for execution",
                    }
                )

            return jsonify(
                {
                    "functions": functions,
                    "count": len(functions),
                }
            )

        @self.app.route("/api/<function_name>", methods=["POST"])
        def call_function(function_name: str):
            if not self.component:
                return jsonify({"error": "Component not loaded"}), 500

            # Check if function exists
            if function_name not in self.component.exports:
                return (
                    jsonify(
                        {
                            "error": "Function not found",
                            "function": function_name,
                            "available": self.component.exports,
                        }
                    ),
                    404,
                )

            # Get arguments from request
            try:
                data = request.get_json() or {}
                args = data.get("args", [])

                # Call the function
                result = self.component.call_function(function_name, args)

                return jsonify(
                    {
                        "function": function_name,
                        "args": args,
                        "result": result,
                        "status": "success",
                    }
                )

            except Exception as e:
                return (
                    jsonify(
                        {
                            "error": str(e),
                            "function": function_name,
                            "status": "failed",
                        }
                    ),
                    500,
                )

        @self.app.route("/openapi.json")
        def openapi_spec():
            paths = {}

            for func_name in self.component.exports if self.component else []:
                sig = self.function_signatures.get(func_name, {})

                paths[f"/api/{func_name}"] = {
                    "post": {
                        "summary": f"Call {func_name}",
                        "description": sig.get(
                            "signature", f"Call the {func_name} function using wasmtime CLI"
                        ),
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
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "function": {"type": "string"},
                                                "args": {"type": "array"},
                                                "result": {},
                                                "status": {"type": "string"},
                                            },
                                        }
                                    }
                                },
                            },
                            "404": {"description": "Function not found"},
                            "500": {"description": "Execution error"},
                        },
                    }
                }

            return jsonify(
                {
                    "openapi": "3.0.0",
                    "info": {
                        "title": f"WASM Component API - {self.wasm_file.name}",
                        "version": "1.0.0",
                        "description": "Auto-discovered API for WASM component. "
                        "Functions are invoked using wasmtime CLI for execution.",
                    },
                    "servers": [{"url": f"http://{self.host}:{self.port}"}],
                    "paths": paths,
                }
            )

        @self.app.route("/docs")
        def rapidoc_ui():
            html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation</title>
    <script type="module" src="https://unpkg.com/rapidoc/dist/rapidoc-min.js"></script>
</head>
<body>
    <rapi-doc
        spec-url="/openapi.json"

        theme="light"
        bg-color="#fafafa"
        text-color="#1a1a1a"
        header-color="#1a1a1a"
        primary-color="#1a1a1a"

        font-size="default"

        render-style="focused"
        layout="column"

        show-header="true"
        show-info="true"

        allow-try="true"
        allow-server-selection="false"
        allow-authentication="false"

        schema-style="table"
        schema-expand-level="1"
        schema-description-expanded="false"

        default-schema-tab="example"
        response-area-height="300px"

        nav-bg-color="#ffffff"
        nav-text-color="#1a1a1a"
        nav-hover-bg-color="#f5f5f5"
        nav-hover-text-color="#000000"
        nav-accent-color="#1a1a1a"

        regular-font="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
        mono-font="SF Mono, Monaco, Consolas, Courier New, monospace"

        use-path-in-nav-bar="false"

        style="height: 100vh; width: 100%;"
    >
        <div slot="nav-logo" style="display: flex; align-items: center; padding: 16px 24px; border-bottom: 1px solid #e5e5e5;">
            <div style="font-size: 18px; font-weight: 600; color: #1a1a1a;">API Documentation</div>
        </div>
    </rapi-doc>
</body>
</html>
            """
            return html

        @self.app.route("/reload", methods=["POST"])
        def reload_component():
            try:
                self._load_component()
                self._parse_function_signatures()
                return jsonify({"status": "ok", "message": "Component reloaded"})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def start_with_watch(self, watch: bool = False):
        self._start_server()

    def _start_server(self):
        console.print("\n[bold green]WASM Component Server Running (CLI-based)[/bold green]")
        console.print(f"Component: [cyan]{self.wasm_file.name}[/cyan]")
        console.print(f"URL: [cyan]http://{self.host}:{self.port}[/cyan]")
        console.print(f"API Docs: [cyan]http://{self.host}:{self.port}/docs[/cyan]")
        console.print(f"API Endpoints: [cyan]http://{self.host}:{self.port}/api[/cyan]\\n")

        if self.component:
            console.print("[bold]Discovered functions:[/bold]")
            for func_name in self.component.exports:
                sig = self.function_signatures.get(func_name, {})
                params = sig.get("params", [])
                params_str = ", ".join(f"{p['name']}: {p['type']}" for p in params)
                returns = sig.get("returns", "unknown")
                console.print(f"  • [cyan]{func_name}[/cyan]({params_str}) -> {returns}")

        console.print("\n[yellow]NOTE:[/yellow] Function invocation not yet available.")
        console.print("[dim]Waiting for wasmtime-py Component API support...[/dim]")
        console.print("\nPress Ctrl+C to stop\n")

        # Run Flask app
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
