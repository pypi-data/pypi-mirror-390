# Advanced Example - Nested Iterations and Conditional Patterns

This example demonstrates advanced YAML-based template generation with nested iterations, conditional patterns, and array iterations.

## Features Demonstrated

- **Nested iteration** using `>>` operator: `module in dd.modules >> component in module.components`
- **Conditional iteration** using `if`: `endpoint in dd.endpoints if endpoint.public`
- **Array iteration**: Multiple patterns in a list to generate from different data sources
- **Complex template organization** with multiple `_foreach_` contexts
- **Manual sections** for preserving user code between regenerations

## Project Structure

```
advanced/
├── config.yaml              # Advanced YAML configuration
├── data.json                # Complex nested data structure
├── templates/
│   ├── _foreach_module___init__.py.j2        # Module initialization
│   ├── _foreach_component_component.py.j2    # Component files (nested)
│   ├── _foreach_endpoint_api.py.j2           # API endpoints (conditional)
│   ├── _foreach_module_module_doc.md.j2      # Module docs (array iteration)
│   ├── _foreach_endpoint_endpoint_doc.md.j2  # Endpoint docs (array iteration)
│   └── PROJECT_OVERVIEW.md.j2                # Static overview
└── output/                  # Generated files
```

## Running the Example

From the `examples/advanced` directory:

```bash
# Generate all files
uv run yagen --config config.yaml --data data.json

# Generate only specific template sets
uv run yagen -c config.yaml -d data.json --include "Module*"

# Exclude documentation generation
uv run yagen -c config.yaml -d data.json --exclude "Documentation"

# Verbose output
uv run yagen -c config.yaml -d data.json -v
```

## Expected Output

```
output/
├── modules/
│   ├── authentication/
│   │   ├── __init__.py
│   │   ├── login.py
│   │   ├── session.py
│   │   └── password.py
│   ├── users/
│   │   ├── __init__.py
│   │   ├── profile.py
│   │   └── roles.py
│   └── internal/
│       ├── __init__.py
│       └── cache.py
├── api/
│   ├── api_v1_login_api.py
│   ├── api_v1_logout_api.py
│   └── api_v1_users_api.py
├── docs/
│   ├── authentication_module_doc.md
│   ├── users_module_doc.md
│   ├── api_v1_login_endpoint_doc.md
│   ├── api_v1_logout_endpoint_doc.md
│   └── api_v1_users_endpoint_doc.md
└── PROJECT_OVERVIEW.md
```

## Key Concepts

### 1. Nested Iteration (`>>` operator)

```yaml
iterate: "module in dd.modules >> component in module.components"
```

This creates a nested loop:

- Outer loop: Iterates over `modules`
- Inner loop: For each module, iterates over its `components`
- Both `module` and `component` are available in templates

### 2. Conditional Iteration (`if` clause)

```yaml
iterate: "endpoint in dd.endpoints if endpoint.public"
```

Only processes endpoints where `public` is `true`.

### 3. Array Iteration

```yaml
iterate:
  - "module in dd.modules if module.documented"
  - "endpoint in dd.endpoints if endpoint.public"
```

Processes templates multiple times:

- First with documented modules
- Then with public endpoints

### 4. Template Context with `_foreach_`

- `_foreach_module_` - Available when iterating over `module`
- `_foreach_component_` - Available when iterating over `component` (nested context)
- `_foreach_endpoint_` - Available when iterating over `endpoint`

### 5. Manual Sections

```python
# MANUAL SECTION START: endpoint_implementation
# Your custom code here - preserved between regenerations
# MANUAL SECTION END
```

User code within manual sections is preserved when templates are regenerated.

## Template Filtering Examples

### Include Only API Files

```bash
uv run yagen -c config.yaml -d data.json --include "Public APIs*"
```

### Exclude Documentation

```bash
uv run yagen -c config.yaml -d data.json --exclude "Documentation"
```

### Multiple Patterns

```bash
uv run yagen -c config.yaml -d data.json \
  --include "Module*" --include "Component*" \
  --exclude "*Documentation*"
```

### Using Regex

```bash
uv run yagen -c config.yaml -d data.json \
  --include "regex:^(Module|Component).*"
```

## Data Structure

The `data.json` file contains:

- **modules**: Array of modules, each with nested components
- **endpoints**: Array of API endpoints with conditional flags
- Each module has: name, description, documented flag, components array
- Each component has: name, type, methods array
- Each endpoint has: path, method, public flag, module, description

## Advanced Jinja2 Features Used

- **Filters**: `title`, `replace`, `lower`, `selectattr`, `sum`
- **Tests**: `equalto`
- **Functions**: `length`, `list`
- **Complex expressions**: `modules | selectattr('documented', 'equalto', true) | list | length`

## Next Steps

- Modify `data.json` to add more modules or components
- Create custom template filters
- Use data helpers for computed properties (see with_helpers example)
- Experiment with regex patterns for filtering
