"""
Tests for wasm-kit builders.
"""

import pytest
from wasm_kit.builders import JavaScriptBuilder, PythonBuilder, RustBuilder
from wasm_kit.utils import BuildError


def test_rust_builder_init():
    """Test Rust builder initialization."""
    builder = RustBuilder("tests/examples/rust-hello")
    assert builder.project_path.exists()
    assert builder.cargo_toml.exists()


def test_rust_builder_invalid_path():
    """Test Rust builder with invalid path."""
    with pytest.raises(BuildError):
        RustBuilder("nonexistent/path")


def test_javascript_builder_init():
    """Test JavaScript builder initialization."""
    builder = JavaScriptBuilder("tests/examples/js-hello")
    assert builder.project_path.exists()
    assert builder.package_json.exists()


def test_python_builder_init():
    """Test Python builder initialization."""
    builder = PythonBuilder("tests/examples/python-hello")
    assert builder.project_path.exists()


def test_rust_check_dependencies():
    """Test Rust dependency checking."""
    builder = RustBuilder("tests/examples/rust-hello")
    deps = builder.check_dependencies()
    assert "rustc" in deps
    assert "cargo" in deps
    assert "cargo-component" in deps


def test_js_check_dependencies():
    """Test JavaScript dependency checking."""
    builder = JavaScriptBuilder("tests/examples/js-hello")
    deps = builder.check_dependencies()
    assert "node" in deps
    assert "npm" in deps


def test_python_check_dependencies():
    """Test Python dependency checking."""
    builder = PythonBuilder("tests/examples/python-hello")
    deps = builder.check_dependencies()
    assert "python" in deps
    assert "pip" in deps
