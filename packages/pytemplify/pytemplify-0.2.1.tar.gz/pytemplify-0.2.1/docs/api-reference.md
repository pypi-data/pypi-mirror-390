# API Reference

> **⚠️ NOTICE**: This document contains outdated API signatures that don't match the current implementation.
>
> **Please use instead**:
>
> - **[API.md](API.md)** - Complete and accurate API reference (recommended)
> - **[API-QUICK-REFERENCE.md](API-QUICK-REFERENCE.md)** - Quick lookup guide
>
> This file will be updated or merged in a future release. For now, refer to API.md for correct method signatures.

Complete Python API documentation for PyTemplify.

## TemplateRenderer

The main class for rendering Jinja2 templates with data.

### Constructor

```python
from pytemplify.renderer import TemplateRenderer

renderer = TemplateRenderer(
    data,                          # dict: Your data
    filters=None,                  # dict: Custom Jinja2 filters
    auto_register_filters=True,    # bool: Auto-register built-in filters
    template_folder=None           # str: Default template folder
)
```

**Parameters:**
- `data` (dict): The data dictionary to use for template rendering
- `filters` (dict, optional): Custom Jinja2 filters to register
- `auto_register_filters` (bool): Whether to automatically register built-in filters (default: True)
- `template_folder` (str, optional): Default folder for template files

### Methods

#### render_string()

Render a template string with data.

```python
result = renderer.render_string(
    template_str,              # str: Template string
    previous=None,             # str: Previous content for manual sections
    filename=None              # str: Filename for error reporting
)
```

**Parameters:**
- `template_str` (str): The Jinja2 template string
- `previous` (str, optional): Previously rendered content (for manual section preservation)
- `filename` (str, optional): Filename for error reporting

**Returns:** `str` - The rendered template

**Example:**
```python
template = "Hello {{ name }}!"
result = renderer.render_string(template)
print(result)  # "Hello World!"
```

#### render_file()

Render a template file to an output file.

```python
renderer.render_file(
    template_path,             # str|Path: Template file path
    output_path,               # str|Path: Output file path
    preserve_manual_sections=True  # bool: Preserve manual sections
)
```

**Parameters:**
- `template_path` (str|Path): Path to the template file
- `output_path` (str|Path): Path to the output file
- `preserve_manual_sections` (bool): Whether to preserve manual sections (default: True)

**Example:**
```python
renderer.render_file("template.j2", "output.txt")
```

#### generate()

Generate an entire directory structure from templates.

```python
renderer.generate(
    temp_dirpath,              # str|Path: Template directory
    output_dirpath,            # str|Path: Output directory
    preserve_manual_sections=True,  # bool: Preserve manual sections
    template_filter=None       # callable: Filter function for templates
)
```

**Parameters:**
- `temp_dirpath` (str|Path): Path to the template directory
- `output_dirpath` (str|Path): Path to the output directory
- `preserve_manual_sections` (bool): Whether to preserve manual sections (default: True)
- `template_filter` (callable, optional): Function to filter which templates to process

**Example:**
```python
renderer.generate("templates/", "output/")

# With filter
def only_python(template_path):
    return template_path.suffix == ".py"

renderer.generate("templates/", "output/", template_filter=only_python)
```

#### inject_string()

Inject content into an existing file based on injection patterns.

```python
result = renderer.inject_string(
    template_str,              # str: Template with injection patterns
    existing_content,          # str: Existing file content
    filename=None              # str: Filename for error reporting
)
```

**Parameters:**
- `template_str` (str): Template string with injection patterns
- `existing_content` (str): Existing file content
- `filename` (str, optional): Filename for error reporting

**Returns:** `str` - The content with injections applied

**Example:**
```python
template = """
<!-- injection-pattern: imports -->
pattern: (?P<injection>import .*)
<!-- injection-string-start -->
import os
import sys
<!-- injection-string-end -->
"""

existing = "import os\n# Other code"
result = renderer.inject_string(template, existing)
```

#### set_env_options()

Configure Jinja2 environment options.

```python
renderer.set_env_options(
    trim_blocks=True,          # bool: Remove first newline after tag
    lstrip_blocks=True,        # bool: Strip leading spaces before block
    autoescape=False,          # bool: Enable HTML escaping
    keep_trailing_newline=False  # bool: Keep trailing newline
)
```

**Parameters:**
- `trim_blocks` (bool): Remove first newline after template tag
- `lstrip_blocks` (bool): Strip leading spaces/tabs before block tags
- `autoescape` (bool): Enable automatic HTML escaping
- `keep_trailing_newline` (bool): Keep trailing newline at end of template

**Example:**
```python
renderer.set_env_options(
    trim_blocks=True,
    lstrip_blocks=True
)
```

## Data Helpers

For working with enhanced data structures.

### wrap_with_helpers()

Wrap dictionary data with helper extensions.

```python
from pytemplify.data_helpers import wrap_with_helpers

wrapped = wrap_with_helpers(
    data,                      # dict: Data to wrap
    helpers,                   # list: List of DataHelper classes
    auto_order=True            # bool: Automatically order by specificity
)
```

**Parameters:**
- `data` (dict): Dictionary data to wrap
- `helpers` (List[Type[DataHelper]]): List of DataHelper classes
- `auto_order` (bool): Automatically order helpers by specificity (default: True)

**Returns:** `DictProxy` - Wrapped dictionary with helpers applied

