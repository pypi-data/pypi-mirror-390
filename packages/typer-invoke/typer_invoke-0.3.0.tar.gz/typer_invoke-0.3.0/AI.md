# AI Assistant Instructions for typer-invoke

## Project Overview

**typer-invoke** is a Python library that simplifies invocation of Typer apps from any directory within a project. It serves as a modern alternative to Make and Invoke, providing an improved developer experience for project management scripts.

### Key Concepts

- **Purpose**: Wrap custom project scripts as Typer apps and invoke them from anywhere in the project
- **Command**: Uses `inv` command (inspired by Invoke)
- **Configuration**: Defined in `pyproject.toml` under `[tool.typer-invoke]`
- **Module Pattern**: Typer apps are organized in directories (e.g., `admin/`, `sample/`) and registered as modules

## Project Structure

```
typer-invoke/
├── admin/              # Administrative tasks (build, pip management)
├── sample/             # Example implementations
├── src/                # Core library code
│   ├── invoke.py       # Main entry point
│   └── pyproject.py    # Configuration handling
├── tests/              # Test suite
├── pyproject.toml      # Project config & tool settings
└── README.md           # User documentation
```

## Development Standards

### Python Version
- Target: Python 3.12
- Minimum: Python 3.10

### Code Style
- **Formatter**: Black (line length: 100, skip string normalization)
- **Import sorting**: isort (black profile)
- **Type checking**: mypy (check_untyped_defs enabled, disallow_untyped_defs disabled)
- **Linting**: flake8 (max line length: 100)

### Key Configuration
```toml
[tool.typer-invoke]
modules = ['admin.build', 'admin.pip', 'sample.hello']
no_args_is_help = true
add_completion = false
rich_markup_mode = 'markdown'
```

## Coding Guidelines

1. **Type Hints**: Use type hints where practical, but `disallow_untyped_defs` is disabled for flexibility
2. **Documentation**: Typer supports Markdown in docstrings - use it for rich help text
3. **Dependencies**: Keep minimal - only `typer` and `tomli` (for Python ≤3.10)
4. **Testing**: pytest with strict markers enabled
5. **Virtual Environments**: Use `.venv*` or `venv*` naming pattern

## Common Tasks

### Testing
```bash
pytest
```

### Code Quality
```bash
black .
isort .
mypy .
flake8 .
```

### Build
Uses the `admin.build` module via the `inv` command.

## Architecture Notes

- **Entry point**: `inv` script points to `src.invoke:main`
- **Module discovery**: Reads `pyproject.toml` to find registered Typer apps
- **Rich output**: Leverages the `rich` library for enhanced terminal output
- **Markdown support**: Help text can use Markdown formatting

## Design Philosophy

- **Simplicity**: Easier to use than Make or Invoke
- **Modern**: Built on Typer (widely supported) rather than legacy tools
- **Intuitive**: Standard CLI patterns (e.g., `cmd subcommand --help` not `cmd --help subcommand`)
- **Beautiful**: Rich terminal output with Markdown support

## When Making Changes

1. Follow black/isort formatting (configs in `pyproject.toml`)
2. Run type checking with mypy
3. Add tests in `tests/` directory
4. Update README.md if user-facing changes
5. Ensure Python 3.10+ compatibility
6. Keep dependencies minimal
