from pathlib import Path

from utils.wasm_detect import detect_language

from .wasm_cpp_builder import CppWasmBuilder
from .wasm_go_builder import GoWasmBuilder
from .wasm_js_builder import JavaScriptWasmBuilder
from .wasm_python_builder import PythonWasmBuilder
from .wasm_rust_builder import RustWasmBuilder


def get_builder(project_dir: Path):
    language = detect_language(project_dir)

    if language == "python":
        return PythonWasmBuilder()
    elif language in ("javascript", "typescript"):
        return JavaScriptWasmBuilder()
    elif language == "rust":
        return RustWasmBuilder()
    elif language == "go":
        return GoWasmBuilder()
    elif language in ("c", "cpp"):
        return CppWasmBuilder()
    else:
        raise ValueError(f"Unsupported language: {language}")
