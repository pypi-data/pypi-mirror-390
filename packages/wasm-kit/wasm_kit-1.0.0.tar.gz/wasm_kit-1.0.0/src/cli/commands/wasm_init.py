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
@click.option(
    "--template",
    "-t",
    type=click.Choice(["basic", "http", "api", "mcp"]),
    default="basic",
    help="Project template type",
)
@click.option(
    "--name",
    "-n",
    default="my-wasm-component",
    help="Project name",
)
def init(language: str, template: str, name: str):
    """Initialize a new WASM project."""
    console.print(f"Creating a new {language.title()} WASM project ({template} template)...")

    # Create project structure based on template
    if template == "http":
        files = _get_http_template(language, name)
    elif template == "api":
        files = _get_api_template(language, name)
    elif template == "mcp":
        files = _get_mcp_template(language, name)
    else:  # basic
        files = _get_basic_template(language, name)

    # Write files
    for file_path, content in files.items():
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            console.print(f"[dim]Skipping existing:[/dim] {file_path}")
        else:
            path.write_text(content)
            console.print(f"Created: {file_path}")

    if language == "wit":
        console.print("\n[bold]WIT file created[/bold]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("  1. Edit wit/world.wit to define your interface")
        console.print("  2. Run: wasm-kit build")
        return

    console.print(f"\n[bold]{language.title()} project initialized[/bold]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Edit the source files")
    console.print("  2. Run: wasm-kit build")
    console.print("  3. Serve: wasm-kit serve")
    console.print(
        "\n[dim]The serve command will automatically create a REST API for your functions[/dim]"
    )


def _get_basic_template(language: str, name: str) -> dict:
    """Get basic template files."""
    if language == "typescript":
        language = "javascript"

    templates = {
        "rust": {
            "Cargo.toml": f"""[package]
name = "{name}"
version = "0.1.0"
edition = "2021"

[dependencies]

[lib]
crate-type = ["cdylib"]

[package.metadata.component]
package = "component:{name}"
""",
            "src/lib.rs": """#[no_mangle]
pub extern "C" fn run() -> i32 {
    println!("Hello from Rust WASM!");
    42
}
""",
        },
        "javascript": {
            "package.json": f"""{{
  "name": "{name}",
  "version": "0.1.0",
  "main": "index.js",
  "type": "module"
}}
""",
            "index.js": """export function run() {
  console.log("Hello from JavaScript WASM!");
  return "Success";
}
""",
            "wit/world.wit": f"""package example:{name};

world app {{
  export run: func() -> string;
}}
""",
        },
        "python": {
            "main.py": """import wit_world

class WitWorld(wit_world.WitWorld):
    def run(self) -> str:
        return "Hello from Python WASM component!"

if __name__ == "__main__":
    component = WitWorld()
    print(component.run())
""",
            "requirements.txt": """componentize-py==0.13.5
""",
            "wit/world.wit": f"""package example:{name};

world wit-world {{
  export run: func() -> string;
}}
""",
            "README.md": f"""# {name}

A Python WebAssembly component built with componentize-py.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Build the component:
   ```bash
   wasm-kit build
   ```

3. Test locally (dev server with hot-reload):
   ```bash
   wasm-kit dev
   ```

4. Access the API:
   - Documentation: http://localhost:8080/docs
   - Test the `run` function directly in the interactive docs

## Project Structure

- `main.py` - Component implementation (WitWorld class)
- `wit/world.wit` - WebAssembly Interface Type definition
- `requirements.txt` - Python dependencies

## How It Works

This component uses componentize-py to create a WebAssembly Component Model binary.
The `WitWorld` class implements the interface defined in `wit/world.wit`.
""",
        },
        "go": {
            "go.mod": f"""module {name}

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
        "wit": {
            "wit/world.wit": f"""package example:{name};

world app {{
  export run: func() -> string;
}}
""",
        },
    }

    return templates.get(language, {})


def _get_api_template(language: str, name: str) -> dict:
    """Get multi-function API template."""
    if language == "typescript":
        language = "javascript"

    templates = {
        "python": {
            "main.py": """import wit_world

class WitWorld(wit_world.WitWorld):
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"

    def add(self, a: int, b: int) -> int:
        return a + b

    def process_data(self, data: str) -> str:
        return data.upper()

    def get_info(self) -> str:
        return "Multi-function API Component v1.0"

if __name__ == "__main__":
    component = WitWorld()
    print(component.greet("World"))
    print(component.add(5, 3))
    print(component.process_data("test"))
    print(component.get_info())
""",
            "requirements.txt": """componentize-py==0.13.5
""",
            "wit/world.wit": f"""package example:{name};

world wit-world {{
  export greet: func(name: string) -> string;
  export add: func(a: s32, b: s32) -> s32;
  export process-data: func(data: string) -> string;
  export get-info: func() -> string;
}}
""",
            "README.md": f"""# {name}

A multi-function Python WebAssembly API component.

## Functions

- `greet(name: string) -> string` - Greet a user
- `add(a: int, b: int) -> int` - Add two numbers
- `process-data(data: string) -> string` - Process data
- `get-info() -> string` - Get component info

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Test locally:
   ```bash
   python main.py
   ```

3. Build component:
   ```bash
   wasm-kit build
   ```

4. Start dev server:
   ```bash
   wasm-kit dev
   ```

5. Try the API at: http://localhost:8080/docs

## Example Usage

```bash
# Greet
curl -X POST http://localhost:8080/api/greet \\
  -H "Content-Type: application/json" \\
  -d '{{"args": ["Alice"]}}'

# Add numbers
curl -X POST http://localhost:8080/api/add \\
  -H "Content-Type: application/json" \\
  -d '{{"args": [10, 5]}}'
```
""",
        },
        "javascript": {
            "package.json": f"""{{
  "name": "{name}",
  "version": "0.1.0",
  "main": "index.js",
  "type": "module"
}}
""",
            "index.js": """export function greet(name) {
  return `Hello, ${name}!`;
}

export function add(a, b) {
  return a + b;
}

export function processData(data) {
  return data.toUpperCase();
}

export function getInfo() {
  return "Multi-function API Component v1.0";
}
""",
            "wit/world.wit": f"""package example:{name};

world app {{
  export greet: func(name: string) -> string;
  export add: func(a: s32, b: s32) -> s32;
  export process-data: func(data: string) -> string;
  export get-info: func() -> string;
}}
""",
        },
        "rust": {
            "Cargo.toml": f"""[package]
name = "{name}"
version = "0.1.0"
edition = "2021"

[dependencies]

[lib]
crate-type = ["cdylib"]

[package.metadata.component]
package = "component:{name}"
""",
            "src/lib.rs": """#[no_mangle]
pub extern "C" fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

#[no_mangle]
pub extern "C" fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[no_mangle]
pub extern "C" fn process_data(data: &str) -> String {
    data.to_uppercase()
}

#[no_mangle]
pub extern "C" fn get_info() -> String {
    "Multi-function API Component v1.0".to_string()
}
""",
            "wit/world.wit": f"""package example:{name};

world app {{
  export greet: func(name: string) -> string;
  export add: func(a: s32, b: s32) -> s32;
  export process-data: func(data: string) -> string;
  export get-info: func() -> string;
}}
""",
        },
    }

    return templates.get(language, {})


def _get_http_template(language: str, name: str) -> dict:
    """Get wasi:http template."""
    if language == "typescript":
        language = "javascript"

    # Note: wasi:http templates are more complex and require specific setup
    # For now, return API template with HTTP-ready structure
    templates = _get_api_template(language, name)

    # Add a note about HTTP capabilities
    if "python" in templates or language == "python":
        readme = """# HTTP API Component

This component exports functions that can be called via HTTP using `wasm-kit serve`.

## Usage

1. Build the component:
   ```
   wasm-kit build
   ```

2. Serve it:
   ```
   wasm-kit serve
   ```

3. Access the API:
   - API Documentation: http://localhost:8080/docs
   - List functions: http://localhost:8080/api
   - Call a function: POST http://localhost:8080/api/greet

## Example Request

```bash
curl -X POST http://localhost:8080/api/greet \\
  -H "Content-Type: application/json" \\
  -d '{"args": ["World"]}'
```

## Features

- Auto-generated REST API for all exported functions
- Swagger UI documentation
- Hot-reload with `--watch` flag
- CORS enabled for frontend integration
"""
        templates["README.md"] = readme

    return templates


def _get_mcp_template(language: str, name: str) -> dict:
    """Get MCP (Model Context Protocol) template."""
    if language == "typescript":
        language = "javascript"

    templates = {
        "python": {
            "main.py": """import json

def list_tools() -> str:
    tools = [
        {"name": "greet", "description": "Greet a user"},
        {"name": "calculate", "description": "Perform calculations"},
    ]
    return json.dumps(tools)

def call_tool(tool_name: str, args: str) -> str:
    args_dict = json.loads(args)

    if tool_name == "greet":
        name = args_dict.get("name", "Guest")
        return json.dumps({"result": f"Hello, {name}!"})
    elif tool_name == "calculate":
        a = args_dict.get("a", 0)
        b = args_dict.get("b", 0)
        op = args_dict.get("op", "+")

        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op == "*":
            result = a * b
        elif op == "/":
            result = a / b if b != 0 else "Error: Division by zero"
        else:
            result = "Error: Unknown operation"

        return json.dumps({"result": result})
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
""",
            "requirements.txt": "# Add your dependencies here\n",
            "wit/world.wit": f"""package mcp:{name};

world mcp-server {{
  export list-tools: func() -> string;
  export call-tool: func(tool-name: string, args: string) -> string;
}}
""",
        },
        "javascript": {
            "package.json": f"""{{
  "name": "{name}",
  "version": "0.1.0",
  "main": "index.js",
  "type": "module"
}}
""",
            "index.js": """export function listTools() {
  const tools = [
    { name: "greet", description: "Greet a user" },
    { name: "calculate", description: "Perform calculations" }
  ];
  return JSON.stringify(tools);
}

export function callTool(toolName, args) {
  const argsObj = JSON.parse(args);

  if (toolName === "greet") {
    const name = argsObj.name || "Guest";
    return JSON.stringify({ result: `Hello, ${name}!` });
  } else if (toolName === "calculate") {
    const { a = 0, b = 0, op = "+" } = argsObj;
    let result;

    switch (op) {
      case "+": result = a + b; break;
      case "-": result = a - b; break;
      case "*": result = a * b; break;
      case "/": result = b !== 0 ? a / b : "Error: Division by zero"; break;
      default: result = "Error: Unknown operation";
    }

    return JSON.stringify({ result });
  } else {
    return JSON.stringify({ error: `Unknown tool: ${toolName}` });
  }
}
""",
            "wit/world.wit": f"""package mcp:{name};

world mcp-server {{
  export list-tools: func() -> string;
  export call-tool: func(tool-name: string, args: string) -> string;
}}
""",
        },
    }

    return templates.get(language, {})
