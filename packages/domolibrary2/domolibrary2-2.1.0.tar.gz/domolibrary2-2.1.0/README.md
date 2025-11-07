# Domolibrary

A Python library for interacting with Domo APIs.

## Installation

```bash
pip install domolibrary
```

## Usage

```python
from domolibrary import DomoUser
# Your code here
```

## Project Structure

```
src/                      # Main package source code
├── classes/              # Domain model classes
├── client/               # API client utilities
├── integrations/         # Integration modules
├── routes/               # API route implementations
├── utils/                # Utility functions
├── __init__.py           # Package initialization
└── _modidx.py           # Module index
scripts/                  # Development scripts
tests/                    # Test files
.vscode/                  # VS Code configuration
.github/workflows/        # CI/CD workflows
```

## Development

This project uses `uv` for dependency management and development.

### Setup Development Environment

```powershell
# Initial setup (run once)
.\scripts\setup-dev.ps1
```

This will:
- Install all dependencies (including dev dependencies)
- Set up pre-commit hooks for automatic code quality checks

### Development Scripts

All development scripts are located in the `scripts/` folder. See `scripts/README.md` for detailed documentation.

**Quick reference:**
- **`.\scripts\setup-dev.ps1`** - Setup development environment
- **`.\scripts\format-code.ps1`** - Manual code formatting (fallback)
- **`.\scripts\lint.ps1`** - Run linting and type checking
- **`.\scripts\test.ps1`** - Run tests with coverage
- **`.\scripts\build.ps1`** - Build the package
- **`.\scripts\publish.ps1`** - Publish to PyPI (with validation)

### Manual Development Commands

If you prefer to run commands manually:

```powershell
# Install dependencies
uv sync --dev

# Run linting
uv run ruff check src --fix
uv run black src
uv run isort src
uv run pylint src
uv run mypy src

# Run tests
uv run pytest tests/ --cov=src

# Build package
uv build

# Publish (after all checks pass)
uv publish
```

### Pre-commit Hooks

This project uses pre-commit hooks to automatically check code quality before commits:
- **Ruff** - Fast Python linter
- **Black** - Code formatter
- **isort** - Import sorter

Hooks are installed automatically by `setup-dev.ps1`. If they cause issues, you can use `.\scripts\format-code.ps1` as a fallback.
