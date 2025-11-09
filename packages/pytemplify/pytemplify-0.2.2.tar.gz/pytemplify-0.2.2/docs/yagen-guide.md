# YAGEN Guide

The YAML-based generator (`yagen`) is the **recommended approach** for most PyTemplify use cases. It provides a declarative, powerful way to generate code from data without writing custom Python code.

## Why Choose YAGEN?

- **No Code Required**: Define everything in YAML config + Jinja2 templates
- **Data Helpers**: Extend your data with computed properties
- **Advanced Iteration**: Filter, nest, and iterate with expressive syntax
- **Flexible Output**: Multiple template sets, conditional generation
- **Production Ready**: Schema validation, error handling, CLI interface

## Quick Start

### 1. Create Data File

`data.json`:
```json
{
  "services": [
    {"name": "user-service", "port": 8080, "enabled": true},
    {"name": "auth-service", "port": 8081, "enabled": true},
    {"name": "debug-service", "port": 9000, "enabled": false}
  ]
}
```

### 2. Create Configuration

`config.yaml`:
```yaml
globals:
  version: "1.0.0"
  project: "MyProject"

templates:
  - name: "Service Files"
    folder: "templates"
    output: "services"
    iterate: "service in services if service.enabled"
    enabled: true
```

### 3. Create Templates

`templates/_foreach_service_{{ service.name }}_service.py.j2`:
```jinja2
"""{{ service.name | title }} Service"""

SERVICE_NAME = "{{ service.name }}"
SERVICE_PORT = {{ service.port }}
VERSION = "{{ gg.version }}"

# MANUAL SECTION START: custom_config
# Add your custom configuration here
# MANUAL SECTION END

def start():
    print(f"Starting {SERVICE_NAME} on port {SERVICE_PORT}")
```

### 4. Generate

```bash
yagen --config config.yaml --data data.json
```

**Result**: Two service files (user-service and auth-service) generated. Debug-service skipped because `enabled: false`.

## Configuration Reference

### Complete Configuration Example

```yaml
# Global variables (accessible via gg.* in templates)
globals:
  version: "1.0.0"
  project: "MyProject"
  author: "Your Name"

# Control data flattening (default: true)
flatten_data: true

# Load additional data from external files or inline
extra_data:
  # From external file
  - path: "infrastructure.json"
    key: "infra"
    required: false  # Don't fail if file missing

  # Inline data
  - value:
      database:
        host: "localhost"
        port: 5432
    key: "config"

# Data helpers configuration
data_helpers:
  helpers:
    - "my_helpers.CompanyHelpers"
    - "my_helpers.EmployeeHelpers"
  discovery_paths:
    - "./helpers/"
    - "../shared/helpers/"

# Code formatting configuration
format:
  enabled: true
  defaults:
    preserve_manual_sections: true
    ignore_patterns: ["*.min.*", "*.generated.*"]
  formatters:
    ".py":
      type: "black"
      options:
        line_length: 88

# Template sets
templates:
  - name: "Core Services"
    folder: "service_templates"
    output: "src/services"
    iterate: "service in services"
    enabled: true

  - name: "API Endpoints"
    folder: "api_templates"
    output: "src/api"
    iterate: "endpoint in endpoints if endpoint.public"
    enabled: true

  - name: "Static Files"
    folder: "static_templates"
    output: "config"
    enabled: true
```

## Iteration Patterns

### Simple Iteration

Iterate over a list in your data:

```yaml
iterate: "service in services"
```

Template access:
```jinja2
{{ service.name }}
{{ service.port }}
```

### Conditional Iteration

Filter items during iteration:

```yaml
iterate: "endpoint in endpoints if endpoint.enabled"
```

```yaml
iterate: "service in services if service.port > 8080"
```

### Nested Iteration

Use `>>` operator for nested structures:

```yaml
iterate: "module in modules >> component in module.components"
```

Template access:
```jinja2
Module: {{ module.name }}
Component: {{ component.name }}
{{ component.description }}
```

Real-world example:
```yaml
iterate: "department in departments >> employee in department.employees"
```

### Array Iteration

Multiple iteration patterns in a single template set:

```yaml
iterate:
  - "service in services if service.public"
  - "module in modules if module.documented"
```

Templates will be processed once for each pattern.

### Access Patterns in Iteration

When using namespaced data access (`dd.`):
```yaml
iterate: "service in dd.services"
iterate: "endpoint in dd.endpoints if endpoint.enabled"
iterate: "module in dd.modules >> component in module.components"
```

When using flattened data access (default):
```yaml
iterate: "service in services"
iterate: "endpoint in endpoints if endpoint.enabled"
iterate: "module in modules >> component in module.components"
```

## Template Organization

### File Naming Convention

Use `_foreach_` prefix to control template processing:

