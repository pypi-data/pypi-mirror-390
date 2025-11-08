# Build cache for faster incremental builds

import hashlib
import json
import shutil
from pathlib import Path
from typing import Optional


class BuildCache:
    """SHA-based build cache to skip unchanged builds."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".cache" / "wasm-kit" / "builds"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "index.json"
        self.index = self._load_index()

    def _load_index(self) -> dict:
        if self.index_file.exists():
            return json.loads(self.index_file.read_text())
        return {}

    def _save_index(self):
        self.index_file.write_text(json.dumps(self.index, indent=2))

    def _hash_file(self, file_path: Path) -> str:
        hasher = hashlib.sha256()
        hasher.update(file_path.read_bytes())
        return hasher.hexdigest()

    def _hash_project_files(self, project_path: Path) -> str:
        """Hash all relevant source files."""
        hasher = hashlib.sha256()

        patterns = ["*.py", "*.js", "*.ts", "*.rs", "*.go", "*.c", "*.cpp", "*.wit"]
        files = []
        for pattern in patterns:
            files.extend(sorted(project_path.rglob(pattern)))

        for file in files:
            if ".git" in file.parts or "node_modules" in file.parts:
                continue
            hasher.update(file.read_bytes())

        return hasher.hexdigest()

    def _hash_config(self, project_path: Path) -> str:
        """Hash configuration files."""
        hasher = hashlib.sha256()

        config_files = [
            "Cargo.toml",
            "package.json",
            "requirements.txt",
            "go.mod",
            "wit/world.wit",
        ]

        for config_file in config_files:
            config_path = project_path / config_file
            if config_path.exists():
                hasher.update(config_path.read_bytes())

        return hasher.hexdigest()

    def get_cache_key(self, project_path: Path) -> str:
        """Generate cache key from project state."""
        files_hash = self._hash_project_files(project_path)
        config_hash = self._hash_config(project_path)
        combined = f"{files_hash}{config_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def get(self, cache_key: str) -> Optional[Path]:
        """Get cached build artifact if it exists."""
        if cache_key not in self.index:
            return None

        cached_file = self.cache_dir / f"{cache_key}.wasm"
        if cached_file.exists():
            return cached_file

        del self.index[cache_key]
        self._save_index()
        return None

    def put(self, cache_key: str, build_artifact: Path):
        """Store build artifact in cache."""
        if not build_artifact.exists():
            return

        cached_file = self.cache_dir / f"{cache_key}.wasm"
        shutil.copy2(build_artifact, cached_file)

        self.index[cache_key] = {
            "timestamp": build_artifact.stat().st_mtime,
            "size": build_artifact.stat().st_size,
        }
        self._save_index()

    def clear(self):
        """Clear all cached builds."""
        for file in self.cache_dir.glob("*.wasm"):
            file.unlink()
        self.index = {}
        self._save_index()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.wasm"))
        return {
            "cached_builds": len(self.index),
            "total_size_mb": total_size / (1024 * 1024),
            "cache_dir": str(self.cache_dir),
        }
