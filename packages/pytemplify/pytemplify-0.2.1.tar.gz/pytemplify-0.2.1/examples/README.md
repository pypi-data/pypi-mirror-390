# PyTemplify Examples

This directory contains comprehensive examples demonstrating the `yagen` YAML-based template generator.

## Overview

**yagen** is a powerful template generation tool that uses:
- YAML configuration files for template sets
- JSON data files as input
- Jinja2 templates with advanced iteration patterns
- Optional data helpers for computed properties

## Quick Start

```bash
# Install pytemplify
pip install pytemplify

# Navigate to any example directory
cd basic/

# Generate files
uv run yagen --config config.yaml --data data.json
```

## Data Access in Templates

PyTemplify supports **two ways** to access data in templates:

### 1. Flattened Access (Default, Easier)

By default, top-level data keys are available directly:

```jinja2
Project: {{ project_name }}
{% for service in services %}
  - {{ service.name }}
{% endfor %}
```

### 2. Namespaced Access (Explicit)

You can also use the `dd.` namespace explicitly:

```jinja2
Project: {{ dd.project_name }}
{% for service in dd.services %}
  - {{ service.name }}
{% endfor %}
```

Both methods work simultaneously! Use whichever is clearer for your templates.

### Configuring Data Flattening

You can control flattening in two ways:

**1. Via YAML Configuration (Recommended):**

```yaml
# config.yaml
globals:
  version: "1.0.0"
  project: "MyProject"

# Disable flattening for this project
flatten_data: false

templates:
  - name: "My Templates"
    folder: "templates"
    output: "output"
```

**2. Via CLI Flag (Overrides YAML):**

```bash
# Disable flattening via command line
yagen --config config.yaml --data data.json --no-flatten
```

**Precedence:** CLI `--no-flatten` > YAML `flatten_data` > Default (`true`)

### Reserved Keys and Conflicts

When using flattened data access, certain keys are **reserved** and cannot be overridden:

- `dd` - Data dictionary namespace
- `dd_raw` - Raw unwrapped data
- `helpers` - Helper information
- `globals` - Global variables
- `gg` - Global variables alias

If your JSON data contains any of these keys, they will be **skipped during flattening** and a warning will be logged. You can still access them via the `dd.` namespace:

```json
{
  "project_name": "MyProject",
  "globals": "This conflicts with reserved key!",
  "helpers": "This also conflicts!"
}
```

```jinja2
{# These work #}
Project: {{ project_name }}

{# These DON'T work - reserved keys #}
Globals: {{ globals }}  {# This is the YAML globals, not your data! #}

{# Access conflicting keys via dd. namespace #}
My Globals: {{ dd.globals }}  {# This works! #}
My Helpers: {{ dd.helpers }}  {# This works! #}
```

**Best Practice:** Avoid naming your data keys with reserved names to prevent confusion.

## Available Examples

### 1. [Basic](./basic/) - Simple Service Generation

**Difficulty:** ⭐ Beginner

Learn the fundamentals of yagen:
- Simple iteration over lists
- Using `_foreach_` prefix for template filtering
- Global variables in templates
- Static vs. iterated template generation

```bash
cd basic/
uv run yagen -c config.yaml -d data.json
```

**What You'll Generate:**
- Service files for each service in the data
- A static configuration file
- ~4 output files total

---

### 2. [Advanced](./advanced/) - Nested Iterations & Conditional Patterns

**Difficulty:** ⭐⭐ Intermediate

Master advanced iteration patterns:
- Nested iteration with `>>` operator
- Conditional iteration with `if` clauses
- Array iteration for multiple data sources
- Complex template organization
- Manual sections for preserving user code

```bash
cd advanced/
uv run yagen -c config.yaml -d data.json
```

**What You'll Generate:**
- Module hierarchy with nested components
- API endpoint handlers
- Documentation for modules and endpoints
- ~20+ output files

**Key Features:**
- `module in dd.modules >> component in module.components` (nested)
- `endpoint in dd.endpoints if endpoint.public` (conditional)
- Array iteration for multi-source generation

---

### 3. [With Helpers](./with_helpers/) - Data Helpers Integration

**Difficulty:** ⭐⭐⭐ Advanced

Add computed properties to your data:
- Creating custom DataHelper classes
- Using `@property` and `@cached_property`
- Helper-to-helper communication
- Cross-level data queries
- YAML configuration for helpers

```bash
cd with_helpers/
uv run yagen -c config.yaml -d data.json
```