**Example:**
```python
from pytemplify.data_helpers import wrap_with_helpers, DataHelper

class CompanyHelpers(DataHelper):
    @staticmethod
    def matches(data: dict) -> bool:
        return "company_name" in data

    @property
    def employee_count(self):
        return len(self._data.employees)

wrapped = wrap_with_helpers(data, [CompanyHelpers])
print(wrapped.employee_count)
```

### DataHelper

Base class for creating data helpers.

```python
from pytemplify.data_helpers import DataHelper

class MyHelper(DataHelper):
    @staticmethod
    def matches(data: dict) -> bool:
        """Return True if this helper applies to the data."""
        return "required_key" in data

    @property
    def computed_value(self):
        """Computed properties are accessible as attributes."""
        return self._data.some_field * 2

    def helper_method(self, param):
        """Methods can accept parameters."""
        return [item for item in self._data.items if item > param]
```

**Attributes available in helpers:**
- `self._data`: Smart wrapper that auto-wraps nested values
- `self._raw_data`: Unwrapped original dictionary
- `self._root_data`: Root-level data for cross-level queries
- `self._parent_data`: Parent-level data (None at root)

## Built-in Filters

PyTemplify includes several built-in Jinja2 filters.

### String Filters

```python
# Convert to snake_case
{{ "CamelCase" | snake_case }}  # "camel_case"

# Convert to camelCase
{{ "snake_case" | camel_case }}  # "snakeCase"

# Convert to PascalCase
{{ "snake_case" | pascal_case }}  # "SnakeCase"

# Convert to kebab-case
{{ "snake_case" | kebab_case }}  # "snake-case"

# Pluralize
{{ "box" | pluralize }}  # "boxes"

# Singularize
{{ "boxes" | singularize }}  # "box"
```

### Collection Filters

```python
# Group by attribute
{{ items | group_by('category') }}

# Unique values
{{ items | unique }}

# Flatten nested lists
{{ nested_list | flatten }}

# Sort by attribute
{{ items | sort_by('name') }}
```

### Utility Filters

```python
# Default value
{{ value | default('N/A') }}

# Date formatting
{{ timestamp | format_date('%Y-%m-%d') }}
```

## YAML Generator (yagen)

The YAML-based generator is the recommended approach for most use cases.

### Command Line

Basic usage:
```bash
yagen --config templates.yaml --data data.json
```

For complete CLI reference including all options, filtering patterns, helpers, and examples, see [YAGEN Guide - Command-Line Reference](yagen-guide.md#command-line-reference).

### Configuration Schema

For complete YAML configuration reference including all options, iteration patterns, data helpers, and formatting, see [YAGEN Guide - Configuration Reference](yagen-guide.md#configuration-reference).

Basic structure:
```yaml
globals:
  version: "1.0.0"

templates:
  - name: "Service Files"
    folder: "templates"
    output: "output"
    iterate: "service in services"  # Optional
```

## Exceptions

### TemplateRendererException

Raised when template rendering fails.

```python
from pytemplify.renderer import TemplateRendererException

try:
    renderer.render_string(template)
except TemplateRendererException as e:
    print(f"Error: {e}")
    print(f"File: {e.filename}")
    print(f"Line: {e.line_number}")
```

## Type Hints

PyTemplify is fully typed. Import types:

```python
from pytemplify.renderer import TemplateRenderer
from pytemplify.data_helpers import DataHelper, DictProxy
from pathlib import Path
from typing import Dict, List, Optional

def my_function(data: Dict, helpers: List[type[DataHelper]]) -> DictProxy:
    return wrap_with_helpers(data, helpers)
```

## Advanced Topics

### Custom Filters

Create custom Jinja2 filters:

```python
def reverse_string(text):
    return text[::-1]

custom_filters = {"reverse": reverse_string}
renderer = TemplateRenderer(data, filters=custom_filters)

# In template: {{ "hello" | reverse }}  # "olleh"
```

### Template Context

Access special variables in templates:

```python
# Current data (flattened by default)
{{ project_name }}

# Data dictionary (namespaced)
{{ dd.project_name }}

# Global variables
{{ gg.version }}

# Current iteration variable
{{ service.name }}  # when iterating over services

# Raw unwrapped data
{{ dd_raw.some_field }}
```

### Manual Section Configuration

Manual sections use standard markers to preserve user code between regenerations. See [Template Guide - Manual Sections](template-guide.md#manual-sections) for comprehensive documentation including:
- Marker syntax and usage
- Best practices for section naming
- Multiple sections in one file
- Integration with formatters

## Best Practices

1. **Use YAML configuration (yagen)** for most projects instead of Python API
2. **Enable data flattening** for simpler template syntax (default)
3. **Use data helpers** for computed properties instead of pre-processing data
4. **Organize templates** with `_foreach_` prefix for clarity
5. **Preserve manual sections** to allow safe regeneration
6. **Use specific helper matching** to avoid conflicts
7. **Cache expensive computations** with `@cached_property`
8. **Handle errors gracefully** in helpers with `.get()` and try/except

## See Also

- [Getting Started](getting-started.md) - Quick start guide
- [YAGEN Guide](yagen-guide.md) - Advanced YAML-based generation
- [Data Helpers Guide](data-helpers.md) - Complete data helpers documentation
- [Template Guide](template-guide.md) - Template writing best practices
- [Examples](../examples/README.md) - Working examples
