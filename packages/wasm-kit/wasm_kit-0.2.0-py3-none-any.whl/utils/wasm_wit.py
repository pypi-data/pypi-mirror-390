# WIT (WebAssembly Interface Types) utilities for parsing and generation.

import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def parse_wit_file(wit_path: Path) -> Dict[str, Any]:
    content = wit_path.read_text()

    package_match = re.search(r"package\s+([^;]+);", content)
    package = package_match.group(1).strip() if package_match else None

    world_match = re.search(r"world\s+([a-zA-Z0-9_-]+)\s*\{", content)
    world_name = world_match.group(1) if world_match else None

    interfaces = []
    interface_pattern = r"interface\s+([a-zA-Z0-9_-]+)\s*\{([^}]+)\}"
    for match in re.finditer(interface_pattern, content, re.DOTALL):
        interface_name = match.group(1)
        interface_body = match.group(2)

        functions = []
        func_pattern = r"(\w+):\s*func\(([^)]*)\)\s*(?:->\s*([^;]+))?;"
        for func_match in re.finditer(func_pattern, interface_body):
            func_name = func_match.group(1)
            params = func_match.group(2).strip()
            returns = func_match.group(3).strip() if func_match.group(3) else None

            functions.append({"name": func_name, "params": params, "returns": returns})

        interfaces.append({"name": interface_name, "functions": functions})

    exports = []
    if world_name:
        world_pattern = rf"world\s+{world_name}\s*\{{([^}}]+)\}}"
        world_match = re.search(world_pattern, content, re.DOTALL)
        if world_match:
            world_body = world_match.group(1)
            export_pattern = r"export\s+([a-zA-Z0-9_-]+)"
            for match in re.finditer(export_pattern, world_body):
                exports.append(match.group(1))

    return {
        "package": package,
        "world": world_name,
        "interfaces": interfaces,
        "exports": exports,
        "content": content,
    }


def generate_wit_file(
    output_path: Path,
    world_name: str = "app",
    package: str = "example:component",
    exports: Optional[List[Dict[str, str]]] = None,
) -> Path:
    if exports is None:
        exports = [{"name": "run", "signature": "func() -> string"}]

    wit_content = f"package {package};\n\n"
    wit_content += f"world {world_name} {{\n"

    for export in exports:
        wit_content += f"  export {export['name']}: {export['signature']};\n"

    wit_content += "}\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(wit_content)

    return output_path


def find_wit_files(project_dir: Path) -> List[Path]:
    wit_files: List[Path] = []

    common_dirs = ["wit", "idl", "interface", "interfaces", "."]
    for dir_name in common_dirs:
        wit_dir = project_dir / dir_name
        if wit_dir.exists():
            wit_files.extend(wit_dir.glob("*.wit"))
            wit_files.extend(wit_dir.glob("**/*.wit"))

    wit_files.extend(project_dir.rglob("*.wit"))
    return sorted(set(wit_files), key=lambda p: (p.parent.name, p.name))
