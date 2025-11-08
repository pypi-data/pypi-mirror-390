# Template Writing Guide

Learn how to write effective Jinja2 templates for PyTemplify.

## Template Basics

PyTemplify uses Jinja2 as its template engine. Templates combine static text with dynamic expressions and control structures.

### Basic Syntax

```jinja2
{# This is a comment #}

{{ variable }}                    {# Output variable #}
{{ expression | filter }}         {# Apply filter #}
{% if condition %}...{% endif %}  {# Conditional #}
{% for item in list %}...{% endfor %}  {# Loop #}
```

## Data Access

### Flattened Access (Default)

When data flattening is enabled (default), top-level data keys are directly accessible:

```jinja2
Project: {{ project_name }}
Version: {{ version }}

{% for service in services %}
  Service: {{ service.name }}
  Port: {{ service.port }}
{% endfor %}
```

### Namespaced Access

Use explicit namespaces for clarity:

```jinja2
{# Data from JSON file #}
Project: {{ dd.project_name }}

{# Global variables from YAML #}
Version: {{ gg.version }}

{# Iteration variable #}
{% for service in dd.services %}
  Service: {{ service.name }}
{% endfor %}
```

### Reserved Keys

These are reserved and must use `dd.` prefix if they exist in your data:
- `dd`, `dd_raw` - Data dictionary
- `helpers` - Helper information
- `globals`, `gg` - Global variables

```jinja2
{# If your data has a "globals" key #}
{{ dd.globals }}  {# Your data #}
{{ gg.version }}  {# YAML global #}
```

## Template File Naming

### Static Templates

Regular templates are always processed:

```
config.yaml.j2          → config.yaml
README.md.j2            → README.md
setup.py.j2             → setup.py
```

### Dynamic Templates

Use Jinja2 expressions in filenames:

```
{{ service.name }}_service.py.j2
→ user_service.py, auth_service.py

api/{{ endpoint.path }}/handler.py.j2
→ api/users/handler.py, api/orders/handler.py
```

### Filtered Templates

Use `_foreach_` prefix to process only during specific iterations:

```
_foreach_service_{{ service.name }}_main.py.j2
→ Only processed when iterating over "service"

_foreach_module_{{ module.name }}/init.py.j2
→ Only processed when iterating over "module"
```

**Example:**
```yaml
# config.yaml
templates:
  - name: "Services"
    iterate: "service in services"  # "service" is the variable
    folder: "templates"
```

Only templates matching `_foreach_service_*` will be processed.

## Manual Sections

Preserve user-edited content between regenerations:

### Basic Usage

```jinja2
class {{ class_name }}:
    def __init__(self):
        self.name = "{{ class_name }}"

    # MANUAL SECTION START: custom_methods
    # Add your custom methods here
    # MANUAL SECTION END
```

### With Default Content

```jinja2
# MANUAL SECTION START: imports
import os
import sys
# MANUAL SECTION END
```

On first generation, the default content appears. On regeneration, user edits are preserved.

### Multiple Sections

```jinja2
class {{ class_name }}:
    # MANUAL SECTION START: class_attributes
    # Add class attributes here
    # MANUAL SECTION END

    def __init__(self):
        # MANUAL SECTION START: init_code
        # Add initialization code here
        # MANUAL SECTION END
        pass

    # MANUAL SECTION START: methods
    # Add custom methods here
    # MANUAL SECTION END
```

### Best Practices

1. **Use descriptive section names**: `custom_methods` not `section1`
2. **Place strategically**: Where users are likely to add code
3. **Include defaults**: Show users what's expected
4. **Document purpose**: Add comments explaining the section

## Control Structures

### Conditionals

```jinja2
{% if service.enabled %}
Service {{ service.name }} is enabled
{% endif %}

{% if service.port > 8080 %}
High port: {{ service.port }}
{% elif service.port > 8000 %}
Medium port: {{ service.port }}
{% else %}
Low port: {{ service.port }}
{% endif %}
```

### Loops

```jinja2
{# Simple loop #}
{% for service in services %}
  - {{ service.name }}
{% endfor %}

{# With index #}
{% for service in services %}
  {{ loop.index }}. {{ service.name }}
{% endfor %}

{# With conditionals #}
{% for service in services if service.enabled %}
  - {{ service.name }}
{% endfor %}

{# Nested loops #}
{% for module in modules %}
  Module: {{ module.name }}
  {% for component in module.components %}
    - Component: {{ component.name }}
  {% endfor %}
{% endfor %}
```

