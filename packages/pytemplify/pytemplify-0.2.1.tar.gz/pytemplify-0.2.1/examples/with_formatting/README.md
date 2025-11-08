# Code Formatting Example

This example demonstrates how to use pytemplify's optional code formatting feature to automatically format generated files.

## Overview

The formatting feature allows you to:

- Automatically format generated code using popular formatters
- Preserve manual sections during formatting
- Configure different formatters for different file types
- Use both built-in Python formatters and external command-line tools

## Files

- `config.yaml` - Template configuration with formatting enabled
- `data.json` - Sample data for code generation
- `templates/` - Jinja2 templates that will be formatted after generation
- `README.md` - This documentation

## Configuration

The `config.yaml` file includes a `format` section that configures code formatting:

```yaml
format:
  enabled: true  # Enable formatting globally

  defaults:
    preserve_manual_sections: true  # Keep manual sections intact
    ignore_patterns: ["*.min.*"]    # Files to skip formatting

  formatters:
    # Python files - use Black formatter
    ".py":
      type: "black"
      options:
        line_length: 88
        string_normalization: true

    # JavaScript files - use command-line prettier (more stable)
    ".js|.ts|.jsx|.tsx":
      type: "command"
      command: "prettier --stdin-filepath ${input} --parser typescript < ${input} > ${output}"
      options:
        timeout: 30

    # C/C++ files - use builtin cpp_format formatter (recommended)
    ".cpp|.hpp|.c|.h|.cc|.cxx":
      type: "cpp_format"
      options:
        style: "Google"    # or "LLVM", "Mozilla", etc.
        indent_width: 2    # indentation width

    # Alternative: use command-line clang-format (requires system installation)
    # ".cpp|.hpp|.c|.h|.cc|.cxx":
    #   type: "command"
    #   command: "clang-format -style=file ${input} > ${output}"
    #   extensions: [".cpp", ".hpp", ".c", ".h", ".cc", ".cxx"]
    #   options:
    #     timeout: 30
```

## Running the Example

Formatting dependencies are now included by default in pytemplify. For additional formatters:

```bash
# Install prettier via npm (recommended for stability):
npm install -g prettier

# Install clang-format (varies by OS) - only needed for command-line usage:
# Ubuntu/Debian:
sudo apt-get install clang-format
# macOS:
brew install clang-format
# Windows (via chocolatey):
choco install llvm
```

2. Run the generator:

```bash
yagen --config config.yaml --data data.json --output ./output
```

3. Check the generated files - they will be automatically formatted according to the configuration.

## Generated Output

The example generates:

- `service.py` - A Python service file formatted with Black
- `utils.js` - A JavaScript utility file formatted with Prettier
- `config.json` - A JSON configuration file (formatted with Prettier)
- `*.cpp` - C++ component files formatted with the builtin cpp_format formatter

## Manual Section Preservation

Notice how manual sections in the templates are preserved during formatting:

```python
# Generated code (formatted)
def process_data(data):
    """Process the input data."""
    if not data:
        return None

    # MANUAL SECTION START: custom_processing
    # This section is preserved exactly as written
    # even though the rest of the file is formatted
    result = data.copy()
    result['processed'] = True
    # MANUAL SECTION END

    return result
```

## Supported Formatters

### Built-in Formatters (Python APIs)

- **Black**: Python code formatter (included by default)
- **Prettier**: JavaScript, TypeScript, JSON, CSS, HTML, Markdown (use command-line version for stability)
- **cpp_format**: C/C++ formatter using clang-format (included by default)

### Command Formatters (CLI Tools)

- **clang-format**: C/C++ formatter (system installation required - see installation instructions below)
- **prettier**: JavaScript, TypeScript, JSON, CSS, HTML, Markdown (`npm install -g prettier`)
- **Custom commands**: Any command-line formatter using `${input}` and `${output}` placeholders

## Custom Formatter Example

You can also define custom formatters:

```yaml
formatters:
  ".custom":
    type: "command"
    command: "my-custom-formatter --input ${input} --output ${output}"
    options:
      timeout: 30
```

## C++ Format Configuration

The builtin `cpp_format` formatter uses clang-format styles. You can configure it with:

- **Style**: Predefined styles like "Google", "LLVM", "Mozilla", "WebKit", "Microsoft"
- **Indent Width**: Number of spaces for indentation
- **Custom Styles**: Full clang-format configuration options

For command-line clang-format usage, this example includes a `.clang-format` configuration file that defines the formatting style for C++ code. The configuration uses:

- **Style Base**: LLVM style with customizations
- **Indentation**: 4 spaces, no tabs
- **Line Length**: 120 characters
- **Brace Style**: Attach (K&R style)
- **Pointer Alignment**: Left (`int* ptr` not `int *ptr`)
- **Include Sorting**: Automatically sorts and groups includes

You can customize the `.clang-format` file to match your project's coding standards. Common style bases include:

- `LLVM` - LLVM coding standards
- `Google` - Google C++ Style Guide
- `Chromium` - Chromium project style
- `Mozilla` - Mozilla style
- `WebKit` - WebKit style
- `Microsoft` - Microsoft style

### Example C++ Output

Generated C++ files will be formatted according to the builtin cpp_format configuration:

```cpp
namespace processing {

class DataProcessor {
private:
    bool initialized_;
    std::string name_;

public:
    DataProcessor() : initialized_(false), name_("DataProcessor") {
        std::cout << "Initializing DataProcessor..." << std::endl;
    }

    bool process(const std::vector<int>& data) {
        if (!initialized_) {
            throw std::runtime_error("DataProcessor not initialized");
        }
        return true;
    }

    // MANUAL SECTION START: custom_methods
    // This section is preserved exactly as written
    void customMethod() {
        std::cout << "Custom implementation" << std::endl;
    }
    // MANUAL SECTION END
};

} // namespace processing
```

## Troubleshooting

### Clang-Format Installation

If clang-format is not available, you'll see a warning but generation will continue. To install:

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install clang-format
```

**macOS:**

```bash
brew install clang-format
```

**Windows:**

```bash
# Using Chocolatey
choco install llvm

# Or download from LLVM releases:
# https://releases.llvm.org/
```

**Verify installation:**

```bash
clang-format --version
```

### Prettier Installation (Recommended: Command Line)

For stability, use the command-line version of prettier via npm:

```bash
# Install prettier globally via npm (recommended)
npm install -g prettier

# Or install locally in your project
npm install prettier
```

The command-line formatter will automatically find prettier if it's installed globally or locally.

### Alternative: Python prettier Package

If you prefer the Python package (may have installation issues):

```bash
pip install prettier
```

But the command-line version is more reliable and stable.

### Formatter Not Found

If a formatter is not installed, pytemplify will:

1. Log a warning message
2. Skip formatting for that file type
3. Continue generation with unformatted output

This ensures generation never fails due to missing formatters.