```
templates/
├── _foreach_service_{{ service.name }}_main.py.j2
├── _foreach_service_{{ service.name }}_test.py.j2
├── _foreach_module_{{ module.name }}_init.py.j2
└── static_config.yaml.j2
```

**Rules:**
- `_foreach_service_*` - Only processed when iterating over variable named `service`
- `_foreach_module_*` - Only processed when iterating over variable named `module`
- No `_foreach_` prefix - Always processed

### Dynamic Filenames

Use Jinja2 expressions in filenames:

```
_foreach_service_{{ service.name }}_service.py.j2
→ generates: user_service_service.py, auth_service_service.py

_foreach_module_{{ module.path | replace('.', '/') }}/init.py.j2
→ generates: com/example/utils/init.py
```

## Data Access in Templates

### Flattened Access (Default)

When `flatten_data: true` (default):

```jinja2
Project: {{ project_name }}
Version: {{ gg.version }}

{% for service in services %}
  - {{ service.name }}: {{ service.port }}
{% endfor %}
```

### Namespaced Access

When `flatten_data: false` or explicit namespacing:

```jinja2
Project: {{ dd.project_name }}
Version: {{ gg.version }}

{% for service in dd.services %}
  - {{ service.name }}: {{ service.port }}
{% endfor %}
```

### Reserved Keys

These keys are reserved and cannot be flattened:
- `dd` - Data dictionary
- `dd_raw` - Raw unwrapped data
- `helpers` - Helper information
- `globals` - Global variables
- `gg` - Global variables alias

Access them via `dd.` namespace if they exist in your data.

## Template Filtering

### Command-Line Filtering

Filter which template sets to process:

```bash
# Include only matching templates
yagen -c config.yaml -d data.json --include "Core*"

# Exclude matching templates
yagen -c config.yaml -d data.json --exclude "*Test*"

# Combine multiple patterns
yagen -c config.yaml -d data.json \
  --include "Core*" --include "API*" \
  --exclude "Debug*"

# Use regex
yagen -c config.yaml -d data.json --include "regex:^(Core|API).*"
```

### Filter Patterns

**Glob patterns** (default):
- `"Service*"` - Matches "Service Files", "Service Tests"
- `"*Test*"` - Matches anything with "Test"
- `"Core*"` - Matches "Core Services", "Core Utils"

**Regex patterns**:
- `"regex:^Core.*"` - Starts with "Core"
- `"regex:.*Test$"` - Ends with "Test"
- `"regex:^(Core|API).*"` - Starts with "Core" or "API"

## Data Helpers Integration

### Configuration

Add data helpers in YAML:

```yaml
data_helpers:
  helpers:
    - "my_helpers.CompanyHelpers"
    - "my_helpers.EmployeeHelpers"
  discovery_paths:
    - "./helpers/"
```

Or via CLI:

```bash
yagen -c config.yaml -d data.json \
  --helpers "my_helpers.CompanyHelpers" \
  --helper-path "./helpers/"
```

### Using Helpers in Templates

```jinja2
Company: {{ dd.company_name }}
Total Employees: {{ dd.total_employees }}  {# Computed by helper #}
Total Salary: ${{ dd.total_salary }}        {# Computed by helper #}

{% for dept in dd.departments %}
Department: {{ dept.name }}
  Average Salary: ${{ dept.average_salary }}  {# Computed by helper #}
  {% for emp in dept.employees %}
    - {{ emp.name }}: {{ emp.years_of_service }} years  {# Computed #}
  {% endfor %}
{% endfor %}
```

See [Data Helpers Guide](data-helpers.md) for complete documentation.

## Extra Data Loading

### From External Files

```yaml
extra_data:
  - path: "infrastructure.json"
    key: "infra"
    required: true  # Fail if missing

  - path: "secrets.json"
    key: "secrets"
    required: false  # Optional file
```

Access in templates:
```jinja2
Database: {{ infra.database.host }}:{{ infra.database.port }}
API Key: {{ secrets.api_key }}
```

### Inline Data

```yaml
extra_data:
  - value:
      database:
        host: "localhost"
        port: 5432
      redis:
        host: "localhost"
        port: 6379
    key: "config"
```

Access in templates:
```jinja2
DB Host: {{ config.database.host }}
Redis Port: {{ config.redis.port }}
```

## Code Formatting

### Configuration

```yaml
format:
  enabled: true

  defaults:
    preserve_manual_sections: true
    ignore_patterns: ["*.min.*", "*.generated.*"]

  formatters:
    # Python files
    ".py":
      type: "black"
      enabled: true
      options:
        line_length: 88
        string_normalization: true

    # JavaScript/TypeScript
    ".js|.ts|.jsx|.tsx":
      type: "prettier"
      options:
        printWidth: 80
        semi: true

    # C/C++
    ".c|.cpp|.h":
      type: "command"
      command: "clang-format ${input} > ${output}"
      options:
        timeout: 30
```

