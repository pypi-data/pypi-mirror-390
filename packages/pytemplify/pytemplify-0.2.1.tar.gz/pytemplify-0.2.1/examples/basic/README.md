# Basic Example - Simple Service Generation

This example demonstrates basic YAML-based template generation with simple iteration.

## Features Demonstrated

- Simple iteration over a list (`iterate: "service in dd.services"`)
- Using `_foreach_` prefix to filter templates by iteration context
- Global variables (`gg`) for project-wide settings
- Static template generation (no iteration)
- Conditional rendering based on data

## Project Structure

```
basic/
├── config.yaml              # YAML configuration for template generation
├── data.json                # JSON data file with service definitions
├── templates/
│   ├── _foreach_service_service.py.j2   # Template for each service
│   └── config.ini.j2                     # Static configuration template
└── output/                  # Generated files will appear here
```

## Running the Example

From the `examples/basic` directory:

```bash
# Generate files with yagen
uv run yagen --config config.yaml --data data.json

# Or with explicit output directory
uv run yagen -c config.yaml -d data.json -o output

# With verbose logging
uv run yagen -c config.yaml -d data.json -v
```

## Expected Output

After running yagen, you should see:

```
output/
├── services/
│   ├── user-service_service.py
│   ├── auth-service_service.py
│   └── api-gateway_service.py
└── config.ini
```

## Key Concepts

### 1. Template Configuration (config.yaml)

The `templates` section defines two template sets:
- **Service Files**: Uses `iterate` to generate one file per service
- **Static Config**: Generates a single configuration file

### 2. Data Access in Templates

- `dd.services` - Access data from data.json (dd = data dictionary)
- `gg.version` - Access global variables (gg = global variables)
- `service.name` - Access properties of the current iteration item

### 3. Template Filtering with `_foreach_`

The filename `_foreach_service_service.py.j2`:
- `_foreach_service_` - Only processed when iterating over `service` variable
- `service.py.j2` - Becomes `{service.name}_service.py` in output

### 4. Conditional Rendering

```jinja2
{% if service.database -%}
self.database = "{{ service.database }}"
{%- endif %}
```

Only renders database code if the service has a database defined.

## Next Steps

- Try modifying `data.json` to add more services
- Add custom properties to services and use them in templates
- Experiment with the template filtering: `--include "Service*"`
- Check out the advanced example for nested iterations
