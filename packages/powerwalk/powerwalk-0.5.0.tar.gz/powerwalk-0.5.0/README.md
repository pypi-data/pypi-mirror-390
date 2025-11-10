# powerwalk

[![PyPI](https://img.shields.io/pypi/v/powerwalk.svg)](https://pypi.org/project/powerwalk/)
[![CI](https://github.com/Peter554/powerwalk/actions/workflows/check.yml/badge.svg)](https://github.com/Peter554/powerwalk/actions/workflows/check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://peter554.github.io/powerwalk/)

Fast parallel directory walking for Python, powered by Rust.

- Find the repo [here](https://github.com/Peter554/powerwalk).
- Read the docs [here](https://peter554.github.io/powerwalk/).

## Features

- 🚀 **Fast**: Uses the rust [ignore](https://crates.io/crates/ignore) crate for fast directory traversal.
- ⚡ **Parallel**: Multi-threaded directory traversal.
- 🎯 **Smart filtering**: Built-in support for `.gitignore`, `.ignore`, and glob patterns.
- 🔒 **Type-safe**: Full type hints.

## Installation

```bash
pip install powerwalk
```

## Quick Start

```python
import powerwalk

# Find all Python files, respecting .gitignore
for entry in powerwalk.walk(".", filter="**/*.py"):
    if entry.is_file:
        print(entry.path)

# Custom configuration with filtering and exclusion
for entry in powerwalk.walk(
    ".",
    filter=["**/*.yaml", "**/*.yml"],
    exclude=["**/node_modules", "**/__pycache__"],
    max_depth=3,
    threads=4,
):
    print(entry.path_str, entry.is_dir)
```
