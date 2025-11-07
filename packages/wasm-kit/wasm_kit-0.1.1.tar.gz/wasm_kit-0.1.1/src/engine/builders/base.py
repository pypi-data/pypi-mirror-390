from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class WasmBuilder(ABC):
    _IMAGE_MAP = {
        "wasm_js.Dockerfile": "wasm-js-builder",
        "wasm_rust.Dockerfile": "wasm-rust-builder",
        "wasm_python.Dockerfile": "wasm-python-builder",
        "wasm_go.Dockerfile": "wasm-go-builder",
        "wasm_cpp.Dockerfile": "wasm-cpp-builder",
    }

    def __init__(self) -> None:
        self._custom_image_name: Optional[str] = None

    def set_image_name(self, image_name: str) -> None:
        self._custom_image_name = image_name

    def get_image_name(self) -> str:
        if self._custom_image_name:
            return self._custom_image_name

        dockerfile_name = self.get_dockerfile()
        return self._IMAGE_MAP.get(dockerfile_name, "wasm-builder")

    @abstractmethod
    def build(
        self,
        project_dir: Path,
        wit_dir: Path,
        world: str,
        entry: Path,
        wasm_type: str = "component",
    ) -> Path:
        pass

    @abstractmethod
    def get_dockerfile(self) -> str:
        pass
