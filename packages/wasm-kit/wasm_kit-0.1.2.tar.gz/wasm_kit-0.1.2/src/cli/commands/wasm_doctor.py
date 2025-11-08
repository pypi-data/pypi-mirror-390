# wasm-kit doctor command - Check environment and diagnose issues.

import subprocess
from pathlib import Path

import click
from rich.console import Console

from system.wasm_health import check_environment

console = Console()


@click.command(name="doctor")
def doctor():
    # Check environment and diagnose potential issues.
    console.print("Checking environment...\n")

    env = check_environment()

    # Check Docker
    docker_ok = env.get("docker", False)
    docker_status = "OK" if docker_ok else "Missing"
    docker_fix = "" if docker_ok else "Install Docker"
    console.print(f"Docker: {docker_status}")
    if docker_fix:
        console.print(f"  Fix: {docker_fix}")

    # Check wasmtime
    wasmtime_ok = False
    try:
        subprocess.run(["wasmtime", "--version"], capture_output=True, check=True)
        wasmtime_ok = True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    wasmtime_status = "OK" if wasmtime_ok else "Missing"
    wasmtime_fix = "" if wasmtime_ok else "curl https://wasmtime.dev/install.sh | bash"
    console.print(f"\nwasmtime: {wasmtime_status}")
    if wasmtime_fix:
        console.print(f"  Fix: {wasmtime_fix}")

    # Check WIT files (if in a project)
    project_path = Path.cwd()
    wit_files = list(project_path.rglob("*.wit"))
    wit_status = "Found" if wit_files else "Missing"
    wit_fix = "" if wit_files else "wasm-kit init wit"
    console.print(f"\nWIT files: {wit_status}")
    if wit_fix:
        console.print(f"  Fix: {wit_fix}")

    console.print()
