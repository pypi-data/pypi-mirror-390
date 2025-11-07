# wasm-kit init command - Initialize a new WASM project.

from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.command(name="init")
@click.argument(
    "language",
    type=click.Choice(["rust", "javascript", "typescript", "python", "go", "c", "cpp", "wit"]),
)
def init(language: str):
    """
    Initialize a new WASM project.

    Example:
      wasm-kit init rust
    """
    console.print(f"Creating a new {language.title()} WASM project...")

    # Create basic project structure
    templates = {
        "rust": {
            "Cargo.toml": """[package]
name = "my-wasm-component"
version = "0.1.0"
edition = "2021"

[dependencies]

[lib]
crate-type = ["cdylib"]

[package.metadata.component]
package = "component:my-component"
""",
            "src/lib.rs": """#[no_mangle]
pub extern "C" fn run() -> i32 {
    println!("Hello from Rust WASM!");
    42
}
""",
        },
        "javascript": {
            "package.json": """{
  "name": "my-wasm-component",
  "version": "0.1.0",
  "main": "index.js",
  "type": "module"
}
""",
            "index.js": """export function run() {
  console.log("Hello from JavaScript WASM!");
  return "Success";
}
""",
            "wit/world.wit": """package example:component;

world example {
  export run: func() -> string;
}
""",
        },
        "python": {
            "main.py": """def run():
    print("Hello from Python WASM!")
    return "Success"

if __name__ == "__main__":
    print(run())
""",
            "requirements.txt": "# Add your dependencies here\n",
            "wit/world.wit": """package example:component;

world example {
  export run: func() -> string;
}
""",
        },
        "go": {
            "go.mod": """module my-wasm-app

go 1.21
""",
            "main.go": """package main

import "fmt"

func main() {
    fmt.Println("Hello from Go WASM!")
}
""",
        },
        "c": {
            "main.c": """#include <stdio.h>

int main() {
    printf("Hello from C WASM!\\n");
    return 0;
}
""",
        },
        "cpp": {
            "main.cpp": """#include <iostream>

int main() {
    std::cout << "Hello from C++ WASM!" << std::endl;
    return 0;
}
""",
        },
    }

    if language == "typescript":
        language = "javascript"

    template = templates.get(language, {})

    for file_path, content in template.items():
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            console.print(f"[dim]Skipping existing:[/dim] {file_path}")
        else:
            path.write_text(content)
            console.print(f"Created: {file_path}")

    if language == "wit":
        # Generate WIT file
        from utils.wasm_wit import generate_wit_file

        wit_path = Path("wit/world.wit")
        generate_wit_file(wit_path)
        console.print(f"Created: {wit_path}")
        console.print("\n[bold]WIT file created[/bold]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("  1. Edit wit/world.wit to define your interface")
        console.print("  2. Run: wasm-kit build")
        return

    console.print(f"\n[bold]{language.title()} project initialized[/bold]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Edit the source files")
    console.print("  2. Run: wasm-kit build")
    console.print("  3. Test: wasm-kit run")
