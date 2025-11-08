"""
CLI package for wasm-kit.
"""


# Avoid importing cli.main when it's being run as __main__ to prevent RuntimeWarning
# The warning occurs when: python -m cli.main imports cli package, which imports cli.main,
# then Python tries to execute cli.main as __main__, but it's already in sys.modules.
#
# Solution: Use lazy imports - only import when actually accessed, not at module level.
# This prevents cli.main from being added to sys.modules during package import.
def _get_cli():
    """Lazy import of cli function."""
    from .main import cli

    return cli


def _get_main():
    """Lazy import of main function."""
    from .main import main

    return main


# Use __getattr__ for lazy imports (Python 3.7+)
def __getattr__(name):
    if name == "cli":
        return _get_cli()
    elif name == "main":
        return _get_main()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["cli", "main"]
