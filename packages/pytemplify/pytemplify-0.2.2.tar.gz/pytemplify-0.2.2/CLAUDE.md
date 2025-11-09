# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`pytemplify` is a generic text file generator framework that uses Jinja2 templates and user-defined parsers. It provides a powerful `TemplateRenderer` class with features like manual section preservation and content injection for template-based code generation.

## Core Architecture

- **Base Classes** (`pytemplify/base_classes.py`): Abstract base classes for data structures (`BaseDataClass`) and parsers (`BaseParserClass`)
- **Template Renderer** (`pytemplify/renderer.py`): Main rendering engine with manual section preservation and injection capabilities
- **Parser Loader** (`pytemplify/parser_loader.py`): Dynamic parser loading system
- **CLI Entry Point** (`pytemplify/main.py`): Command-line interface for template generation
- **Generator Initializer** (`scripts/mygen_init.py`): Creates skeleton projects using `mygen-init` command

## Essential Commands

**Important: Always use `uv run` to execute Python commands and tools.**

### Testing and Quality
```bash
# Run all sessions (format, lint, tests)
uv run nox

# Run only tests
uv run nox -s tests

# Run only linting
uv run nox -s lint

# Run only code formatting
uv run nox -s format_code

# Run pytest directly (from virtual environment)
uv run pytest -v --ignore=temp

# Run specific test
uv run pytest tests/unit_test/test_renderer.py -v
```

### Development Environment
```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### Build and Publish
```bash
# Build package
uv build

# Publish to PyPI
uv publish

# Publish to test PyPI
uv publish --repository testpypi
```

## Key Features

### Template Renderer
The `TemplateRenderer` class supports:
- **Manual Sections**: Preserve user-modified content between regenerations using `MANUAL SECTION START/END` markers
- **Content Injection**: Inject content into existing files using injection patterns
- **Template Directory Processing**: Generate entire directory structures from templates

### Error Handling
- Uses `TemplateRendererException` with clickable file URI encoding in error messages
- `RenderContext` tracks filename and line numbers for debugging

### Code Style and Principles
- **SOLID Principles**: Follow Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion principles
- **DRY Principle**: Don't Repeat Yourself - extract common functionality into reusable methods
- **Refactoring**: When methods become complex (>15 local variables, >50 statements), split into smaller focused methods
- Black formatting with 120 character line length
- isort for import organization
- Pylint with custom rules (disables `too-few-public-methods`, `too-many-return-statements`)
- All configuration in `pyproject.toml`
- Always use `uv run` to execute Python commands and tools