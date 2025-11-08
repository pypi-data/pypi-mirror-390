# wasm-kit build command for building projects to WASM

import sys
import threading
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from engine.wasm_builder import build_project
from utils import BuildError, format_size
from utils.build_cache import BuildCache
from utils.structured_logger import metrics
from utils.wasm_detect import detect_language
from utils.wasm_logger import Logger, set_logger
from utils.wasm_security import SecurityError, validate_project_path


def _get_version():
    try:
        from importlib.metadata import version

        return version("wasm-kit")
    except (ImportError, Exception):
        try:
            import importlib_metadata

            return importlib_metadata.version("wasm-kit")
        except Exception:
            # Fallback: read from pyproject.toml
            try:
                pyproject_path = Path(__file__).parent.parent.parent.parent / "pyproject.toml"
                if pyproject_path.exists():
                    with open(pyproject_path, "rb") as f:
                        # Try tomllib (Python 3.11+)
                        try:
                            import tomllib

                            data = tomllib.load(f)
                        except ImportError:
                            # Fallback to tomli for older Python
                            import tomli

                            data = tomli.load(f)
                        return data.get("project", {}).get("version", "0.1.0")
            except Exception:
                pass
            return "0.1.0"


__version__ = _get_version()

console = Console()


@click.command(name="build")
@click.argument("project_path", type=click.Path(exists=True), default=".")
@click.option(
    "-t",
    "--type",
    "wasm_type",
    type=click.Choice(["component", "standalone"], case_sensitive=False),
    default="component",
    help="WASM type: component (WASI component model) or standalone (entrypoint binary)",
)
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(),
    default=None,
    help="Output file path for the WASM file",
)
@click.option("-v", "--verbose", is_flag=True, help="Show detailed build output")
@click.option("--no-cache", is_flag=True, help="Disable build cache")
def build(
    project_path: str, wasm_type: str, output_path: Optional[str], verbose: bool, no_cache: bool
):
    logger_instance = Logger(project_name=Path(project_path).name)
    set_logger(logger_instance)

    build_start_time = time.time()
    build_cache = BuildCache() if not no_cache else None

    try:
        # Validate project path for security
        project_directory = validate_project_path(Path(project_path), allow_parent=True)

        # Check cache first
        if build_cache and not output_path:
            cache_key = build_cache.get_cache_key(project_directory)
            cached_artifact = build_cache.get(cache_key)
            if cached_artifact:
                if verbose:
                    console.print(f"Using cached build: {cached_artifact}")
                console.print(f"Build complete: {cached_artifact.name} (cached)")
                file_size = cached_artifact.stat().st_size
                console.print(f"Size: {format_size(file_size)}, Time: 0.0s")
                metrics.record_cache_hit()
                metrics.record_build(success=True, duration=0.0)
                return

        if build_cache:
            metrics.record_cache_miss()

        # Detect language silently (only show errors)
        try:
            detected_language = detect_language(project_directory)
            if verbose:
                console.print(f"Detected language: {detected_language}")
                from utils.wasm_deps import get_dependencies

                project_dependencies = get_dependencies(project_directory, detected_language)
                if project_dependencies:
                    dependencies_string = ", ".join(
                        f"{key}={value}" for key, value in project_dependencies.items()
                    )
                    console.print(f"Dependencies: {dependencies_string}")
        except ValueError:
            console.print("Error: Language not detected. Run: wasm-kit init <language>")
            sys.exit(1)

        # Build with simple spinner
        spinner_chars = ["|", "/", "-", "\\"]
        spinner_running = True
        spinner_index = 0

        def show_spinner():
            nonlocal spinner_index
            while spinner_running:
                sys.stdout.write(
                    f"\rBuilding... {spinner_chars[spinner_index % len(spinner_chars)]}"
                )
                sys.stdout.flush()
                time.sleep(0.1)
                spinner_index += 1

        spinner_thread = threading.Thread(target=show_spinner, daemon=True)
        spinner_thread.start()

        try:
            # Build the project
            build_result = build_project(
                project_directory, wasm_type=wasm_type, output_path=output_path
            )
        finally:
            spinner_running = False
            spinner_thread.join()
            sys.stdout.write("\r" + " " * 20 + "\r")  # Clear spinner line

        built_wasm_file = build_result["wasm_file"]
        build_duration = build_result["time"]
        file_size_bytes = built_wasm_file.stat().st_size
        formatted_size = format_size(file_size_bytes)

        # Store in cache
        if build_cache and not output_path:
            cache_key = build_cache.get_cache_key(project_directory)
            build_cache.put(cache_key, built_wasm_file)

        # Record metrics
        total_duration = time.time() - build_start_time
        metrics.record_build(success=True, duration=total_duration)

        # Simple output
        console.print(f"Build complete: {built_wasm_file.name}")
        console.print(f"Size: {formatted_size}, Time: {build_duration:.1f}s")

    except BuildError as build_error:
        metrics.record_build(success=False, duration=time.time() - build_start_time)
        error_msg = str(build_error)
        error_lower = error_msg.lower()

        # Determine fix command
        fix_command: Optional[str] = None
        if "docker" in error_lower and ("not found" in error_lower or "not running" in error_lower):
            try:
                import docker

                docker_client = docker.from_env()  # type: ignore[attr-defined]
                docker_client.ping()
                fix_command = "sudo systemctl start docker"
            except Exception:
                fix_command = "Install Docker"
        elif "permission" in error_lower or "denied" in error_lower:
            fix_command = "sudo chown -R $USER:$USER ."
        elif "not found" in error_lower and "wit" in error_lower:
            fix_command = "wasm-kit init wit"
        elif "not found" in error_lower and ("entry" in error_lower or "file" in error_lower):
            fix_command = "wasm-kit init <language>"
        elif "only supports" in error_lower or "does not support" in error_lower:
            fix_command = (
                "wasm-kit build . --type standalone"
                if "standalone" not in error_msg.lower()
                else None
            )
        else:
            fix_command = "wasm-kit build . --verbose"

        # Simple error output
        console.print(f"Error: {error_msg}")
        if fix_command:
            console.print(f"Run: {fix_command}")
        sys.exit(1)
    except SecurityError as security_error:
        console.print(f"Security error: {str(security_error)}")
        sys.exit(1)
    except ValueError as value_error:
        console.print(f"Configuration error: {str(value_error)}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\nBuild cancelled by user")
        sys.exit(130)
    except Exception as unexpected_error:
        console.print(f"Unexpected error: {unexpected_error}")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            import traceback

            console.print("\n" + traceback.format_exc())
        sys.exit(1)
