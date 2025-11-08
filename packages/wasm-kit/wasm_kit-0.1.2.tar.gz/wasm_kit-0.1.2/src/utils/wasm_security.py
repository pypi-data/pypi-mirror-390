# Security utilities for path validation and rate limiting

import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, Optional, Set


class SecurityError(Exception):
    """Raised when a security validation fails."""

    pass


def validate_project_path(path: Path, allow_parent: bool = False) -> Path:
    """
    Validate that a project path is safe to use.

    Args:
        path: The path to validate
        allow_parent: If True, allow paths outside current directory (use with caution)

    Returns:
        The resolved absolute path

    Raises:
        SecurityError: If the path is unsafe (symlink attack, path traversal, etc.)
        FileNotFoundError: If the path doesn't exist
        NotADirectoryError: If the path is not a directory
    """
    try:
        # Resolve to absolute path, following symlinks
        resolved_path = path.resolve(strict=True)
    except (FileNotFoundError, RuntimeError) as e:
        raise FileNotFoundError(f"Path does not exist: {path}") from e

    # Verify it's a directory
    if not resolved_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    # If we don't allow parent directories, ensure the path is within current directory
    if not allow_parent:
        current_dir = Path.cwd().resolve()
        try:
            # This will raise ValueError if resolved_path is not relative to current_dir
            resolved_path.relative_to(current_dir)
        except ValueError:
            raise SecurityError(
                f"Path traversal detected: {path} resolves outside current directory"
            )

    # Additional checks for suspicious patterns
    path_str = str(resolved_path)

    # Check for null bytes (can cause issues in C-level code)
    if "\0" in path_str:
        raise SecurityError("Path contains null bytes")

    return resolved_path


def validate_file_path(path: Path, allowed_extensions: Optional[Set[str]] = None) -> Path:
    """
    Validate that a file path is safe to use.

    Args:
        path: The path to validate
        allowed_extensions: If provided, only allow these extensions (e.g., {'.wasm', '.wat'})

    Returns:
        The resolved absolute path

    Raises:
        SecurityError: If the path is unsafe
        FileNotFoundError: If the file doesn't exist
    """
    try:
        resolved_path = path.resolve(strict=True)
    except (FileNotFoundError, RuntimeError) as e:
        raise FileNotFoundError(f"File does not exist: {path}") from e

    if not resolved_path.is_file():
        raise SecurityError(f"Path is not a file: {path}")

    # Check allowed extensions
    if allowed_extensions and resolved_path.suffix.lower() not in allowed_extensions:
        raise SecurityError(
            f"File extension '{resolved_path.suffix}' not allowed. "
            f"Allowed: {', '.join(allowed_extensions)}"
        )

    # Check for null bytes
    if "\0" in str(resolved_path):
        raise SecurityError("Path contains null bytes")

    return resolved_path


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize a filename to prevent security issues.

    Args:
        filename: The filename to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized filename

    Raises:
        SecurityError: If filename is invalid
    """
    if not filename:
        raise SecurityError("Filename cannot be empty")

    # Check length
    if len(filename) > max_length:
        raise SecurityError(f"Filename too long (max {max_length} chars)")

    # Check for path traversal attempts
    if ".." in filename or "/" in filename or "\\" in filename:
        raise SecurityError("Filename contains path separators")

    # Check for null bytes
    if "\0" in filename:
        raise SecurityError("Filename contains null bytes")

    # Check for control characters
    if any(ord(c) < 32 for c in filename):
        raise SecurityError("Filename contains control characters")

    return filename


def is_safe_symlink(path: Path) -> bool:
    """
    Check if a symlink is safe (doesn't point outside the project).

    Args:
        path: The path to check

    Returns:
        True if safe, False otherwise
    """
    if not path.is_symlink():
        return True

    try:
        target = path.resolve()
        current_dir = Path.cwd().resolve()
        target.relative_to(current_dir)
        return True
    except (ValueError, RuntimeError):
        return False


class RateLimiter:
    """Simple rate limiter for API endpoints."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for this client."""
        now = time.time()
        window_start = now - self.window_seconds

        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] if req_time > window_start
        ]

        # Check if under limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False

        # Record this request
        self.requests[client_id].append(now)
        return True

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for this client."""
        now = time.time()
        window_start = now - self.window_seconds

        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] if req_time > window_start
        ]

        return max(0, self.max_requests - len(self.requests[client_id]))
