# Development server with file watching and auto-build

import os
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

from rich.console import Console
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

console = Console()


class BuildError:
    def __init__(self, file: str = "", line: int = 0, message: str = "", full_error: str = ""):
        self.file = file
        self.line = line
        self.message = message
        self.full_error = full_error

    @staticmethod
    def parse(error_output: str) -> List["BuildError"]:
        import re

        errors = []

        patterns = [
            r'File "([^"]+)", line (\d+).*?(\w+Error: .+)',  # Python
            r"error\[E\d+\]: (.+?) --> ([^:]+):(\d+):\d+",  # Rust
            r"([^:]+):(\d+):\d+ - error .+?: (.+)",  # JS/TS
            r"([^:]+):(\d+):\d+: (.+)",  # Go
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, error_output, re.MULTILINE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 3:
                    if "error[E" in pattern:
                        # Rust format
                        errors.append(
                            BuildError(
                                file=groups[1],
                                line=int(groups[2]),
                                message=groups[0],
                                full_error=match.group(0),
                            )
                        )
                    else:
                        try:
                            errors.append(
                                BuildError(
                                    file=groups[0],
                                    line=int(groups[1]),
                                    message=groups[2] if len(groups) > 2 else "Error",
                                    full_error=match.group(0),
                                )
                            )
                        except (ValueError, IndexError):
                            pass

        if not errors and error_output.strip():
            errors.append(BuildError(message="Build failed", full_error=error_output[:200]))

        return errors


class BuildStats:
    def __init__(self):
        self.files_watched = 0
        self.total_builds = 0
        self.successful_builds = 0
        self.failed_builds = 0

    def record_build(self, success: bool, build_time: float):
        self.total_builds += 1
        if success:
            self.successful_builds += 1
        else:
            self.failed_builds += 1


class WasmFileWatcher(FileSystemEventHandler):
    def __init__(
        self,
        project_path: Path,
        on_change: Callable[[Path], None],
        debounce_seconds: float = 0.5,
    ):
        self.project_path = project_path
        self.on_change = on_change
        self.debounce_seconds = debounce_seconds
        self.last_trigger_time: Dict[str, float] = {}

        # Language-specific file patterns to watch
        self.watch_patterns = {
            "python": ["*.py", "requirements.txt", "pyproject.toml"],
            "javascript": ["*.js", "*.ts", "*.mjs", "*.cjs", "package.json", "tsconfig.json"],
            "rust": ["*.rs", "Cargo.toml", "Cargo.lock"],
            "go": ["*.go", "go.mod", "go.sum"],
            "c": ["*.c", "*.h", "Makefile", "CMakeLists.txt"],
            "cpp": ["*.cpp", "*.hpp", "*.cc", "*.cxx", "Makefile", "CMakeLists.txt"],
            "wit": ["*.wit"],
        }

        # Files/directories to ignore
        self.ignore_patterns = {
            "__pycache__",
            "node_modules",
            ".git",
            ".venv",
            "venv",
            "target",
            "dist",
            "build",
            "*.wasm",
            "*.wcmp",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
        }

    def should_watch_file(self, file_path: Path) -> bool:
        """Determine if a file should trigger a rebuild."""
        # Ignore hidden files
        if any(part.startswith(".") for part in file_path.parts):
            # Except for .wit files in wit directory
            if not (file_path.suffix == ".wit" and "wit" in file_path.parts):
                return False

        # Ignore patterns
        for ignore in self.ignore_patterns:
            if ignore in str(file_path):
                return False

        # Check if matches any watch pattern
        for patterns in self.watch_patterns.values():
            for pattern in patterns:
                if file_path.match(pattern):
                    return True

        return False

    def should_trigger(self, file_path: str) -> bool:
        """Check if enough time has passed since last trigger (debouncing)."""
        now = time.time()
        last_trigger = self.last_trigger_time.get(file_path, 0)

        if now - last_trigger < self.debounce_seconds:
            return False

        self.last_trigger_time[file_path] = now
        return True

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if not self.should_watch_file(file_path):
            return

        if not self.should_trigger(event.src_path):
            return

        # Trigger rebuild
        console.print(f"[dim]📝 Changed:[/dim] {file_path.name}")
        self.on_change(file_path)

    def on_created(self, event: FileSystemEvent):
        """Handle file creation events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if not self.should_watch_file(file_path):
            return

        self.on_change(file_path)


class WasmDevServer:
    """
    Development server with file watching and auto-build.

    Features:
    - Watches source files for changes
    - Automatically rebuilds on changes
    - Serves with hot-reload
    - Beautiful terminal UI
    """

    def __init__(
        self,
        project_path: Path,
        port: int = 8080,
        host: str = "0.0.0.0",
        build_only: bool = False,
        debug: bool = False,
    ):
        self.project_path = project_path
        self.port = port
        self.host = host
        self.build_only = build_only
        self.debug = debug

        self.observer: Optional[Observer] = None
        self.is_running = False
        self.build_count = 0

        # Build statistics
        self.stats = BuildStats()

        # HTTP server for serving component
        self.http_server = None
        self.server_thread: Optional[threading.Thread] = None
        self.wasm_file: Optional[Path] = None

    def get_files_to_watch(self) -> List[Path]:
        """Get list of source files in the project."""
        source_files: Set[Path] = set()

        # Common source file patterns
        patterns = [
            "**/*.py",
            "**/*.js",
            "**/*.ts",
            "**/*.rs",
            "**/*.go",
            "**/*.c",
            "**/*.cpp",
            "**/*.wit",
            "**/Cargo.toml",
            "**/package.json",
            "**/requirements.txt",
            "**/go.mod",
        ]

        for pattern in patterns:
            for file_path in self.project_path.glob(pattern):
                # Skip ignored directories
                if any(
                    ignored in file_path.parts
                    for ignored in ["node_modules", "__pycache__", "target", ".git"]
                ):
                    continue
                source_files.add(file_path)

        return sorted(source_files)

    def _find_wasm_file(self) -> Optional[Path]:
        """Find the built WASM/WCMP file in the project."""
        # Look for .wcmp first, then .wasm
        wasm_files = list(self.project_path.glob("*.wcmp"))
        if not wasm_files:
            wasm_files = list(self.project_path.glob("*.wasm"))

        if wasm_files:
            # Return the most recently modified file
            return max(wasm_files, key=lambda p: p.stat().st_mtime)

        return None

    def _start_http_server(self):
        """Start the HTTP server in a separate thread."""
        if self.build_only:
            if self.debug:
                console.print("  [dim]build-only mode, skipping HTTP server[/dim]")
            return

        # Check if this is a standalone module (can't be served as component API)
        build_type = self._detect_build_type()
        if build_type == "standalone":
            wasm_file = self._find_wasm_file()
            if wasm_file:
                console.print()
                console.print("  [yellow]⚠ Standalone Module (Cannot Serve)[/yellow]")
                console.print()
                console.print("  This is an executable with main(), not a component library.")
                console.print("  Standalone modules cannot be served via HTTP API.")
                console.print()
                console.print("  [bold]To run this module:[/bold]")
                console.print(f"    wasm-kit run {wasm_file.name}")
                console.print()
                console.print("  [bold]To create an HTTP API instead:[/bold]")
                console.print("    wasm-kit init python --template api")
                console.print()
                console.print("  [dim]See STANDALONE_VS_COMPONENT.md for details[/dim]")
                console.print()
            return

        try:
            # Import here to avoid circular dependencies
            # Use CLI-based server since wasmtime-py doesn't have Component API
            from server.wasm_http_server_cli import WasmHttpServerCLI

            # Find WASM file
            self.wasm_file = self._find_wasm_file()
            if not self.wasm_file:
                console.print("[yellow]⚠️  No WASM file found, skipping server start[/yellow]")
                return

            if self.debug:
                console.print(f"  [dim]found wasm file: {self.wasm_file}[/dim]")

            # Create HTTP server
            self.http_server = WasmHttpServerCLI(
                wasm_file=self.wasm_file,
                host=self.host,
                port=self.port,
            )

            if self.debug:
                console.print(
                    f"  [dim]discovered exports: {self.http_server.component.exports}[/dim]"
                )
                console.print(f"  [dim]starting HTTP server on {self.host}:{self.port}[/dim]")

            # Start server in background thread
            def run_server():
                try:
                    import logging
                    import sys
                    from io import StringIO

                    # Configure logging based on debug mode
                    if self.debug:
                        # Debug mode: show request logs but not startup messages
                        logging.getLogger("werkzeug").setLevel(logging.INFO)
                    else:
                        # Normal mode: silence all Flask logs
                        logging.getLogger("werkzeug").setLevel(logging.ERROR)

                    # Always suppress Flask's startup messages (they're confusing)
                    old_stderr = sys.stderr
                    sys.stderr = StringIO()

                    try:
                        self.http_server.app.run(
                            host=self.host,
                            port=self.port,
                            debug=False,
                            use_reloader=False,
                            threaded=True,
                        )
                    finally:
                        sys.stderr = old_stderr

                except Exception as e:
                    if self.debug:
                        console.print(f"  [red]server error:[/red] {e}")

            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()

        except ImportError:
            pass  # Silent - server won't start but build will work
        except Exception:
            pass  # Silent fail

    def _reload_http_server(self):
        """Reload the HTTP server with the new component."""
        if self.build_only or not self.http_server:
            return

        try:
            # Find the updated WASM file
            new_wasm_file = self._find_wasm_file()
            if not new_wasm_file:
                if self.debug:
                    console.print("  [dim]no wasm file found for reload[/dim]")
                return

            self.wasm_file = new_wasm_file

            if self.debug:
                console.print(f"  [dim]reloading component from: {new_wasm_file.name}[/dim]")

            # Reload the component
            self.http_server._load_component()
            self.http_server._parse_function_signatures()

            if self.debug:
                console.print(
                    f"  [dim]reloaded exports: {self.http_server.component.exports}[/dim]"
                )

        except Exception as e:
            # Silent fail on reload unless debug
            if self.debug:
                console.print(f"  [yellow]reload error:[/yellow] {e}")

    def on_file_change(self, changed_file: Path):
        """Handle file change event."""
        try:
            # Show rebuild message
            timestamp = datetime.now().strftime("%H:%M:%S")
            if self.debug:
                console.print(f"  [{timestamp}] [dim]file changed: {changed_file}[/dim]")
            console.print(f"  [{timestamp}] [dim]{changed_file.name} changed, rebuilding...[/dim]")

            start_time = time.time()
            self.build_count += 1

            # Call the actual build system
            success, build_output = self._build_project()

            build_time = time.time() - start_time

            # Record build statistics
            self.stats.record_build(success, build_time)

            if success:
                # If build succeeded and not build-only mode, reload server
                if not self.build_only:
                    if self.debug:
                        console.print(f"  [{timestamp}] [dim]reloading HTTP server...[/dim]")
                    self._reload_http_server()

                # Simple success message
                console.print(
                    f"  [{timestamp}] [green]ready[/green] in [cyan]{build_time*1000:.0f}ms[/cyan]"
                )
            else:
                # Show errors cleanly
                console.print(f"  [{timestamp}] [red]build failed[/red] in {build_time*1000:.0f}ms")
                if build_output:
                    self._display_build_errors(build_output)

            console.print()

        except Exception as e:
            console.print(f"  [red]error:[/red] {e}")
            if self.debug:
                import traceback

                console.print(f"  [dim]{traceback.format_exc()}[/dim]")

    def _display_build_errors(self, error_output: str):
        """Display build errors cleanly."""
        errors = BuildError.parse(error_output)

        if not errors:
            console.print(f"  {error_output[:300]}")
            return

        # Show errors simply
        for error in errors[:3]:  # First 3 errors
            if error.file:
                console.print(f"  [red]✗[/red] {error.file}:{error.line}")
                console.print(f"    {error.message}")
            else:
                console.print(f"  [red]✗[/red] {error.message}")

        if len(errors) > 3:
            console.print(f"  [dim]and {len(errors) - 3} more errors[/dim]")

    def _detect_build_type(self) -> str:
        """
        Detect whether to build as 'component' or 'standalone'.

        Go and some Rust projects need standalone, others use component.
        """
        # Check for Go files - Go only supports standalone
        if list(self.project_path.glob("*.go")) or list(self.project_path.glob("go.mod")):
            return "standalone"

        # Check for Rust main.rs (indicates standalone binary)
        src_dir = self.project_path / "src"
        if src_dir.exists():
            main_rs = src_dir / "main.rs"
            if main_rs.exists():
                # Check if it has fn main() - indicates standalone
                try:
                    content = main_rs.read_text()
                    if "fn main()" in content:
                        return "standalone"
                except Exception:
                    pass

        # Check for explicit standalone indicator in README or docs
        readme = self.project_path / "README.md"
        if readme.exists():
            try:
                content = readme.read_text().lower()
                if "standalone" in content and "wasm" in content:
                    return "standalone"
            except Exception:
                pass

        # Default to component (Python, JS, Rust component model)
        return "component"

    def _build_project(self) -> tuple[bool, Optional[str]]:
        try:
            # Detect build type
            build_type = self._detect_build_type()

            if self.debug:
                console.print(f"  [dim]detected build type: {build_type}[/dim]")

            # Build command
            cmd = ["python", "-m", "cli.main", "build", str(self.project_path)]

            # Add --type flag if standalone
            if build_type == "standalone":
                cmd.extend(["--type", "standalone"])

            if self.debug:
                console.print(f"  [dim]build command: {' '.join(cmd)}[/dim]")

            # Use the existing wasm-kit build command
            result = subprocess.run(
                cmd,
                cwd=self.project_path.parent,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                env={
                    **dict(os.environ),
                    "PYTHONPATH": str(Path(__file__).parent.parent),
                },
            )

            if result.returncode == 0:
                if self.debug and result.stdout:
                    console.print("  [dim]build output:[/dim]")
                    # Filter out spinner animation lines
                    for line in result.stdout.strip().split("\n"):
                        # Skip spinner lines and empty lines
                        if any(
                            x in line
                            for x in [
                                "Building... |",
                                "Building... /",
                                "Building... -",
                                "Building... \\",
                            ]
                        ):
                            continue
                        if line.strip() in ["[/dim]", ""]:
                            continue
                        console.print(f"    [dim]{line}[/dim]")
                return True, None
            else:
                # Extract relevant error info
                error_output = result.stderr or result.stdout
                return False, error_output

        except subprocess.TimeoutExpired:
            return False, "Build timed out after 2 minutes"
        except Exception as e:
            return False, str(e)

    def start(self):
        """Start the development server."""
        self.is_running = True

        try:
            # Get source files
            source_files = self.get_files_to_watch()
            self.stats.files_watched = len(source_files)

            # Show initial message - clean and minimal
            console.print()
            if self.debug:
                # Debug mode: show compact info
                mode = "build-only" if self.build_only else "dev"
                console.print(
                    f"  [bold]wasm-kit[/bold] {mode} [dim]• {self.project_path.name} • :{self.port} • debug[/dim]"
                )
            else:
                console.print("  [bold]wasm-kit[/bold] dev server")
            console.print()

            # Initial build
            start_time = time.time()
            success, error_output = self._build_project()
            build_time = time.time() - start_time

            # Record initial build statistics
            self.stats.record_build(success, build_time)

            if success:
                console.print(f"  [green]ready[/green] in [cyan]{build_time*1000:.0f}ms[/cyan]")
                console.print()

                # Start HTTP server if not in build-only mode
                if not self.build_only:
                    self._start_http_server()
                    if self.http_server:
                        console.print(f"  [dim]Local:[/dim]   http://{self.host}:{self.port}")
                        console.print(f"  [dim]API:[/dim]     http://{self.host}:{self.port}/api")
                        console.print(f"  [dim]Docs:[/dim]    http://{self.host}:{self.port}/docs")
                        console.print()
                        console.print(f"  [dim]watching {len(source_files)} files[/dim]")
                    else:
                        console.print(
                            f"  [dim]watching {len(source_files)} files for changes[/dim]"
                        )
            else:
                console.print(f"  [red]build failed[/red] in {build_time*1000:.0f}ms")
                if error_output:
                    console.print()
                    # Show clean error
                    errors = BuildError.parse(error_output)
                    if errors:
                        for err in errors[:3]:
                            if err.file:
                                console.print(f"  [red]error[/red] {err.file}:{err.line}")
                                console.print(f"  {err.message}")
                    else:
                        console.print(f"  {error_output[:200]}")

            console.print()

            # Setup file watcher
            event_handler = WasmFileWatcher(
                project_path=self.project_path,
                on_change=self.on_file_change,
            )

            self.observer = Observer()
            self.observer.schedule(event_handler, str(self.project_path), recursive=True)
            self.observer.start()

            # Simple message
            console.print("  [dim]press ctrl+c to stop[/dim]")
            console.print()

            # Keep running - no fancy UI, just wait
            try:
                while self.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()

        except Exception as e:
            console.print(f"\n  [red]error:[/red] {e}")
            raise

    def stop(self):
        """Stop the development server."""
        self.is_running = False

        if self.observer:
            self.observer.stop()
            self.observer.join()

        console.print()
        console.print(f"  [green]✓[/green] built {self.build_count} times")
        console.print()
