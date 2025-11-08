# WASM optimization utilities

import subprocess
from pathlib import Path

from utils import check_command_available


def optimize(wasm_file: Path) -> Path:
    if not check_command_available("wasm-opt"):
        return wasm_file

    try:
        subprocess.run(
            ["wasm-opt", "-O4", "-o", str(wasm_file), str(wasm_file)],
            check=False,
            capture_output=True,
        )
    except Exception:
        pass

    return wasm_file
