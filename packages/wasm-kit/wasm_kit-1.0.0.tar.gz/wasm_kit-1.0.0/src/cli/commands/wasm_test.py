# wasm-kit test - Run automated tests for WASM components

import json
import sys
import time
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from utils.wasm_security import SecurityError, validate_project_path

console = Console()


@click.command(name="test")
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option("--function", "-f", help="Test specific function only")
@click.option("--load", is_flag=True, help="Run load testing (100 requests)")
@click.option("--watch", "-w", is_flag=True, help="Watch mode - rerun on changes")
@click.option("--port", "-p", default=8081, help="Port for test server")
def test(path: str, function: str, load: bool, watch: bool, port: int):
    """Test WASM component functions."""
    try:
        project_path = validate_project_path(Path(path), allow_parent=True)
    except SecurityError as e:
        console.print(f"  [red]error:[/red] {e}")
        sys.exit(1)

    console.print()
    console.print("  [bold]wasm-kit[/bold] test")
    console.print()

    test_file = project_path / "tests.json"
    if test_file.exists():
        run_tests_from_file(project_path, test_file, function, load, port)
    else:
        run_discovery_tests(project_path, function, load, port)


def run_tests_from_file(
    project_path: Path, test_file: Path, target_function: str, load: bool, port: int
):
    try:
        tests = json.loads(test_file.read_text())
    except json.JSONDecodeError as e:
        console.print(f"  [red]error:[/red] Invalid tests.json: {e}")
        sys.exit(1)

    import subprocess
    import threading

    server_process = None

    def start_server():
        nonlocal server_process
        server_process = subprocess.Popen(
            ["wasm-kit", "dev", str(project_path), "--port", str(port), "--no-open"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # wait for server startup

    results = []
    for test in tests.get("tests", []):
        func_name = test.get("function")

        if target_function and func_name != target_function:
            continue

        args = test.get("args", [])
        expected = test.get("expected")

        try:
            import requests

            response = requests.post(
                f"http://localhost:{port}/api/{func_name}",
                json={"args": args},
                timeout=5,
            )

            if response.status_code == 200:
                result = response.json().get("result")
                passed = str(result) == str(expected)
                results.append(
                    {
                        "function": func_name,
                        "args": args,
                        "expected": expected,
                        "actual": result,
                        "passed": passed,
                    }
                )
            else:
                results.append(
                    {
                        "function": func_name,
                        "args": args,
                        "expected": expected,
                        "actual": f"Error: {response.status_code}",
                        "passed": False,
                    }
                )

        except Exception as e:
            results.append(
                {
                    "function": func_name,
                    "args": args,
                    "expected": expected,
                    "actual": f"Error: {e}",
                    "passed": False,
                }
            )

    if server_process:
        server_process.terminate()

    display_test_results(results)

    failed = sum(1 for r in results if not r["passed"])
    if failed > 0:
        sys.exit(1)


def run_discovery_tests(project_path: Path, target_function: str, load: bool, port: int):
    console.print("  [yellow]no tests.json found[/yellow]")
    console.print()
    console.print("  [bold]Create tests.json:[/bold]")
    console.print(
        """  {
    "tests": [
      {
        "function": "greet",
        "args": ["World"],
        "expected": "Hello, World!"
      },
      {
        "function": "add",
        "args": [5, 3],
        "expected": "8"
      }
    ]
  }"""
    )
    console.print()
    console.print("  [dim]Then run: wasm-kit test[/dim]")
    console.print()


def display_test_results(results: list):
    console.print()

    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed

    if failed == 0:
        console.print(f"  [green]✓ All {passed} tests passed[/green]")
    else:
        console.print(f"  [red]✗ {failed} of {len(results)} tests failed[/red]")

    console.print()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Status", style="dim", width=8)
    table.add_column("Function")
    table.add_column("Args")
    table.add_column("Expected")
    table.add_column("Actual")

    for result in results:
        status = "[green]✓ PASS[/green]" if result["passed"] else "[red]✗ FAIL[/red]"
        table.add_row(
            status,
            result["function"],
            json.dumps(result["args"]),
            str(result["expected"]),
            str(result["actual"]),
        )

    console.print(table)
    console.print()
