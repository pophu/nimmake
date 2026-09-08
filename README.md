# nimmake

A Nimble cross-platform build tool optimized for ARM and RISC-V architectures.A Python-powered build system for MCU firmware development. Compile C/C++ source code for arm riscv, and other common microcontrollers with ease.
Built-in extensive MCU and toolchain configurations, automatically generating the required compile flags. Add code as third-party libraries without manually adding source files, headers, or macros one by one; you can set dependencies between each library. Especially suitable for rapid development and prototyping.

## Features

- Multi-Toolchain Support — Use armgcc, LLVM/Clang, or armclang to compile your firmware.
- Modular Third-Party Integration — Pre-built modules for FreeRTOS, LVGL, FatFS, EasyLogger, CherryUSB, FreeModbus, and more.
- Incremental Builds — Analyzes which files need rebuilding and compiles only what changed.
- Multi-Processing Build — Parallel compilation with configurable job count (-j).
- Ninja Backend — Optional Ninja build mode for faster builds (-n or --ninja).
- Compilation Database — Generate compile_commands.json for IDE support and static analysis (--compiledb).
- Build Cache — Cache compiled objects to speed up rebuilds (--cache).
- Dry-Run Mode — Preview what would be built without actually compiling (--dry-run).
- Party System — Organize third-party library flags and configurations in reusable "party" modules.

## Installation

```bash
pip install nimmake
```

## Usage

```bash
nimmake -f Nimmake.py
nimmake --version
nimmake --compiledb
```

## Development

```bash
# Clone the repo
git clone https://github.com/pophu/nimmake.git
cd nimmake

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dev dependencies
pip install -e ".[dev]"
pip install -e .

# Run tests
pytest

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Build
python -m build
```
