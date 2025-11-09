# sphinx-autodoc-toml

A Sphinx extension for documenting TOML configuration files with embedded directives.

[![Tests](https://github.com/calvingiles/autodoc-toml/actions/workflows/test.yml/badge.svg)](https://github.com/calvingiles/autodoc-toml/actions/workflows/test.yml)
[![Lint](https://github.com/calvingiles/autodoc-toml/actions/workflows/lint.yml/badge.svg)](https://github.com/calvingiles/autodoc-toml/actions/workflows/lint.yml)
[![Build](https://github.com/calvingiles/autodoc-toml/actions/workflows/build.yml/badge.svg)](https://github.com/calvingiles/autodoc-toml/actions/workflows/build.yml)
[![Publish](https://github.com/calvingiles/autodoc-toml/actions/workflows/publish.yml/badge.svg)](https://github.com/calvingiles/autodoc-toml/actions/workflows/publish.yml)
[![Documentation](https://github.com/calvingiles/autodoc-toml/actions/workflows/docs.yml/badge.svg)](https://github.com/calvingiles/autodoc-toml/actions/workflows/docs.yml)
[![codecov](https://codecov.io/gh/calvingiles/autodoc-toml/branch/main/graph/badge.svg)](https://codecov.io/gh/calvingiles/autodoc-toml)
[![Python Versions](https://img.shields.io/pypi/pyversions/sphinx-autodoc-toml.svg)](https://pypi.org/project/sphinx-autodoc-toml/)

📖 [**Read the full documentation**](https://calvingiles.github.io/autodoc-toml/)

## Overview

`sphinx-autodoc-toml` enables you to embed documentation directly within your TOML configuration files (like `pyproject.toml`) using a special doc-comment syntax. This documentation can include Sphinx directives such as `sphinx-needs` requirements and specifications, keeping your configuration and its documentation in sync.

## The Problem

- `pyproject.toml` files are central to modern Python projects but are often complex and under-documented
- Configuration and the requirements that drive it live in separate places
- `sphinx-needs` is excellent for tracking requirements, but it's difficult to keep them synchronized with the configuration they refer to
- Standard TOML parsers discard comments, making documentation extraction impossible

## The Solution: TOML-Doc Specification

This project defines a formal "doc-comment" syntax that allows documentation to be embedded directly in TOML files:

### Syntax

The doc-comment marker is `#:` (hash followed by colon), which distinguishes doc-comments from regular `#` comments.

### Rules

1. **Separator Rule**: A doc-comment block MUST be preceded by at least one empty newline
2. **Attachment Rule**: A doc-comment block MUST NOT be separated from the item it documents by any empty newlines

### Example

```toml
[project]
name = "my-project"
version = "1.0.0"

# This is a regular comment and will be ignored

#: This doc-comment documents the 'dependencies' table.
#: It can be multi-line.
#:
#: .. spec:: All dependencies MUST be pinned.
#:    :id: S_DEPS_001
[project.dependencies]
flask = "==3.0.0"

#: This docstring documents only the 'pytest' key.
#:
#: .. req:: Pytest must be version 7 or higher.
#:    :id: R_TEST_001
pytest = ">=7.0.0"
```

## Installation

```bash
pip install sphinx-autodoc-toml
```

## Usage

### In Your Sphinx Configuration

Add the extension to your `conf.py`:

```python
extensions = [
    'sphinx_autodoc_toml',
    # ... other extensions
]
```

### In Your Documentation

Use the `autodoc-toml` directive to include TOML documentation:

```rst
.. autodoc-toml:: ../pyproject.toml
   :show-all:
   :recursive:
```

### Hierarchical Documentation

The extension supports hierarchical documentation of nested tables:

```toml
#: Documentation for the entire hatch build system.
#:
#: .. spec:: All hatch configuration must be tested.
#:    :id: S_HATCH_001
[hatch]

#: Documents the 'foo' subsection.
[hatch.foo]
my_foo_key = "value1"

#: Documents the 'bar' subsection.
[hatch.bar]
my_bar_key = "value2"
```

## Components

This project provides three components:

1. **TOML-Doc Specification**: A formal syntax for doc-comments in TOML
2. **sphinx-autodoc-toml**: The Sphinx extension (this package)
3. **toml-doc-lint**: A linter/formatter tool (planned)

## How It Works

The extension uses `tomlkit` (a round-trip TOML parser) to preserve comments and whitespace. It:

1. Parses the TOML file while preserving all comments
2. Walks the document tree recursively
3. Identifies valid doc-comment blocks using the TOML-Doc specification
4. Extracts the content and passes it to Sphinx's `nested_parse()`
5. Sphinx processes embedded directives (like `.. req::` or `.. spec::`) normally

## Development Status

This project is in active development. Current status:

- [x] TOML-Doc specification defined
- [x] Project structure created
- [x] Core parser implementation
- [x] Sphinx extension directive
- [x] Full documentation (dogfooded!)
- [x] GitHub Actions CI/CD
- [x] PyPI deployment workflow
- [ ] Linter tool (implementation in progress)
- [ ] Comprehensive test suite
- [ ] First PyPI release

## Development

This project uses [Hatch](https://hatch.pypa.io/) with [uv](https://docs.astral.sh/uv/) for development workflows.

### Setup

First, install uv and hatch:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install hatch
uv tool install hatch

# Install pre-commit hooks (automatically runs if using Claude Code)
hatch run setup
```

**Note:** If you're using Claude Code, the pre-commit hooks will be automatically installed when you start a session via the SessionStart hook.

### Common Tasks

```bash
# Run tests
hatch run test:run

# Run tests with coverage report
hatch run test:cov

# Run linting checks
hatch run lint:all

# Run individual lint checks
hatch run lint:check        # ruff check
hatch run lint:format-check # ruff format check
hatch run lint:typing       # mypy type checking

# Format code
hatch run lint:format

# Build documentation
hatch run docs:build

# Build package
hatch build
```

### Environments

Hatch manages separate environments for different tasks:

- **test**: Testing with pytest and coverage
- **lint**: Code quality checks with ruff and mypy
- **docs**: Documentation building with Sphinx

All environments use uv for fast dependency installation.

### Dependency Management

Dependencies are locked in `uv.lock` for reproducible builds:

```bash
uv lock      # Update lock file with latest compatible versions
uv sync      # Sync environment with lock file
```

The lock file is committed to version control to ensure everyone gets the same dependency versions.

### Releasing

For maintainers: see [RELEASING.md](RELEASING.md) for instructions on publishing releases to PyPI.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see LICENSE file for details.
