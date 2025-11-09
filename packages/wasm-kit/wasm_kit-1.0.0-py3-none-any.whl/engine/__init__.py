"""
WASM build engine - unified interface for building any language to WASM.
"""

from .wasm_builder import build_project

__all__ = ["build_project"]
