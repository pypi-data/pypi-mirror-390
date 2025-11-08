# Code Formatting Guide

PyTemplify supports automatic code formatting for generated files, ensuring consistent code style across your projects.

## Overview

The formatting feature allows you to:
- Automatically format generated code using popular formatters
- Preserve manual sections during formatting
- Configure per-file-type formatting rules
- Use built-in or custom command-line formatters

## Installation

To use formatting features, install PyTemplify with formatting support. See [Getting Started](getting-started.md#installation) for complete installation instructions.

For quick reference:
```bash
pip install pytemplify[formatting]
```

## Configuration

### Basic Configuration

Add a `format` section to your YAML configuration:

```yaml
format:
  enabled: true  # Enable/disable globally

  defaults:
    preserve_manual_sections: true
    ignore_patterns: ["*.min.*", "*.generated.*"]

  formatters:
    ".py":
      type: "black"
      enabled: true
```

### Complete Configuration Example

```yaml
format:
  # Global enable/disable
  enabled: true

  # Default settings for all formatters
  defaults:
    preserve_manual_sections: true  # Keep manual sections intact
    ignore_patterns:
      - "*.min.*"              # Skip minified files
      - "*.generated.*"        # Skip generated files
      - "vendor/**"            # Skip vendor directory

  # Per-file-type formatters
  formatters:
    # Python files
    ".py":
      type: "black"
      enabled: true
      options:
        line_length: 88
        string_normalization: true
        skip_string_normalization: false

    # JavaScript/TypeScript files
    ".js|.ts|.jsx|.tsx":
      type: "prettier"
      enabled: true
      options:
        printWidth: 80
        semi: true
        singleQuote: false
        tabWidth: 2
        useTabs: false

    # JSON files
    ".json":
      type: "prettier"
      options:
        printWidth: 120
        tabWidth: 2

    # C/C++ files
    ".c|.cpp|.h|.hpp":
      type: "command"
      command: "clang-format -style=google ${input} > ${output}"
      options:
        timeout: 30

    # Go files
    ".go":
      type: "command"
      command: "gofmt ${input} > ${output}"
```

## Supported Formatters

### Black (Python)

```yaml
".py":
  type: "black"
  enabled: true
  options:
    line_length: 88                  # Max line length
    string_normalization: true       # Normalize string quotes
    skip_string_normalization: false # Don't normalize strings
    target_version: ["py39"]         # Target Python version
```

**Requirements:**
```bash
pip install black
```

### Prettier (JavaScript, TypeScript, JSON, CSS, HTML, Markdown)

```yaml
".js|.ts|.jsx|.tsx|.json|.css|.html|.md":
  type: "prettier"
  options:
    printWidth: 80           # Line width
    semi: true               # Add semicolons
    singleQuote: false       # Use single quotes
    tabWidth: 2              # Tab width
    useTabs: false           # Use spaces instead of tabs
    trailingComma: "es5"     # Trailing commas
    bracketSpacing: true     # Space in brackets
    arrowParens: "always"    # Arrow function parens
```

**Requirements:**
```bash
pip install prettier
```

### Custom Command

For any command-line formatter:

```yaml
".ext":
  type: "command"
  command: "formatter ${input} > ${output}"
  options:
    timeout: 30  # Timeout in seconds
```

**Placeholders:**
- `${input}` - Input file path
- `${output}` - Output file path

**Examples:**

```yaml
# clang-format
".c|.cpp|.h":
  type: "command"
  command: "clang-format -style=google ${input} > ${output}"

# gofmt
".go":
  type: "command"
  command: "gofmt ${input} > ${output}"

# rustfmt
".rs":
  type: "command"
  command: "rustfmt ${input} --output-file ${output}"

# custom script
".custom":
  type: "command"
  command: "python format_script.py ${input} ${output}"
```

## Manual Section Preservation

### How It Works

When `preserve_manual_sections: true`:

1. Extract manual sections before formatting
2. Format the code
3. Restore manual sections to their original locations

**Example:**

**Input (before formatting):**
```python
class MyClass:
    def method(self):
        x=1+2  # Unformatted

    # MANUAL SECTION START: custom_code
    def custom(self):y=3+4  # User's unformatted code
    # MANUAL SECTION END
```

**Output (after formatting):**
```python
class MyClass:
    def method(self):
        x = 1 + 2  # Formatted by Black

    # MANUAL SECTION START: custom_code
    def custom(self):y=3+4  # User's code preserved as-is
    # MANUAL SECTION END
```

### Configuration

```yaml
defaults:
  preserve_manual_sections: true  # Enable globally

formatters:
  ".py":
    type: "black"
    preserve_manual_sections: false  # Override for specific type
```

## File Patterns

### Ignore Patterns

Skip formatting for specific files:

```yaml
defaults:
  ignore_patterns:
    - "*.min.*"           # Minified files
    - "*.generated.*"     # Generated files
    - "vendor/**"         # Vendor directory
    - "**/node_modules/**"  # Dependencies
    - "dist/**"           # Distribution files
```

Patterns use glob syntax:
- `*` - Match any characters
- `**` - Match any directories
- `?` - Match single character
- `[abc]` - Match any of a, b, c

### File Type Matching

Match multiple file types:

```yaml
# Single type
".py":
  type: "black"

# Multiple types (OR)
".js|.ts|.jsx|.tsx":
  type: "prettier"

# Alternative: separate configurations
".js":
  type: "prettier"
".ts":
  type: "prettier"
```

## Python API

### Using TemplateRenderer with Formatting

```python
from pytemplify.renderer import TemplateRenderer
from pytemplify.formatting import FormattingManager

# Create renderer
renderer = TemplateRenderer(data)

# Create formatting manager from config
config = {
    "enabled": True,
    "defaults": {
        "preserve_manual_sections": True
    },
    "formatters": {
        ".py": {
            "type": "black",
            "options": {"line_length": 88}
        }
    }
}

formatter = FormattingManager.from_config(config)

# Generate and format
renderer.generate("templates/", "output/")

# Format specific file
formatter.format_file("output/service.py")
```

### Manual Formatting

```python
from pytemplify.formatting import FormattingManager
from pytemplify.formatting.builtin import BlackFormatter

# Create formatter
black = BlackFormatter(options={"line_length": 100})

# Format code
code = "x=1+2"
formatted = black.format_string(code)
print(formatted)  # "x = 1 + 2\n"

# Format file
black.format_file("input.py", "output.py")
```

### Custom Formatter

Create your own formatter:

```python
from pytemplify.formatting.base import BaseFormatter

class CustomFormatter(BaseFormatter):
    def format_string(self, content: str) -> str:
        """Format string content."""
        # Your formatting logic
        return content.upper()

    def format_file(self, input_path: str, output_path: str) -> None:
        """Format file."""
        with open(input_path) as f:
            content = f.read()

        formatted = self.format_string(content)

        with open(output_path, 'w') as f:
            f.write(formatted)

# Use custom formatter
formatter = CustomFormatter(options={})
result = formatter.format_string("hello")
print(result)  # "HELLO"
```

## CLI Usage

Formatting is automatically applied when using `yagen` based on your configuration. See [YAGEN Guide - Command Reference](yagen-guide.md#command-line-reference) for complete CLI documentation.

To control formatting:
- Enable/disable in `config.yaml` with `format.enabled: true/false`
- Configure formatters per file type in the `format` section

## Best Practices

### 1. Configure Per Project

Keep formatter configuration in your `config.yaml`:

```yaml
format:
  enabled: true
  formatters:
    ".py":
      type: "black"
      options:
        line_length: 120  # Match your project's line length
```

### 2. Use Standard Formatters

Prefer well-known formatters:
- **Python**: Black (opinionated, minimal config)
- **JavaScript/TypeScript**: Prettier (opinionated, good defaults)
- **Go**: gofmt (standard formatter)
- **Rust**: rustfmt (standard formatter)

### 3. Preserve Manual Sections

Always enable manual section preservation:

```yaml
defaults:
  preserve_manual_sections: true
```

This ensures user code isn't reformatted.

### 4. Ignore Generated Files

Skip formatting for files that shouldn't be formatted:

```yaml
defaults:
  ignore_patterns:
    - "*.min.js"
    - "vendor/**"
    - "**/node_modules/**"
```

### 5. Test Formatting

Test your formatting configuration:

```bash
# Generate with formatting
yagen -c config.yaml -d data.json -o output/

# Check if files are properly formatted
black --check output/**/*.py
prettier --check output/**/*.ts
```

### 6. Version Control Formatter Config

Include formatter configuration in version control:

```
.
├── config.yaml           # PyTemplify config with formatting
├── pyproject.toml        # Black config (optional)
├── .prettierrc           # Prettier config (optional)
└── .clang-format         # clang-format config (optional)
```

## Troubleshooting

### Formatter Not Found

**Error:** `Command not found: black`

**Solutions:**
```bash
# Install formatter
pip install black

# Or install all formatters
pip install pytemplify[formatting]

# Check installation
which black
black --version
```

### Manual Sections Reformatted

**Problem:** User code in manual sections was reformatted

**Solutions:**
- Ensure `preserve_manual_sections: true`
- Check marker syntax: `MANUAL SECTION START: name`
- Verify markers are on separate lines
- Check formatter logs for errors

### Formatting Timeout

**Problem:** Formatter takes too long

**Solutions:**
```yaml
".ext":
  type: "command"
  command: "slow_formatter ${input} > ${output}"
  options:
    timeout: 60  # Increase timeout (seconds)
```

### Wrong Formatter Applied

**Problem:** Files formatted with wrong formatter

**Solutions:**
- Check file extension matching: `.js|.ts` (OR, not AND)
- Verify file extension in pattern
- Check ignore patterns don't exclude files
- Use verbose mode to see which formatter is used

### Formatting Errors

**Problem:** Formatter produces errors

**Solutions:**
- Test formatter directly: `black input.py`
- Check formatter options in config
- Review generated code for syntax errors
- Check formatter version compatibility

### Files Not Being Formatted

**Problem:** No formatting applied

**Solutions:**
- Check `enabled: true` in config
- Verify file extension has formatter configured
- Check ignore patterns aren't excluding files
- Ensure formatter is installed
- Use verbose logging

## Advanced Usage

### Conditional Formatting

Format only specific template sets:

```yaml
templates:
  - name: "Production"
    folder: "prod_templates"
    output: "dist"
    # Formatting applied (global config)

  - name: "Debug"
    folder: "debug_templates"
    output: "debug"
    # Could disable formatting here if needed
```

### Multiple Formatters per Type

Apply different formatters based on subdirectories:

```python
from pytemplify.formatting import FormattingManager

# Create manager
manager = FormattingManager()

# Add formatters for different paths
manager.add_formatter(".py", black_formatter, path_pattern="src/**")
manager.add_formatter(".py", custom_formatter, path_pattern="tests/**")
```

### Pre/Post Processing

Add custom processing around formatting:

```python
class CustomFormatter(BaseFormatter):
    def format_string(self, content: str) -> str:
        # Pre-processing
        content = self.preprocess(content)

        # Format
        formatted = self.run_formatter(content)

        # Post-processing
        formatted = self.postprocess(formatted)

        return formatted

    def preprocess(self, content: str) -> str:
        # Remove custom markers
        return content

    def postprocess(self, content: str) -> str:
        # Add custom headers
        return f"# Auto-formatted\n{content}"
```

## Examples

### Python Project

```yaml
format:
  enabled: true
  defaults:
    preserve_manual_sections: true
  formatters:
    ".py":
      type: "black"
      options:
        line_length: 100
        target_version: ["py39"]
```

### JavaScript/TypeScript Project

```yaml
format:
  enabled: true
  formatters:
    ".js|.jsx":
      type: "prettier"
      options:
        semi: true
        singleQuote: true
        tabWidth: 2

    ".ts|.tsx":
      type: "prettier"
      options:
        semi: true
        singleQuote: true
        tabWidth: 2
```

### Mixed Project

```yaml
format:
  enabled: true
  defaults:
    preserve_manual_sections: true
  formatters:
    ".py":
      type: "black"
    ".js|.ts":
      type: "prettier"
    ".go":
      type: "command"
      command: "gofmt ${input} > ${output}"
```

## See Also

- [Getting Started](getting-started.md) - Quick start guide
- [YAGEN Guide](yagen-guide.md) - YAML-based generation
- [Template Guide](template-guide.md) - Template writing
- [API Reference](api-reference.md) - Python API
- [Examples](../examples/README.md) - Working examples
