# speedywalk

Fast parallel directory walking for Python, powered by Rust.

## Features

- 🚀 **Fast**: Uses the rust [ignore](https://crates.io/crates/ignore) crate for fast directory traversal.
- ⚡ **Parallel**: Multi-threaded directory traversal.
- 🎯 **Smart filtering**: Built-in support for `.gitignore`, `.ignore`, and glob patterns.
- 🔒 **Type-safe**: Full type hints.

## Installation

```bash
pip install speedywalk
```

## Usage

```python
import speedywalk

# Find all Python files, respecting .gitignore
for entry in speedywalk.walk(".", filters=["*.py"]):
    if entry.is_file:
        print(entry.path)

# Custom configuration
for entry in speedywalk.walk(
    ".",
    filters=["*.yaml", "*.yml"],
    ignore_dirs=["node_modules", "venv"],
    max_depth=3,
    threads=4,
):
    print(entry.path_str, entry.is_dir)
```
