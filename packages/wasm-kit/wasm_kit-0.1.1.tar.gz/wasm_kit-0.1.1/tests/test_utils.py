"""
Tests for wasm-kit utilities.
"""

import pytest
from wasm_kit.utils import (
    LanguageNotDetectedError,
    check_command_available,
    detect_language,
    format_size,
)


def test_detect_rust():
    """Test Rust project detection."""
    language, config = detect_language("tests/examples/rust-hello")
    assert language == "rust"
    assert config.name == "Cargo.toml"


def test_detect_javascript():
    """Test JavaScript project detection."""
    language, config = detect_language("tests/examples/js-hello")
    assert language == "javascript"
    assert config.name == "package.json"


def test_detect_python():
    """Test Python project detection."""
    language, config = detect_language("tests/examples/python-hello")
    assert language == "python"


def test_detect_invalid_path():
    """Test detection with invalid path."""
    with pytest.raises(LanguageNotDetectedError):
        detect_language("nonexistent/path")


def test_check_command_available():
    """Test command availability checking."""
    # Python should be available in test environment
    assert check_command_available("python") or check_command_available("python3")

    # This command should not exist
    assert not check_command_available("this-command-definitely-does-not-exist")


def test_format_size():
    """Test size formatting."""
    assert format_size(100) == "100.00 B"
    assert format_size(1024) == "1.00 KB"
    assert format_size(1024 * 1024) == "1.00 MB"
    assert format_size(1024 * 1024 * 1024) == "1.00 GB"
