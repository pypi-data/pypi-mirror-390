# wasm-kit detect command - Detect project configuration.

import sys
from pathlib import Path

import click
from rich.console import Console

from utils import LanguageNotDetectedError
from utils.wasm_detect import detect_entry, detect_language, detect_wit

console = Console()


@click.command(name="detect")
@click.argument("project_path", type=click.Path(exists=True), default=".")
def detect(project_path: str):
    """Detect the language and configuration of a project."""
    try:
        lang = detect_language(Path(project_path))
        entry = detect_entry(Path(project_path))
        wit_dir, world = detect_wit(Path(project_path))

        console.print(f"Language: {lang.title()}")
        console.print(f"Entry Point: {entry}")
        console.print(f"WIT Directory: {wit_dir}")
        console.print(f"World: {world}")
    except (ValueError, LanguageNotDetectedError) as e:
        console.print(f"Error: {str(e)}")
        sys.exit(1)
