# Template Filtering Example

This example demonstrates how to use **template filtering** to selectively generate subsets of files using include/exclude patterns.

## Features Demonstrated

- **Include Patterns**: Generate only matching template sets
- **Exclude Patterns**: Skip specific template sets
- **Glob Patterns**: Use wildcards like `*Test*`, `Core*`
- **Regex Patterns**: Use complex patterns like `regex:^(Core|API).*`
- **Multiple Patterns**: Combine multiple include/exclude filters
- **Conditional Iteration**: Filter data at the iteration level

## Project Structure

```
filtered/
├── config.yaml              # Multiple template sets for filtering
├── data.json                # Services with categories
├── templates/
│   ├── _foreach_service_{{ service.name }}_core_service.py.j2
│   ├── _foreach_service_{{ service.name }}_api_handler.py.j2
│   ├── _foreach_service_{{ service.name }}_debug.py.j2
│   ├── _foreach_service_{{ service.name }}_unit_test.py.j2
│   ├── _foreach_service_{{ service.name }}_integration_test.py.j2
│   ├── _foreach_service_{{ service.name }}_doc.md.j2
│   └── overview.md.j2
└── output/                  # Generated files
```

## Template Sets

The config defines 7 template sets:

1. **Core Infrastructure** - Core services only
2. **API Services** - API services only
3. **Debug Utilities** - Debug tools for all services
4. **Unit Tests** - Unit test files
5. **Integration Tests** - Integration test files
6. **Documentation** - Service documentation
7. **Static Config** - Static overview file

## Running with Filters

### Basic Usage

```bash
# Generate all files (no filtering)
uv run yagen -c config.yaml -d data.json

# With explicit output directory
uv run yagen -c config.yaml -d data.json -o output
```

### Include Patterns

```bash
# Generate only core infrastructure
uv run yagen -c config.yaml -d data.json --include "Core Infrastructure"

# Generate only API services
uv run yagen -c config.yaml -d data.json --include "API Services"

# Generate multiple sets
uv run yagen -c config.yaml -d data.json \
  --include "Core Infrastructure" \
  --include "API Services"

# Use glob patterns
uv run yagen -c config.yaml -d data.json --include "Core*"

# Generate only tests
uv run yagen -c config.yaml -d data.json --include "*Test*"
```

### Exclude Patterns

```bash
# Exclude debug utilities
uv run yagen -c config.yaml -d data.json --exclude "Debug*"

# Exclude all tests
uv run yagen -c config.yaml -d data.json --exclude "*Test*"

# Exclude multiple sets
uv run yagen -c config.yaml -d data.json \
  --exclude "Debug*" \
  --exclude "*Test*"

# Generate everything except documentation
uv run yagen -c config.yaml -d data.json --exclude "Documentation"
```

### Combined Patterns

```bash
# Include services, exclude tests
uv run yagen -c config.yaml -d data.json \
  --include "Core*" --include "API*" \
  --exclude "*Test*"

# Development build (no tests, no debug)
uv run yagen -c config.yaml -d data.json \
  --exclude "*Test*" --exclude "Debug*"

# Test-only build
uv run yagen -c config.yaml -d data.json \
  --include "*Test*"
```

### Regex Patterns

```bash
# Include Core or API services using regex
uv run yagen -c config.yaml -d data.json \
  --include "regex:^(Core|API).*"

# Exclude anything with "Test" or "Debug"
uv run yagen -c config.yaml -d data.json \
  --exclude "regex:.*(Test|Debug).*"

# Complex pattern
uv run yagen -c config.yaml -d data.json \
  --include "regex:^(Core|API) .*" \
  --exclude "regex:.*Debug.*"
```

## Expected Outputs

### All Files (No Filter)

```
output/
├── core/
│   ├── database_core_service.py
│   └── cache_core_service.py
├── api/
│   ├── auth-api_api_handler.py
│   ├── user-api_api_handler.py
│   └── payment-api_api_handler.py
├── debug/
│   ├── database_debug.py
│   ├── cache_debug.py
│   ├── auth-api_debug.py
│   ├── user-api_debug.py
│   └── payment-api_debug.py
├── tests/
│   ├── unit/
│   │   ├── database_unit_test.py
│   │   ├── cache_unit_test.py
│   │   ├── auth-api_unit_test.py
│   │   ├── user-api_unit_test.py
│   │   └── payment-api_unit_test.py
│   └── integration/
│       ├── database_integration_test.py
│       ├── cache_integration_test.py
│       ├── auth-api_integration_test.py
│       ├── user-api_integration_test.py
│       └── payment-api_integration_test.py
├── docs/
│   ├── database_doc.md
│   ├── cache_doc.md
│   ├── auth-api_doc.md
│   ├── user-api_doc.md
│   └── payment-api_doc.md
└── overview.md
```

