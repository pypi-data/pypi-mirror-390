import subprocess
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rich import box
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn
from rich.spinner import Spinner
from rich.table import Table


class Logger:

    def __init__(
        self, project_name: str = "project", verbose: bool = True, show_timestamps: bool = False
    ):
        self.console = Console()
        self.project_name = project_name
        self.start_time = time.time()
        self.current_step = 0
        self.total_steps = 0
        self.step_times: Dict[str, float] = {}
        self.verbose = verbose
        self.show_timestamps = show_timestamps
        self._completed_steps: List[str] = []

    def banner(
        self,
        title: str,
        subtitle: Optional[str] = None,
        version: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        lines = [f"[bold white]{title}[/bold white]"]
        if subtitle:
            lines.append(f"[dim]{subtitle}[/dim]")
        if version or url:
            footer_parts = []
            if version:
                footer_parts.append(f"v{version}")
            if url:
                footer_parts.append(url)
            lines.append(f"[dim]{' • '.join(footer_parts)}[/dim]")

        content = "\n".join(lines)
        self.console.print()
        self.console.print(
            Panel(
                content,
                border_style="cyan",
                box=box.ROUNDED,
                padding=(1, 2),
                width=56,
            )
        )
        self.console.print()

    def section(self, title: str) -> None:
        self.console.print()
        self.console.print(f"[bold bright_white]{title}[/bold bright_white]")
        self.console.print("[dim]" + "─" * 60 + "[/dim]")

    @contextmanager
    def step(self, description: str):
        self.current_step += 1
        step_num = (
            f"[dim]({self.current_step}/{self.total_steps})[/dim]" if self.total_steps > 0 else ""
        )

        step_start = time.time()
        spinner = Spinner("dots", text=f"[bold]{description}[/bold] {step_num}", style="cyan")

        try:
            with Live(spinner, console=self.console, refresh_per_second=10):
                yield self

            duration = time.time() - step_start
            self.step_times[description] = duration
            self.console.print(
                f"[green]✓[/green] [bold]{description}[/bold] {step_num} "
                f"[dim]({self._format_duration(duration)})[/dim]"
            )
            self._completed_steps.append(description)

        except Exception:
            duration = time.time() - step_start
            self.console.print(
                f"[red]✗[/red] [bold]{description}[/bold] {step_num} "
                f"[dim red]({self._format_duration(duration)})[/dim]"
            )
            raise

    def substep(self, message: str, status: str = "info") -> None:
        icons = {
            "info": "[cyan]→[/cyan]",
            "success": "[green]✓[/green]",
            "warning": "[yellow]![/yellow]",
            "error": "[red]✗[/red]",
            "working": "[cyan]◆[/cyan]",
        }
        icon = icons.get(status, icons["info"])

        timestamp = (
            f"[dim]{datetime.now().strftime('%H:%M:%S')}[/dim] " if self.show_timestamps else ""
        )
        self.console.print(f"  {timestamp}{icon} [dim]{message}[/dim]")

    def info(self, message: str, indent: int = 0) -> None:
        prefix = "  " * (indent + 1)
        self.console.print(f"{prefix}[cyan]ℹ[/cyan] {message}")

    def success(self, message: str, indent: int = 0) -> None:
        prefix = "  " * (indent + 1)
        self.console.print(f"{prefix}[green]✓[/green] [green]{message}[/green]")

    def warning(self, message: str, indent: int = 0) -> None:
        prefix = "  " * (indent + 1)
        self.console.print(f"{prefix}[yellow]⚠[/yellow] [yellow]{message}[/yellow]")

    def error(self, message: str, hint: Optional[str] = None, indent: int = 0) -> None:
        prefix = "  " * (indent + 1)
        self.console.print(f"{prefix}[red]✗[/red] [red bold]{message}[/red bold]")
        if hint:
            self.console.print(f"{prefix}  [dim]💡 {hint}[/dim]")

    def command(self, cmd: Union[List[str], str], cwd: Optional[Path] = None) -> None:
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
        self.console.print(f"  [dim]$[/dim] [yellow]{cmd_str}[/yellow]")
        if cwd:
            self.console.print(f"  [dim]  in {cwd}[/dim]")

    def run_command(
        self,
        cmd: List[str],
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        show_output: bool = True,
    ) -> subprocess.CompletedProcess:
        if description and self.verbose:
            self.substep(description, "working")

        if self.verbose:
            self.command(cmd, cwd)

        class CommandError(Exception):
            pass

        try:
            if show_output and self.verbose:
                process = subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                )

                stdout_lines = []
                stderr_lines = []

                while True:
                    if process.poll() is not None:
                        break

                    if process.stdout:
                        line = process.stdout.readline()
                        if line:
                            stdout_lines.append(line)
                            self.console.print(f"    [dim]{line.rstrip()}[/dim]")

                remaining_out, remaining_err = process.communicate()
                if remaining_out:
                    for line in remaining_out.splitlines():
                        stdout_lines.append(line + "\n")
                        self.console.print(f"    [dim]{line}[/dim]")
                if remaining_err:
                    for line in remaining_err.splitlines():
                        stderr_lines.append(line + "\n")
                        if line.strip():
                            self.console.print(f"    [yellow dim]{line}[/yellow dim]")

                stdout = "".join(stdout_lines)
                stderr = "".join(stderr_lines)
                returncode = process.returncode

            else:
                result = subprocess.run(
                    cmd,
                    cwd=cwd,
                    env=env,
                    capture_output=True,
                    text=True,
                )
                stdout = result.stdout
                stderr = result.stderr
                returncode = result.returncode

            if returncode != 0:
                self.console.print()
                self.error(f"Command failed with exit code {returncode}")
                if stderr and not show_output:
                    self.console.print(
                        Panel(
                            stderr,
                            title="[red]Error Output[/red]",
                            border_style="red",
                            expand=False,
                        )
                    )
                raise CommandError(f"Command failed: {' '.join(cmd)}")

            class Result:
                def __init__(self, returncode, stdout, stderr):
                    self.returncode = returncode
                    self.stdout = stdout
                    self.stderr = stderr

            return Result(returncode, stdout, stderr)  # type: ignore[return-value]

        except FileNotFoundError:
            self.error(f"Command not found: {cmd[0]}")
            raise CommandError(f"Command not found: {cmd[0]}")

    def table(self, data: Dict[str, Any], title: Optional[str] = None) -> None:
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column(style="cyan bold")
        table.add_column(style="white")

        for key, value in data.items():
            table.add_row(f"{key}:", str(value))

        if title:
            self.console.print()
            self.console.print(
                Panel(
                    table,
                    title=f"[bold]{title}[/bold]",
                    border_style="cyan",
                    box=box.ROUNDED,
                    expand=False,
                )
            )
        else:
            self.console.print(table)

    def list_items(
        self, items: List[str], title: Optional[str] = None, numbered: bool = True
    ) -> None:
        content = []
        for i, item in enumerate(items, 1):
            prefix = f"[cyan]{i}.[/cyan]" if numbered else "[cyan]•[/cyan]"
            content.append(f"{prefix} {item}")

        if title:
            self.console.print()
            self.console.print(
                Panel(
                    "\n".join(content),
                    title=f"[bold]{title}[/bold]",
                    border_style="cyan",
                    box=box.ROUNDED,
                    expand=False,
                    padding=(1, 2),
                )
            )
        else:
            for line in content:
                self.console.print(f"  {line}")

    def file_info(self, file_path: Path, label: str = "File") -> None:
        if not file_path.exists():
            self.warning(f"{label} not found: {file_path}")
            return

        size = file_path.stat().st_size
        modified = datetime.fromtimestamp(file_path.stat().st_mtime)

        data = {
            "File": str(file_path.name),
            "Location": str(file_path.parent),
            "Size": self._format_size(size),
            "Modified": modified.strftime("%Y-%m-%d %H:%M:%S"),
        }

        self.table(data, title=label)

    def show_summary(
        self, title: str = "Summary", details: Optional[Dict[str, Any]] = None, success: bool = True
    ) -> None:
        total_duration = time.time() - self.start_time
        content = []

        if success:
            content.append(f"[green]✓ {title}[/green]")
        else:
            content.append(f"[red]✗ {title}[/red]")

        content.append(f"[dim]Completed in {self._format_duration(total_duration)}[/dim]")

        if details:
            content.append("")
            for key, value in details.items():
                content.append(f"[cyan]{key}:[/cyan] {value}")

        border_style = "green" if success else "red"
        self.console.print()
        self.console.print(
            Panel(
                "\n".join(content),
                border_style=border_style,
                box=box.ROUNDED,
                expand=False,
                padding=(1, 2),
            )
        )
        self.console.print()

    def show_next_steps(self, steps: List[str]) -> None:
        self.list_items(steps, title="Next Steps", numbered=True)

    def progress_table(self, completed: int, total: int, current_task: str = "") -> None:
        pct = (completed / total * 100) if total > 0 else 0
        bar_filled = int(pct / 5)  # 20 chars max
        bar = "█" * bar_filled + "░" * (20 - bar_filled)

        self.console.print()
        self.console.print(f"  [cyan]Progress:[/cyan] {completed}/{total} steps completed")
        self.console.print(f"  [{bar}] {pct:.0f}%")
        if current_task:
            self.console.print(f"  [dim]Current: {current_task}[/dim]")

    def show_progress(self, message: str, progress_pct: float = 0.0) -> None:
        """Display a progress bar with percentage in one line."""
        bar_width = 40
        filled = int(bar_width * progress_pct / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        self.console.print(f"{message} [dim]{progress_pct:.0f}%[/dim] [cyan][{bar}][/cyan]")

    @contextmanager
    def animated_progress(self, message: str = "Building WASM...", build_thread=None):
        """Context manager for animated progress bar during build."""
        progress = Progress(
            TextColumn(f"[bold white][{message}][/bold white]"),
            BarColumn(bar_width=26, style="cyan", complete_style="cyan"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
            transient=False,
        )

        with progress:
            task = progress.add_task("", total=100)

            # Animate progress while build is running
            import time

            current_pct = 0.0
            max_pct = 95.0  # Stop at 95% until build completes

            # Smooth animation while build is running
            if build_thread:
                while build_thread.is_alive():
                    if current_pct < max_pct:
                        current_pct = min(current_pct + 1.5, max_pct)
                        progress.update(task, completed=int(current_pct))
                    time.sleep(0.1)

                # Ensure thread is fully joined
                build_thread.join()

            # Complete to 100% when build finishes
            while current_pct < 100:
                current_pct = min(current_pct + 5, 100)
                progress.update(task, completed=int(current_pct))
                time.sleep(0.02)

            yield progress

    def dashboard(self, title: str, data: Dict[str, Any]) -> None:
        """Display a professional dashboard panel with wide format."""
        content = []
        for key, value in data.items():
            content.append(f"{key}: {value}")

        panel = Panel(
            "\n".join(content),
            title=f"[bold white]{title}[/bold white]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
            width=72,
        )

        self.console.print(panel)
        self.console.print()

    def success_panel(self, title: str, details: Dict[str, Any]) -> None:
        """Display a professional success panel."""
        content = [""]  # Start with empty line
        main_line = details.get("main", "")
        if main_line:
            content.append(f"[bold green]{main_line}[/bold green]")
        content.append("")  # Empty line

        # Add details
        for key, value in details.items():
            if key != "main":
                content.append(f"  {key} [dim]•[/dim] {value}")

        panel = Panel(
            "\n".join(content),
            title=f"[bold green]{title}[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
            width=56,
        )

        self.console.print(panel)
        self.console.print()

    def error_panel(self, title: str, message: str, fix: Optional[str] = None) -> None:
        """Display a professional error panel."""
        content = [""]  # Start with empty line
        content.append(f"[bold red]{message}[/bold red]")
        content.append("")  # Empty line

        if fix:
            content.append(f"  [dim]Run:[/dim] [cyan]{fix}[/cyan]")

        panel = Panel(
            "\n".join(content),
            title=f"[bold red]{title}[/bold red]",
            border_style="red",
            box=box.ROUNDED,
            padding=(1, 2),
            width=56,
        )

        self.console.print(panel)
        self.console.print()

    def live_logs(self, title: str = "Live Logs", logs: Optional[List[str]] = None) -> None:
        """Display live logs panel."""
        if logs is None:
            logs = []

        content = "\n".join(logs) if logs else "[dim]No logs yet...[/dim]"

        panel = Panel(
            content,
            title=f"[bold white]{title}[/bold white]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 1),
            width=56,
        )

        self.console.print(panel)
        self.console.print()

    def footer(self, links: Optional[Dict[str, str]] = None) -> None:
        """Display footer with links."""
        if links is None:
            links = {
                "Star on GitHub": "https://github.com/your-org/wasm-kit",
                "wasmkit.dev": "https://wasmkit.dev",
                "pip install wasm-kit": "pip install wasm-kit",
            }

        footer_text = " • ".join(f"[cyan]{key}[/cyan]" for key in links.keys())

        panel = Panel(
            footer_text,
            border_style="dim",
            box=box.ROUNDED,
            padding=(0, 1),
            width=56,
        )

        self.console.print(panel)
        self.console.print()

    def detect_info(
        self, language: str, config_file: str, details: Optional[Dict[str, str]] = None
    ) -> None:
        data = {"Language": f"[bold green]{language.title()}[/bold green]", "Config": config_file}
        if details:
            data.update(details)

        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column(style="cyan bold", width=12)
        table.add_column(style="white")

        for key, value in data.items():
            table.add_row(f"{key}:", str(value))

        self.console.print(table)

    def show_file_info(self, file_path: Path, label: str = "Output") -> None:
        self.file_info(file_path, label)

    def _format_duration(self, seconds: float) -> str:
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        else:
            mins = int(seconds // 60)
            secs = seconds % 60
            return f"{mins}m {secs:.0f}s"

    def _format_size(self, size_bytes: int) -> str:
        size_float = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB"]:
            if size_float < 1024.0:
                return f"{size_float:.2f} {unit}"
            size_float /= 1024.0
        return f"{size_float:.2f} TB"


# Global logger instance
_global_logger: Optional[Logger] = None


def get_logger(project_name: str = "project") -> Logger:
    """Get or create the global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger(project_name)
    return _global_logger


def set_logger(logger: Logger) -> None:
    """Set the global logger instance."""
    global _global_logger
    _global_logger = logger


# Alias for backward compatibility
BuildLogger = Logger
