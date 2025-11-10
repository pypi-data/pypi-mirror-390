# speedywalk

[![PyPI](https://img.shields.io/pypi/v/speedywalk.svg)](https://pypi.org/project/speedywalk/)
[![CI](https://github.com/Peter554/speedywalk/actions/workflows/check.yml/badge.svg)](https://github.com/Peter554/speedywalk/actions/workflows/check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://peter554.github.io/speedywalk/)

Fast parallel directory walking for Python, powered by Rust.

- Find the repo [here](https://github.com/Peter554/speedywalk).
- Read the docs [here](https://peter554.github.io/speedywalk/).

## Features

- 🚀 **Fast**: Uses the rust [ignore](https://crates.io/crates/ignore) crate for fast directory traversal.
- ⚡ **Parallel**: Multi-threaded directory traversal.
- 🎯 **Smart filtering**: Built-in support for `.gitignore`, `.ignore`, and glob patterns.
- 🔒 **Type-safe**: Full type hints.

## Installation

```bash
pip install speedywalk
```

## Quick Start

```python
import speedywalk

# Find all Python files, respecting .gitignore
for entry in speedywalk.walk(".", filter="**/*.py"):
    if entry.is_file:
        print(entry.path)

# Custom configuration with filtering and exclusion
for entry in speedywalk.walk(
    ".",
    filter=["**/*.yaml", "**/*.yml"],
    exclude=["**/node_modules", "**/__pycache__"],
    max_depth=3,
    threads=4,
):
    print(entry.path_str, entry.is_dir)
```
