# PyTemplify Documentation

Comprehensive documentation for PyTemplify - a data-driven code generation framework.

## Getting Started

New to PyTemplify? Start here:

- **[Getting Started Guide](getting-started.md)** - Installation, quick start, and core concepts
- **[Examples](../examples/README.md)** - Working examples to learn from

## User Guides

### Core Features

- **[Template Guide](template-guide.md)** - Master Jinja2 template writing
  - Template syntax and best practices
  - Manual section preservation
  - Control structures and filters
  - Common patterns

- **[Filters Reference](filters-reference.md)** - Complete built-in filters documentation
  - 70+ filters across 4 categories
  - String manipulation (case conversion, regex, etc.)
  - Collection operations (filter, sort, group, etc.)
  - Formatting (numbers, dates, currency, etc.)
  - Utilities (type checking, hashing, UUIDs, etc.)

- **[YAGEN Guide](yagen-guide.md)** - YAML-based generator (recommended)
  - Configuration reference
  - Iteration patterns (simple, conditional, nested)
  - Template organization
  - Command-line usage

- **[Data Helpers Guide](data-helpers.md)** - Add computed properties to data
  - Creating custom helpers
  - Nested data and cross-helper communication
  - Integration with templates
  - Best practices

- **[Custom Generators Guide](custom-generators-guide.md)** - Create reusable generators
  - Extending GenericCodeGenerator
  - Hook methods for customization
  - Multi-config generation patterns
  - Dynamic helper and context modification

- **[Formatting Guide](formatting.md)** - Automatic code formatting
  - Black, Prettier, and custom formatters
  - Manual section preservation during formatting
  - Per-file-type configuration

- **[Validation Guide](validation-user-guide.md)** - Validate generated files
  - Built-in validators (GTest, JSON Schema, File Structure)
  - Custom validator creation
  - Interactive validation CLI
  - CI/CD integration

### API Reference

- **[API Reference](API.md)** - Complete Python API documentation (recommended)
  - TemplateRenderer class
  - Data helpers API
  - Built-in filters
  - YAML generator (yagen)
  - Exceptions and type hints

- **[API Quick Reference](API-QUICK-REFERENCE.md)** - Quick lookup guide
  - Common imports and usage patterns
  - Method signatures at a glance

## Documentation Structure

```
docs/
├── README.md                   # This file - documentation index
├── getting-started.md          # Quick start and installation
├── api-reference.md            # Complete API documentation
├── filters-reference.md        # Complete built-in filters reference (70+ filters)
├── yagen-guide.md             # YAML-based generator guide
├── data-helpers.md            # Data helpers complete guide
├── custom-generators-guide.md # Custom generator creation guide
├── template-guide.md          # Template writing guide
└── formatting.md              # Code formatting guide
```

## Quick Links

### By Task

**I want to...**

- **Get started quickly** → [Getting Started](getting-started.md)
- **Use YAML configuration** → [YAGEN Guide](yagen-guide.md)
- **Write templates** → [Template Guide](template-guide.md)
- **Use filters** → [Filters Reference](filters-reference.md)
- **Add computed properties** → [Data Helpers Guide](data-helpers.md)
- **Create custom generators** → [Custom Generators Guide](custom-generators-guide.md)
- **Format generated code** → [Formatting Guide](formatting.md)
- **Validate generated files** → [Validation Guide](validation-user-guide.md)
- **Use Python API** → [API Reference](API.md)
- **See examples** → [Examples](../examples/README.md)

### By Experience Level

**Beginner:**
1. [Getting Started](getting-started.md) - Learn the basics
2. [Examples - Basic](../examples/basic/) - Simple example
3. [Template Guide](template-guide.md) - Write templates

**Intermediate:**
1. [YAGEN Guide](yagen-guide.md) - Advanced features
2. [Examples - Advanced](../examples/advanced/) - Complex patterns
3. [Data Helpers Guide](data-helpers.md) - Computed properties
4. [Custom Generators Guide](custom-generators-guide.md) - Reusable generators

**Advanced:**
1. [API Reference](api-reference.md) - Full Python API
2. [Custom Generators Guide](custom-generators-guide.md) - Advanced patterns
3. [Examples - With Helpers](../examples/with_helpers/) - Helpers example
4. [Formatting Guide](formatting.md) - Advanced formatting

## Features Overview

### Template-Based Generation

Generate code from Jinja2 templates with rich data access:

```jinja2
class {{ service.name | pascal_case }}Service:
    PORT = {{ service.port }}

    # MANUAL SECTION START: custom_methods
    # Your code preserved here
    # MANUAL SECTION END
```

### YAML Configuration

Declarative configuration for complex generation:

```yaml
globals:
  version: "1.0.0"

templates:
  - name: "Services"
    folder: "templates"
    output: "generated"
    iterate: "service in services if service.enabled"
```

### Data Helpers

Add computed properties without modifying data:

```python
class CompanyHelpers(DataHelper):
    @property
    def total_employees(self):
        return sum(len(dept.employees) for dept in self._data.departments)
```

### Manual Section Preservation

Safely regenerate files while preserving user edits. See [Template Guide - Manual Sections](template-guide.md#manual-sections) for complete documentation.

```jinja2
# MANUAL SECTION START: custom_code
# User edits preserved here
# MANUAL SECTION END
```

### Automatic Formatting

Format generated code with Black, Prettier, or custom formatters:

```yaml
format:
  enabled: true
  formatters:
    ".py":
      type: "black"
      options:
        line_length: 88
```

## Common Use Cases

1. **Microservices Boilerplate** - Generate service files from configuration
2. **API Handler Generation** - Create handlers from OpenAPI specs
3. **Test File Generation** - Generate test structures from test data
4. **Documentation** - Generate docs with computed metrics
5. **Configuration Files** - Create environment-specific configs

## Getting Help

- **Check documentation** - Start with [Getting Started](getting-started.md)
- **Browse examples** - See [Examples](../examples/README.md)
- **Report issues** - https://github.com/robinbreast/pytemplify/issues

## Contributing

We welcome contributions! Areas where you can help:

- **Documentation** - Improve guides and examples
- **Examples** - Add more real-world examples
- **Formatters** - Add support for more formatters
- **Bug fixes** - Fix issues and improve stability

## License

PyTemplify is open source. Check the main repository for license details.

## Quick Reference

### Installation

See [Getting Started Guide](getting-started.md#installation) for installation instructions.

### CLI Usage

```bash
# Basic generation
yagen -c config.yaml -d data.json
```

For complete CLI reference including filtering, helpers, and all options, see [YAGEN Guide - Command Reference](yagen-guide.md#command-line-reference).

### Python API

```python
from pytemplify.renderer import TemplateRenderer

renderer = TemplateRenderer(data)
renderer.generate("templates/", "output/")
```

See [API Reference](api-reference.md) for complete Python API documentation.

### Template Syntax

Quick reference - see [Template Guide](template-guide.md) for complete documentation:

```jinja2
{{ variable }}                    {# Variables #}
{% if condition %}...{% endif %}  {# Conditionals #}
{% for item in items %}...{% endfor %}  {# Loops #}
{{ text | snakecase }}            {# Filters (70+ available) #}
```

## Version Information

This documentation is for PyTemplify 0.2.0. Check the main repository for the latest version.

---

**Ready to start?** → [Getting Started Guide](getting-started.md)