**What You'll Generate:**
- Company reports with computed metrics
- Department reports with statistics
- Employee cards with calculated properties
- ~10+ output files with rich computed data

**Key Features:**
- `dd.total_employees` - Computed from nested data
- `emp.years_of_service` - Calculated from dates
- `dept.average_salary` - Aggregated statistics

---

### 4. [With Schema Validation](./with_schema_validation/) - Configuration File Schema Validation

**Difficulty:** ⭐⭐ Intermediate

Learn to validate configuration files with JSON Schema:
- Loading YAML, TOML, and JSON configuration files
- JSON Schema validation with detailed error messages
- Cross-platform path handling (Windows & Linux)
- Clickable file URIs in error messages
- Format auto-detection and override

```bash
cd with_schema_validation/
uv run yagen -c config.yaml -d data.json
```

**What You'll Generate:**
- Deployment scripts for multiple environments
- Using data from YAML deployment config
- Using data from TOML build settings
- Using data from JSON database config
- All validated against JSON Schemas

**Key Features:**
- `extra_data` with schema validation
- Support for YAML/TOML/JSON formats
- Clickable error URIs (VSCode, PyCharm compatible)
- Environment variable expansion in paths

---

### 5. [Filtered](./filtered/) - Template Filtering

**Difficulty:** ⭐⭐ Intermediate

Control which templates to generate:
- Include/exclude patterns
- Glob patterns (`Core*`, `*Test*`)
- Regex patterns (`regex:^(Core|API).*`)
- Combining multiple filters
- Use cases for CI/CD pipelines

```bash
cd filtered/

# Generate only core services
uv run yagen -c config.yaml -d data.json --include "Core*"

# Exclude tests
uv run yagen -c config.yaml -d data.json --exclude "*Test*"

# Multiple patterns
uv run yagen -c config.yaml -d data.json \
  --include "Core*" --include "API*" \
  --exclude "Debug*"
```

**What You'll Generate:**
- Core infrastructure services
- API handlers
- Debug utilities
- Unit and integration tests
- Documentation
- ~30+ output files (or filtered subset)

---

## Helper Resources

### [helpers/](./helpers/) - Reusable Data Helpers

Contains example data helper classes:
- `company_helpers.py` - CompanyHelpers, DepartmentHelpers, EmployeeHelpers

These can be used across multiple examples.

---

## Common Commands

### Basic Generation

```bash
# Standard generation
yagen --config config.yaml --data data.json

# With output directory override
yagen -c config.yaml -d data.json -o ./output

# Verbose logging
yagen -c config.yaml -d data.json -v
```

### Template Filtering

```bash
# Include specific templates
yagen -c config.yaml -d data.json --include "Service*"

# Exclude patterns
yagen -c config.yaml -d data.json --exclude "*Test*"

# Regex patterns
yagen -c config.yaml -d data.json --include "regex:^Core.*"

# Multiple patterns
yagen -c config.yaml -d data.json \
  --include "Core*" --include "API*" \
  --exclude "*Debug*"
```

### Data Helpers

```bash
# Using helpers from CLI
yagen -c config.yaml -d data.json \
  --helpers "my_helpers.CompanyHelpers" \
  --helper-path "./helpers/"

# Multiple helper specs
yagen -c config.yaml -d data.json \
  --helpers "helpers.CompanyHelpers" \
  --helpers "helpers.EmployeeHelpers" \
  --helper-path "./custom_helpers/"
```

---

## Learning Path

### For Beginners

1. Start with [Basic](./basic/) - Learn simple iteration
2. Try [With Schema Validation](./with_schema_validation/) - Learn configuration validation
3. Try [Filtered](./filtered/) - Learn template filtering
4. Move to [Advanced](./advanced/) - Master nested iterations

### For Advanced Users

1. Study [Advanced](./advanced/) - Complex patterns
2. Learn [With Schema Validation](./with_schema_validation/) - Validate configurations
3. Explore [With Helpers](./with_helpers/) - Computed properties
4. Combine techniques in your own projects

---

## Key Concepts

### YAML Configuration

Each example has a `config.yaml` file with:

```yaml
globals:
  version: "1.0.0"
  project: "MyProject"

templates:
  - name: "Template Set Name"
    folder: "templates"
    output: "output/path"
    iterate: "item in dd.collection"  # Optional
    enabled: true
```

### Data Access in Templates

- `dd.*` - Access data from JSON file (data dictionary)
- `gg.*` - Access global variables from YAML
- Current iteration variable (e.g., `service`, `module`, `component`)

### Template File Naming

