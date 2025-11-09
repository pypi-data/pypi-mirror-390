# Main CLI entry point for wasm-kit.

import sys

import click

from utils.wasm_welcome import is_first_run, show_welcome

from .commands.wasm_build import build
from .commands.wasm_detect import detect
from .commands.wasm_dev import dev
from .commands.wasm_doctor import doctor
from .commands.wasm_info import info
from .commands.wasm_init import init
from .commands.wasm_run import run
from .commands.wasm_test import test

__version__ = "0.1.0"


@click.group()
@click.version_option(__version__, prog_name="wasm-kit")
@click.pass_context
def cli(ctx):
    """wasm-kit - Build any codebase to WebAssembly with zero setup."""
    # Show welcome message on first run
    if is_first_run() and ctx.invoked_subcommand not in (None, "--help", "help"):
        if "--help" not in sys.argv and "help" not in sys.argv:
            show_welcome()


# Register CLI commands
cli.add_command(build)
cli.add_command(run)
cli.add_command(dev)
cli.add_command(test)
cli.add_command(detect)
cli.add_command(init)
cli.add_command(info)
cli.add_command(doctor)


def main() -> None:
    cli.main(prog_name="wasm-kit", standalone_mode=True)


if __name__ == "__main__":
    main()
