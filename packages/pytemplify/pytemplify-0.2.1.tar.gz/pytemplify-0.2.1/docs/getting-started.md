# Getting Started with PyTemplify

PyTemplify is a data-driven code generation framework that safely regenerates files while preserving manual edits.

## Installation

```bash
pip install pytemplify
```

For formatting support:

```bash
pip install pytemplify[formatting]
```

## Quick Start (CLI)

The easiest way to use PyTemplify is through the `yagen` CLI tool with YAML configuration.

### Step 1: Create Your Data

Create a JSON data file (`services.json`):

```json
{
  "services": [
    { "name": "user", "port": 8080 },
    { "name": "order", "port": 8081 }
  ]
}
```

### Step 2: Create Templates

Create a template file (`templates/_foreach_service_{{ service.name }}_config.py.j2`):

```jinja2
# {{ service.name | upper() }} config
SERVICE_NAME = "{{ service.name }}"
SERVICE_PORT = {{ service.port }}

# MANUAL SECTION START: extras
# add custom code here (preserved on regen)
# MANUAL SECTION END
```

### Step 3: Create Configuration

Create a YAML configuration file (`config.yaml`):

```yaml
templates:
  - name: "Services"
    folder: "templates"
    output: "generated"
    iterate: "service in services"
```

### Step 4: Generate

```bash
yagen -c config.yaml -d services.json -o ./generated
```

Result: One file per service under `generated/` with manual sections preserved.

## Quick Start (Python API)

For programmatic use, you can use the Python API directly:

```python
from pytemplify.renderer import TemplateRenderer

# Your data
data = {
    "project": "MyApp",
    "services": [
        {"name": "auth", "port": 8080}
    ]
}

# Create renderer
renderer = TemplateRenderer(data)

# Render a string template
template = "Project: {{ project }}"
result = renderer.render_string(template)
print(result)  # "Project: MyApp"

# Generate entire directory
renderer.generate("templates/", "output/")
```

## Core Concepts

### Manual Sections

Manual sections allow you to preserve user-edited code between regenerations. See [Template Guide - Manual Sections](template-guide.md#manual-sections) for complete documentation including best practices and multiple section examples.

```jinja2
# MANUAL SECTION START: custom_code
# Your custom code here
# MANUAL SECTION END
```

### Template Organization

Use `_foreach_` prefix to control when templates are processed:

```
templates/
├── _foreach_service_main.py.j2     # Only for service iteration
├── _foreach_module_init.py.j2      # Only for module iteration
└── static_config.py.j2             # Always processed
```

### Data Access in Templates

PyTemplify supports two ways to access data:

1. **Flattened (default)**: `{{ project_name }}`
2. **Namespaced**: `{{ dd.project_name }}`

Both work simultaneously! The flattened approach is more convenient for simple templates.

### String Rendering (No File Output)

**New in v0.2.x**: You can now render templates to strings without writing files, perfect for emails, API responses, or dynamic content generation:

```python
from pytemplify.generator import GenericCodeGenerator

data = {"project_name": "MyAPI", "version": "1.0.0"}
generator = GenericCodeGenerator(data, template_config_filepath="templates.yaml")

# Render inline template to string
result = generator.render_template_to_string(
    "# {{ dd.project_name }} v{{ dd.version }}"
)
# Returns: "# MyAPI v1.0.0"

# Render template file to string
email = generator.render_template_file_to_string("templates/email/welcome.j2")
```

**Use cases**:
- Email generation (render to string for email APIs)
- API responses (generate JSON/HTML dynamically)
- Configuration preview (validate before writing)
- Testing (test templates without file I/O)

Both methods reuse all generator context (helpers, extra_data, globals, flattening, Jinja2 options).

## Next Steps

- [API Reference](api-reference.md) - Complete Python API documentation
- [YAGEN Guide](yagen-guide.md) - Advanced YAML-based generation
- [Data Helpers](data-helpers.md) - Add computed properties to your data
- [Template Guide](template-guide.md) - Master Jinja2 templates
- [Examples](../examples/README.md) - See complete working examples

## Common Use Cases

### 1. Generate Service Files from Data

Perfect for microservices architecture where you need to generate boilerplate for each service.

### 2. Create API Handlers from OpenAPI Specs

Parse OpenAPI specifications and generate handler stubs with proper structure.

### 3. Generate Tests from Test Data

Create test files based on test case data, maintaining consistent structure.

### 4. Documentation Generation

Generate documentation files from structured data with computed metrics.

### 5. Configuration Files

Create environment-specific configuration files from a single data source.

## Getting Help

- Check the [API Reference](api-reference.md) for detailed documentation
- Browse [examples](../examples/README.md) for working code
- Report issues at: https://github.com/robinbreast/pytemplify/issues
