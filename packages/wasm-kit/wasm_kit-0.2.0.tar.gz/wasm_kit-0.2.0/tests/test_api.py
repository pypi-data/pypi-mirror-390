"""
Tests for wasm-kit Python API.
"""

import pytest
from wasm_kit import (
    LanguageNotDetectedError,
    build,
    check_environment,
    detect_language,
    get_version,
)


def test_detect_language_api():
    """Test language detection API."""
    language, config = detect_language("tests/examples/rust-hello")
    assert language == "rust"


def test_check_environment():
    """Test environment checking API."""
    env = check_environment()
    assert "docker" in env
    assert "rust" in env
    assert "javascript" in env
    assert "python" in env
    assert "wasm_tools" in env


def test_get_version():
    """Test version API."""
    version = get_version()
    assert isinstance(version, str)
    assert len(version) > 0


def test_build_invalid_path():
    """Test build with invalid path."""
    with pytest.raises(LanguageNotDetectedError):
        build("nonexistent/path")


def test_build_api_interface():
    """Test that build API has correct interface."""
    # Just check that build function accepts expected parameters
    # Don't actually build as tools may not be installed
    import inspect

    sig = inspect.signature(build)
    params = list(sig.parameters.keys())

    assert "project_path" in params
    assert "output" in params
    assert "wasm_type" in params
    assert "use_docker" in params
