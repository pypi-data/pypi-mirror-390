# First-run welcome experience for wasm-kit.

from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()


def get_config_dir() -> Path:
    """Get wasm-kit config directory."""
    config_dir = Path.home() / ".wasm-kit"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def is_first_run() -> bool:
    """Check if this is the first run."""
    config_dir = get_config_dir()
    first_run_file = config_dir / ".first_run"
    return not first_run_file.exists()


def mark_first_run_complete():
    """Mark first run as complete."""
    config_dir = get_config_dir()
    first_run_file = config_dir / ".first_run"
    first_run_file.touch()


def show_welcome():
    """Show welcome message for first-time users."""
    welcome_text = """
# Welcome to wasm-kit!

**The Docker of WebAssembly** — Build any codebase to WASM with zero setup.

## Quick Start

1. **Choose a language** and create a project:
   ```bash
   wasm-kit init python    # or rust, javascript, go, c, cpp
   ```

2. **Build to WASM**:
   ```bash
   wasm-kit build .
   ```

3. **Run it**:
   ```bash
   wasmtime run <project-name>.wasm
   ```

## That's it!

**Need help?**
- `wasm-kit info` - Show system info
- `wasm-kit doctor` - Check your setup
- `wasm-kit build --help` - See build options

**Ready to build?** Just run `wasm-kit build .` in any project directory!
"""

    panel = Panel(
        Markdown(welcome_text),
        title="[bold cyan]wasm-kit[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    )

    console.print("\n")
    console.print(panel)
    console.print("\n")

    mark_first_run_complete()