- `template.j2` - Regular template
- `_foreach_varname_template.j2` - Only processed when iterating over `varname`

### Iteration Patterns

- **Simple:** `item in dd.items`
- **Conditional:** `item in dd.items if item.enabled`
- **Nested:** `parent in dd.parents >> child in parent.children`
- **Array:** Multiple patterns in a list

---

## Project Structure

```
examples/
├── README.md                    # This file
├── basic/                       # Basic example
│   ├── README.md
│   ├── config.yaml
│   ├── data.json
│   └── templates/
├── advanced/                    # Advanced example
│   ├── README.md
│   ├── config.yaml
│   ├── data.json
│   └── templates/
├── with_helpers/                # Data helpers example
│   ├── README.md
│   ├── config.yaml
│   ├── data.json
│   └── templates/
├── with_schema_validation/      # Schema validation example
│   ├── README.md
│   ├── config.yaml
│   ├── data.json
│   ├── configs/                 # YAML/TOML/JSON configs
│   ├── schemas/                 # JSON Schema files
│   └── templates/
├── filtered/                    # Template filtering example
│   ├── README.md
│   ├── config.yaml
│   ├── data.json
│   └── templates/
└── helpers/                     # Reusable data helpers
    └── company_helpers.py
```

---

## Troubleshooting

### Command Not Found: yagen

Make sure pytemplify is installed:
```bash
pip install pytemplify
```

Or use with uv:
```bash
uv run yagen --config config.yaml --data data.json
```

### Template Not Found

Ensure your `folder` path in config.yaml points to the correct templates directory.

### Data Helper Not Loading

Check:
1. Helper class inherits from `DataHelper`
2. `matches()` method is implemented
3. Helper path is correct in config or CLI
4. Module/class name is spelled correctly

### Output Not Generated

- Check `output` directory in config.yaml
- Ensure `enabled: true` in template set
- Verify iteration pattern matches your data structure
- Use `-v` flag for verbose logging

---

## Additional Resources

- [PyTemplify README](../README.md) - Main documentation
- [DATA_HELPERS.md](../DATA_HELPERS.md) - Data helpers guide
- [yagen.py](../scripts/yagen.py) - Source code
- [generator.py](../pytemplify/generator.py) - Generator implementation

---

## Contributing Examples

Have a great example? Consider contributing:

1. Create a new directory under `examples/`
2. Include:
   - `README.md` - Explanation of the example
   - `config.yaml` - YAML configuration
   - `data.json` - Sample data
   - `templates/` - Template files
3. Update this README with your example
4. Submit a pull request

---

## Testing Your Understanding

Try these challenges:

### Challenge 1: Basic Modification
Modify the [basic](./basic/) example to add a "version" field to each service and display it in the generated files.

### Challenge 2: Nested Data
Create a new example with 3 levels of nesting (e.g., company → departments → teams → employees).

### Challenge 3: Custom Helpers
Write a data helper that computes the "oldest employee" in the [with_helpers](./with_helpers/) example.

### Challenge 4: Complex Filtering
In the [filtered](./filtered/) example, create a filter that generates only API services with ports above 8080.

---

## Quick Reference

| Feature | Syntax | Example |
|---------|--------|---------|
| Simple iteration | `var in dd.list` or `var in list` | `service in dd.services` or `service in services` |
| Conditional | `var in dd.list if condition` | `item in dd.items if item.enabled` |
| Nested | `var1 in dd.list >> var2 in var1.nested` | `mod in dd.modules >> comp in mod.components` |
| Array iteration | YAML list | `- "x in dd.a"` `- "y in dd.b"` |
| Template filtering | `_foreach_var_` prefix | `_foreach_service_file.py.j2` |
| Include filter | `--include pattern` | `--include "Core*"` |
| Exclude filter | `--exclude pattern` | `--exclude "*Test*"` |
| Regex pattern | `regex:pattern` | `--include "regex:^API.*"` |
| Data helpers | YAML `data_helpers` | See with_helpers example |
| Global vars | `gg.varname` | `{{ gg.version }}` |
| Data vars (flattened) | `varname` | `{{ project_name }}` |
| Data vars (namespaced) | `dd.varname` | `{{ dd.project_name }}` |
| Disable flattening | `--no-flatten` or YAML | Requires `dd.` prefix |
| Reserved keys | Cannot be flattened | `dd`, `dd_raw`, `helpers`, `globals`, `gg` |

---

**Happy Generating! 🚀**

For questions or issues, visit: https://github.com/anthropics/pytemplify