### Loop Variables

```jinja2
{% for item in items %}
  Index: {{ loop.index }}      {# 1-indexed #}
  Index0: {{ loop.index0 }}    {# 0-indexed #}
  First: {{ loop.first }}      {# True if first item #}
  Last: {{ loop.last }}        {# True if last item #}
  Length: {{ loop.length }}    {# Total items #}
{% endfor %}
```

## Filters

PyTemplify includes 70+ built-in filters for template processing. Here are some commonly used examples:

### String Filters

```jinja2
{# Case conversion #}
{{ "hello world" | upper }}           {# HELLO WORLD #}
{{ "CamelCase" | snakecase }}         {# camel_case #}
{{ "snake_case" | camelcase }}        {# snakeCase #}
{{ "snake_case" | pascalcase }}       {# SnakeCase #}
{{ "snake_case" | kebabcase }}        {# snake-case #}

{# String manipulation #}
{{ "Hello World!" | slugify }}        {# hello-world #}
{{ "/api/v1/users" | normalize }}     {# api_v1_users #}
{{ "test.txt" | remove_suffix(".txt") }}  {# test #}
```

### Collection Filters

```jinja2
{# List operations #}
{{ items | unique }}                  {# Remove duplicates #}
{{ items | flatten }}                 {# Flatten nested lists #}
{{ items | chunk(3) }}                {# Split into chunks #}
{{ items | compact }}                 {# Remove falsy values #}

{# List querying #}
{{ users | pluck("name") }}           {# Extract names #}
{{ users | where("active", true) }}   {# Filter by condition #}
{{ users | sort_by("age") }}          {# Sort by attribute #}
{{ users | group_by("role") }}        {# Group by attribute #}
```

### Formatting Filters

```jinja2
{# Numbers and currency #}
{{ 1234567.89 | format_number }}             {# 1,234,567.89 #}
{{ 1024 | format_bytes }}                    {# 1.00 KB #}
{{ 0.1234 | format_percentage }}             {# 12.34% #}
{{ 1234.56 | format_currency }}              {# $1,234.56 #}

{# Dates and formatting #}
{{ timestamp | format_date("%Y-%m-%d") }}    {# 2024-10-16 #}
{{ 22 | format_ordinal }}                    {# 22nd #}
{{ data | format_json(2) }}                  {# Pretty JSON #}
```

### Utility Filters

```jinja2
{# Type checking and defaults #}
{{ value | default_if_none("N/A") }}         {# Default for None #}
{{ value | ternary(true_val, false_val) }}   {# Ternary operator #}
{{ value | is_string }}                      {# Type checking #}

{# Hashing and encoding #}
{{ "hello" | hash_md5 }}                     {# MD5 hash #}
{{ "hello" | b64encode }}                    {# Base64 encode #}
{{ uuid_generate("service_name") }}          {# Deterministic UUID #}

{# File paths #}
{{ "/path/to/file.txt" | file_extension }}   {# txt #}
{{ "/path/to/file.txt" | file_basename }}    {# file.txt #}
```

### Filter Chaining

```jinja2
{{ service.name | snakecase | upper }}
→ "UserService" → "user_service" → "USER_SERVICE"

{{ items | map(attribute='name') | unique | sort | join(', ') }}
→ Extract, deduplicate, sort, and join names
```

**See [Filters Reference](filters-reference.md) for complete documentation of all 70+ filters.**

## Whitespace Control

### Trim Blocks

Configure in Python API or via environment:

```python
renderer.set_env_options(
    trim_blocks=True,      # Remove first newline after tag
    lstrip_blocks=True     # Strip leading spaces before tag
)
```

### Manual Control

```jinja2
{# Remove whitespace before #}
{{- variable }}

{# Remove whitespace after #}
{{ variable -}}

{# Remove both #}
{{- variable -}}

{# Works with control structures #}
{%- if condition -%}
  content
{%- endif -%}
```

### Example