### Core Only (`--include "Core*"`)

```
output/
├── core/
│   ├── database_core_service.py
│   └── cache_core_service.py
└── overview.md  (if Static Config is matched)
```

### No Tests (`--exclude "*Test*"`)

```
output/
├── core/
├── api/
├── debug/
├── docs/
└── overview.md
```

## Pattern Matching Rules

### Glob Patterns (Default)

- `Core*` - Matches "Core Infrastructure"
- `*Test*` - Matches "Unit Tests", "Integration Tests"
- `API*` - Matches "API Services"
- `*Debug*` - Matches "Debug Utilities"

### Regex Patterns

Prefix with `regex:`:

- `regex:^Core.*` - Starts with "Core"
- `regex:.*Test.*` - Contains "Test"
- `regex:^(Core|API).*` - Starts with "Core" or "API"

### Exact Matching

- `"Core Infrastructure"` - Exact match only

## Use Cases

### Development Workflow

```bash
# Quick development - only core services
uv run yagen -c config.yaml -d data.json --include "Core*" --include "API*"

# Testing focus - only tests
uv run yagen -c config.yaml -d data.json --include "*Test*"

# Documentation only
uv run yagen -c config.yaml -d data.json --include "Documentation"
```

### CI/CD Pipeline

```bash
# Production build - no debug, no tests
uv run yagen -c config.yaml -d data.json \
  --exclude "*Test*" --exclude "Debug*"

# Test suite generation
uv run yagen -c config.yaml -d data.json \
  --include "*Test*" --include "Debug*"
```

### Incremental Generation

```bash
# Regenerate only unit tests
uv run yagen -c config.yaml -d data.json --include "Unit Tests"

# Update API services only
uv run yagen -c config.yaml -d data.json --include "API Services"
```

## Key Concepts

### 1. Template Set Names

Each template set has a `name` field used for filtering:

```yaml
templates:
  - name: "Core Infrastructure"  # This is the filter key
    folder: "templates"
    output: "output/core"
```

### 2. Template File Filtering

Each template set can specify `files` to filter which template files are processed:

```yaml
templates:
  - name: "Core Infrastructure"
    folder: "templates"
    output: "output/core"
    iterate: "service in dd.services if service.category == 'core'"
    files:
      include: ["*core_service*"]  # Only process templates matching this pattern
    enabled: true
```

This ensures that each template set only processes the relevant template files, preventing all templates from being generated in every output directory.

### 3. Pattern Matching

Patterns match against template set names (for `--include`/`--exclude` CLI flags) or template filenames (for `files.include`/`files.exclude` in config):
- Case-sensitive
- Glob patterns use `*` and `?`
- Regex patterns use `regex:` prefix

### 4. Include vs Exclude

- **Include**: Only matching sets are processed (whitelist)
- **Exclude**: Matching sets are skipped (blacklist)
- **Both**: Include first, then exclude from included sets

### 5. Multiple Patterns

When using multiple patterns:
- Multiple `--include`: Matches ANY pattern (OR logic)
- Multiple `--exclude`: Excludes ALL patterns (OR logic)

## Advanced Tips

### Verbose Output

See which templates are being filtered:

```bash
uv run yagen -c config.yaml -d data.json \
  --include "Core*" --verbose
```

### Testing Patterns

Use verbose mode to verify your patterns match correctly before generating files.

### Convention

Adopt a naming convention for template sets:
- Category prefix: `Core`, `API`, `Test`, `Debug`, `Doc`
- Type suffix: `Services`, `Utilities`, `Tests`, `Files`
- Example: `Core Infrastructure`, `Unit Tests`, `API Services`

## Next Steps

- Experiment with different filter combinations
- Create custom naming conventions for your project
- Use filtering in CI/CD pipelines for selective generation
- Combine with conditional iteration in YAML config