### Supported Formatters

- **black**: Python formatter
- **prettier**: JavaScript, TypeScript, JSON, CSS, etc.
- **command**: Custom command-line formatter

### Manual Section Preservation

Formatters automatically preserve manual sections when enabled:

```yaml
defaults:
  preserve_manual_sections: true
```

See [Formatting Guide](formatting.md) for details.

## Command-Line Reference

```bash
yagen [OPTIONS]

Required:
  -c, --config PATH      YAML configuration file
  -d, --data PATH        JSON data file

Optional:
  -o, --output PATH      Output directory (overrides config)
  -v, --verbose          Verbose output
  --include PATTERN      Include template sets matching pattern (repeatable)
  --exclude PATTERN      Exclude template sets matching pattern (repeatable)
  --helpers SPEC         Helper module specification (repeatable)
  --helper-path PATH     Path to search for helper modules (repeatable)
  --no-flatten           Disable data flattening (requires dd. prefix)
  --help                 Show help message
```

### Examples

**Basic generation:**
```bash
yagen -c config.yaml -d data.json
```

**With output override:**
```bash
yagen -c config.yaml -d data.json -o ./custom_output
```

**With filtering:**
```bash
yagen -c config.yaml -d data.json \
  --include "Core*" \
  --exclude "*Test*"
```

**With helpers:**
```bash
yagen -c config.yaml -d data.json \
  --helpers "my_helpers.CompanyHelpers" \
  --helper-path "./helpers/"
```

**Verbose output:**
```bash
yagen -c config.yaml -d data.json -v
```

**Disable data flattening:**
```bash
yagen -c config.yaml -d data.json --no-flatten
```

## Advanced Patterns

### Conditional Template Sets

```yaml
templates:
  - name: "Production Services"
    folder: "prod_templates"
    output: "dist"
    iterate: "service in services if not service.debug"
    enabled: true

  - name: "Debug Services"
    folder: "debug_templates"
    output: "debug"
    iterate: "service in services if service.debug"
    enabled: false  # Disable by default
```

### Multiple Output Directories

```yaml
templates:
  - name: "Backend"
    folder: "backend_templates"
    output: "src/backend"
    iterate: "service in services"

  - name: "Frontend"
    folder: "frontend_templates"
    output: "src/frontend"
    iterate: "component in components"
```

### Cross-Module Dependencies

```yaml
templates:
  - name: "Models"
    folder: "model_templates"
    output: "src/models"
    iterate: "model in models"

  - name: "API"
    folder: "api_templates"
    output: "src/api"
    iterate: "model in models"  # Same iteration, different templates
```

## Best Practices

1. **Use descriptive template set names** for clear filtering
2. **Organize templates** with `_foreach_` prefix for clarity
3. **Keep configuration DRY** with globals and extra_data
4. **Use data helpers** instead of pre-processing data
5. **Enable formatting** for consistent code style
6. **Preserve manual sections** for safe regeneration
7. **Use conditional iteration** to filter at generation time
8. **Test with small datasets** before full generation
9. **Version control** your config and templates
10. **Document your iteration patterns** for team members

## Troubleshooting

### Template Not Found

**Problem:** Templates not being processed

**Solutions:**
- Check `folder` path in config.yaml
- Verify template files have `.j2` extension
- Check `_foreach_` prefix matches iteration variable

### Data Not Accessible

**Problem:** Variables undefined in templates

**Solutions:**
- Check `flatten_data` setting
- Use `dd.` prefix if flattening disabled
- Verify data structure in JSON file
- Use `-v` flag for verbose output

### Iteration Not Working

**Problem:** Templates processed incorrectly

**Solutions:**
- Check iteration syntax: `"var in data"`
- Verify data structure matches iteration pattern
- Use correct variable name in `_foreach_` prefix
- Check conditional expressions

### Helpers Not Loading

**Problem:** Helper properties not available

**Solutions:**
- Verify `discovery_paths` in config
- Check helper class inherits `DataHelper`
- Ensure `matches()` method implemented correctly
- Use `--helper-path` CLI option

### Output Files Empty

**Problem:** Generated files are empty or incomplete

**Solutions:**
- Check template syntax
- Verify data is correctly structured
- Review conditional logic in templates
- Enable verbose mode with `-v`

## See Also

- [Getting Started](getting-started.md) - Quick start guide
- [API Reference](api-reference.md) - Python API documentation
- [Data Helpers Guide](data-helpers.md) - Complete helper documentation
- [Template Guide](template-guide.md) - Template best practices
- [Examples](../examples/README.md) - Working examples