**Without control:**
```jinja2
{% for item in items %}
  - {{ item }}
{% endfor %}
```
Output:
```

  - Item1

  - Item2

```

**With control:**
```jinja2
{% for item in items -%}
  - {{ item }}
{% endfor %}
```
Output:
```
  - Item1
  - Item2
```

## Macros

Reusable template fragments:

```jinja2
{# Define macro #}
{% macro render_service(service) %}
class {{ service.name | pascal_case }}Service:
    def __init__(self):
        self.port = {{ service.port }}
{% endmacro %}

{# Use macro #}
{% for service in services %}
{{ render_service(service) }}
{% endfor %}
```

### With Defaults

```jinja2
{% macro render_config(name, value="default") %}
{{ name | upper }}_CONFIG = "{{ value }}"
{% endmacro %}

{{ render_config("debug") }}
→ DEBUG_CONFIG = "default"

{{ render_config("debug", "true") }}
→ DEBUG_CONFIG = "true"
```

## Includes

Split templates into reusable components:

**base.j2:**
```jinja2
# Common header
# Generated by PyTemplify
# DO NOT EDIT - regenerate instead
```

**service.py.j2:**
```jinja2
{% include 'base.j2' %}

class {{ service.name | pascal_case }}Service:
    pass
```

## Template Inheritance

### Base Template

**base.py.j2:**
```jinja2
"""Base service module"""

{% block imports %}
import os
import sys
{% endblock %}

class BaseService:
    {% block methods %}
    def start(self):
        pass
    {% endblock %}
```

### Child Template

**service.py.j2:**
```jinja2
{% extends 'base.py.j2' %}

{% block imports %}
{{ super() }}  {# Include parent's imports #}
import json
{% endblock %}

{% block methods %}
{{ super() }}  {# Include parent's methods #}

def custom_method(self):
    pass
{% endblock %}
```

## Data Helpers in Templates

Access computed properties from data helpers:

```jinja2
{# Helper properties #}
Company: {{ dd.company_name }}
Total Employees: {{ dd.total_employees }}  {# Computed #}
Total Salary: ${{ dd.total_salary }}       {# Computed #}

{# Nested helpers #}
{% for dept in dd.departments %}
  Department: {{ dept.name }}
  Average Salary: ${{ dept.average_salary }}  {# Computed #}

  {% for emp in dept.employees %}
    - {{ emp.name }}: {{ emp.years_of_service }} years  {# Computed #}
  {% endfor %}
{% endfor %}

{# Helper methods #}
NYC Employees: {{ dd.get_employees_by_city("NYC") | length }}
```

See [Data Helpers Guide](data-helpers.md) for creating helpers.

## Comments

```jinja2
{# Single line comment #}

{#
  Multi-line comment
  Can span multiple lines
#}

{# Comments are removed from output #}
```

## Escaping

### HTML Escaping

```jinja2
{{ user_input | escape }}        {# Escape HTML #}
{{ user_input | e }}             {# Short form #}

{# Auto-escape (configure in renderer) #}
renderer.set_env_options(autoescape=True)
```

### Raw Content

```jinja2
{% raw %}
  This is {{ not }} processed by Jinja2
  Useful for JavaScript templates, etc.
{% endraw %}
```

## Best Practices

### 1. Naming Conventions

```jinja2
{# Use descriptive names #}
{{ service_name }} not {{ sn }}
{{ user_id }} not {{ uid }}

{# Be consistent with case #}
{{ service.name }}  # Use data structure's case
{{ SERVICE_NAME }}  # For constants
```

### 2. Comments

```jinja2
{# Explain complex logic #}
{% if service.replicas > 3 and service.memory > 2048 %}
  {# Large deployment - use optimized settings #}
  replica_count: {{ service.replicas }}
{% endif %}
```

### 3. Organize Complex Templates

```jinja2
{# Group related sections #}
{# ===== Imports ===== #}
{% include 'imports.j2' %}

{# ===== Configuration ===== #}
{% include 'config.j2' %}

{# ===== Main Code ===== #}
class {{ class_name }}:
    pass
```

### 4. Handle Missing Data

```jinja2
{# Use default filter #}
{{ service.description | default('No description') }}

{# Check before using #}
{% if service.description %}
Description: {{ service.description }}
{% endif %}

{# Provide fallbacks #}
Port: {{ service.port | default(8080) }}
```

### 5. Keep Templates DRY

```jinja2
{# Extract common patterns to macros #}
{% macro render_property(name, value) %}
@property
def {{ name }}(self):
    return {{ value }}
{% endmacro %}

{# Use macros #}
{% for prop in properties %}
{{ render_property(prop.name, prop.value) }}
{% endfor %}
```

### 6. Format Output

```jinja2
{# Use whitespace control for clean output #}
{%- for item in items %}
  - {{ item }}
{% endfor -%}

{# Or enable trim_blocks #}
renderer.set_env_options(trim_blocks=True, lstrip_blocks=True)
```

## Common Patterns

### Generate Python Classes

```jinja2
class {{ class_name }}:
    """{{ class_description | default('Auto-generated class') }}"""

    def __init__(self, {{ params | join(', ') }}):
        {% for param in params -%}
        self.{{ param }} = {{ param }}
        {% endfor %}

    # MANUAL SECTION START: methods
    # Add custom methods here
    # MANUAL SECTION END
```

### Generate API Handlers

```jinja2
from flask import Flask, request

app = Flask(__name__)

{% for endpoint in endpoints %}
@app.route('{{ endpoint.path }}', methods={{ endpoint.methods }})
def {{ endpoint.name | snake_case }}():
    """{{ endpoint.description }}"""
    # MANUAL SECTION START: {{ endpoint.name }}_handler
    return {"message": "Not implemented"}
    # MANUAL SECTION END

{% endfor %}
```

### Generate Configuration Files

```yaml
# config.yaml.j2
version: "{{ gg.version }}"
services:
{% for service in services %}
  - name: {{ service.name }}
    port: {{ service.port }}
    replicas: {{ service.replicas | default(1) }}
    {% if service.env %}
    environment:
      {% for key, value in service.env.items() %}
      {{ key }}: {{ value }}
      {% endfor %}
    {% endif %}
{% endfor %}
```

### Generate Documentation

```markdown
# {{ dd.project_name }} Documentation

Version: {{ gg.version }}

## Services

{% for service in services %}
### {{ service.name | title }}

- **Port:** {{ service.port }}
- **Replicas:** {{ service.replicas | default(1) }}
- **Status:** {{ service.enabled | ternary('Enabled', 'Disabled') }}

{{ service.description | default('No description available') }}

{% endfor %}
```

## Testing Templates

### Test with Sample Data

```python
# test_template.py
from pytemplify.renderer import TemplateRenderer

data = {
    "services": [
        {"name": "test", "port": 8080}
    ]
}

renderer = TemplateRenderer(data)
template = """
{% for service in services %}
Service: {{ service.name }}
{% endfor %}
"""

result = renderer.render_string(template)
print(result)
```

### Validate Output

1. Check syntax is correct (Python, YAML, etc.)
2. Verify manual sections are preserved
3. Test with edge cases (empty lists, missing data)
4. Review generated files manually

## Troubleshooting

### Undefined Variable

**Error:** `jinja2.exceptions.UndefinedError: 'variable' is undefined`

**Solutions:**
- Check data structure
- Use `default` filter: `{{ variable | default('N/A') }}`
- Check flattening settings
- Use `dd.` prefix if needed

### Syntax Error

**Error:** `jinja2.exceptions.TemplateSyntaxError`

**Solutions:**
- Check template syntax
- Ensure all blocks are closed (`{% endif %}`, `{% endfor %}`)
- Check for typos in tag names

### Whitespace Issues

**Problem:** Extra blank lines in output

**Solutions:**
- Use whitespace control (`-`)
- Enable `trim_blocks` and `lstrip_blocks`
- Review template structure

### Manual Sections Not Preserved

**Problem:** Manual edits lost on regeneration

**Solutions:**
- Check marker syntax exactly: `MANUAL SECTION START: name`
- Ensure markers on separate lines
- Verify `preserve_manual_sections=True`

## See Also

- [Getting Started](getting-started.md) - Quick start guide
- [API Reference](api-reference.md) - Python API documentation
- [YAGEN Guide](yagen-guide.md) - YAML-based generation
- [Data Helpers Guide](data-helpers.md) - Computed properties
- [Examples](../examples/README.md) - Working examples
