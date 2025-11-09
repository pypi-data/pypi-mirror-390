# Built-in Filters Reference

Complete reference for all built-in Jinja2 filters provided by PyTemplify.

## Overview

PyTemplify automatically registers a comprehensive set of filters when you create a `TemplateRenderer`. These filters are organized into four categories:

1. **[String Filters](#string-filters)** - String manipulation and transformation
2. **[Collection Filters](#collection-filters)** - List, dict, and set operations
3. **[Formatting Filters](#formatting-filters)** - Data formatting (dates, numbers, etc.)
4. **[Utility Filters](#utility-filters)** - Common utility operations

## String Filters

String manipulation and case conversion filters.

### Case Conversion

#### camelcase
Convert string to camelCase.

```jinja2
{{ "hello_world" | camelcase }}      → "helloWorld"
{{ "hello-world" | camelcase }}      → "helloWorld"
{{ "hello world" | camelcase }}      → "helloWorld"
```

#### pascalcase
Convert string to PascalCase.

```jinja2
{{ "hello_world" | pascalcase }}     → "HelloWorld"
{{ "hello-world" | pascalcase }}     → "HelloWorld"
{{ "hello world" | pascalcase }}     → "HelloWorld"
```

#### snakecase
Convert string to snake_case.

```jinja2
{{ "HelloWorld" | snakecase }}       → "hello_world"
{{ "helloWorld" | snakecase }}       → "hello_world"
{{ "hello-world" | snakecase }}      → "hello_world"
```

#### kebabcase
Convert string to kebab-case.

```jinja2
{{ "HelloWorld" | kebabcase }}       → "hello-world"
{{ "helloWorld" | kebabcase }}       → "hello-world"
{{ "hello_world" | kebabcase }}      → "hello-world"
```

#### screamingsnakecase
Convert string to SCREAMING_SNAKE_CASE.

```jinja2
{{ "HelloWorld" | screamingsnakecase }}    → "HELLO_WORLD"
{{ "helloWorld" | screamingsnakecase }}    → "HELLO_WORLD"
{{ "hello-world" | screamingsnakecase }}   → "HELLO_WORLD"
```

### String Normalization

#### normalize
Normalize string to be safe for filenames and URLs.

```jinja2
{{ "Hello World!" | normalize }}     → "hello_world"
{{ "/api/v1/users" | normalize }}    → "api_v1_users"
```

#### slugify
Convert string to URL-friendly slug.

```jinja2
{{ "Hello World!" | slugify }}       → "hello-world"
{{ "  Product #123  " | slugify }}   → "product-123"
```

### String Manipulation

#### remove_prefix
Remove prefix from string if it exists.

```jinja2
{{ "HelloWorld" | remove_prefix("Hello") }}        → "World"
{{ "test_value" | remove_prefix("test_") }}        → "value"
```

#### remove_suffix
Remove suffix from string if it exists.

```jinja2
{{ "HelloWorld" | remove_suffix("World") }}        → "Hello"
{{ "test.txt" | remove_suffix(".txt") }}           → "test"
```

#### truncate_custom
Truncate string to specified length with custom ending.

**Parameters:**
- `length` (int): Maximum length
- `end` (str): Ending string (default: "...")

```jinja2
{{ "Hello World" | truncate_custom(8) }}           → "Hello..."
{{ "Hello World" | truncate_custom(8, end=">>") }} → "Hello>>"
```

#### wrap_text
Wrap text to specified width.

**Parameters:**
- `width` (int): Maximum line width (default: 80)
- `break_long_words` (bool): Break words longer than width (default: True)

```jinja2
{{ long_text | wrap_text(40) }}
```

#### indent_custom
Indent text with custom options.

**Parameters:**
- `width` (int): Number of spaces to indent (default: 4)
- `first` (bool): Whether to indent the first line (default: False)
- `blank` (bool): Whether to indent blank lines (default: False)

```jinja2
{{ "line1\nline2" | indent_custom(4) }}                → "line1\n    line2"
{{ "line1\nline2" | indent_custom(4, first=true) }}    → "    line1\n    line2"
```

#### quote_string
Wrap string in quotes, escaping any quotes inside.

**Parameters:**
- `quote_char` (str): Quote character (default: '"')

```jinja2
{{ 'hello' | quote_string }}                 → '"hello"'
{{ "it's" | quote_string("'") }}             → "'it\\'s'"
```

### Regular Expressions

#### regex_replace
Replace using regular expressions.

**Parameters:**
- `pattern` (str): Regular expression pattern
- `replacement` (str): Replacement string
- `count` (int): Maximum number of replacements (0 = all, default)

```jinja2
{{ "test123" | regex_replace(r'\d+', 'NUM') }}         → "testNUM"
{{ "a1b2c3" | regex_replace(r'\d', 'X', count=2) }}    → "aXbXc3"
```

#### regex_search
Check if pattern matches anywhere in string.

```jinja2
{{ "test123" | regex_search(r'\d+') }}     → True
{{ "test" | regex_search(r'\d+') }}        → False
```

#### regex_findall
Find all matches of pattern in string.

```jinja2
{{ "test 123 hello 456" | regex_findall(r'\d+') }}    → ["123", "456"]
```

---

## Collection Filters

Operations for lists, dictionaries, and sets.

### List Operations

#### flatten
Flatten nested lists to specified depth.

**Parameters:**
- `levels` (int): Number of levels to flatten (default: 1, use -1 for complete flattening)

```jinja2
{{ [[1, 2], [3, 4]] | flatten }}              → [1, 2, 3, 4]
{{ [[[1]], [[2]], [[3]]] | flatten(2) }}      → [1, 2, 3]
{{ [[[1]], [[2]]] | flatten(-1) }}            → [1, 2]  (complete)
```

#### unique
Remove duplicate items from list while preserving order.

```jinja2
{{ [1, 2, 2, 3, 1] | unique }}     → [1, 2, 3]
{{ ["a", "b", "a"] | unique }}     → ["a", "b"]
```

#### compact
Remove falsy values (None, False, 0, "", [], {}) from list.

```jinja2
{{ [1, None, 2, False, 3, "", 4] | compact }}    → [1, 2, 3, 4]
```

#### chunk
Split list into chunks of specified size.

```jinja2
{{ [1, 2, 3, 4, 5] | chunk(2) }}              → [[1, 2], [3, 4], [5]]
{{ range(10) | list | chunk(3) }}             → [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
```

### List Querying

#### pluck
Extract values for a specific key from list of dictionaries.

```jinja2
{{ users | pluck("name") }}        → ["Alice", "Bob", "Charlie"]
{{ items | pluck("id") }}          → [1, 2, 3]
```

#### where
Filter list of dictionaries by key/value.

**Parameters:**
- `key` (str): Key to check
- `test_value` (Any): Value to match (if None, checks for truthy values)

```jinja2
{{ users | where("active", true) }}          → [users where active=true]
{{ items | where("status") }}                → [items where status is truthy]
```

#### sort_by
Sort list of objects/dicts by a specific attribute/key.

**Parameters:**
- `key` (str): Attribute/key name
- `reverse` (bool): Sort in reverse order (default: False)

```jinja2
{{ users | sort_by("age") }}                     → [users sorted by age]
{{ items | sort_by("price", reverse=true) }}     → [items sorted by price descending]
```

#### group_by
Group list items by a specific key/attribute.

```jinja2
{{ users | group_by("role") }}        → {"admin": [...], "user": [...]}
{{ items | group_by("category") }}    → {"electronics": [...], "books": [...]}
```

#### index_of
Get index of item in list (-1 if not found).

```jinja2
{{ [1, 2, 3] | index_of(2) }}      → 1
{{ ["a", "b"] | index_of("c") }}   → -1
```

### Set Operations

#### intersection
Get intersection of two lists (common elements).

```jinja2
{{ [1, 2, 3] | intersection([2, 3, 4]) }}    → [2, 3]
```

#### difference
Get difference of two lists (elements in first but not second).

```jinja2
{{ [1, 2, 3] | difference([2, 3, 4]) }}      → [1]
```

#### union
Get union of two lists (all unique elements from both).

```jinja2
{{ [1, 2, 3] | union([3, 4, 5]) }}           → [1, 2, 3, 4, 5]
```

### Dictionary Operations

#### dict_keys
Get list of dictionary keys.

```jinja2
{{ {"a": 1, "b": 2} | dict_keys }}     → ["a", "b"]
```

#### dict_values
Get list of dictionary values.

```jinja2
{{ {"a": 1, "b": 2} | dict_values }}   → [1, 2]
```

#### dict_items
Get list of dictionary (key, value) tuples.

```jinja2
{{ {"a": 1, "b": 2} | dict_items }}    → [("a", 1), ("b", 2)]
```

#### merge_dicts
Merge multiple dictionaries (later dicts override earlier ones).

```jinja2
{{ merge_dicts({"a": 1}, {"b": 2}, {"a": 3}) }}    → {"a": 3, "b": 2}
```

### Advanced Operations

#### zip_lists
Zip multiple lists together.

```jinja2
{{ zip_lists([1, 2, 3], ["a", "b", "c"]) }}    → [(1, "a"), (2, "b"), (3, "c")]
```

---

## Formatting Filters

Data formatting for numbers, dates, currency, and more.

### Number Formatting

#### format_number
Format number with thousands separator and decimals.

**Parameters:**
- `decimals` (int): Number of decimal places (default: 2)
- `thousands_sep` (str): Thousands separator (default: ",")

```jinja2
{{ 1234567.89 | format_number }}                → "1,234,567.89"
{{ 1234567.89 | format_number(0) }}             → "1,234,568"
{{ 1234567.89 | format_number(2, " ") }}        → "1 234 567.89"
```

#### format_bytes
Format bytes to human-readable size.

**Parameters:**
- `precision` (int): Decimal places (default: 2)

```jinja2
{{ 1024 | format_bytes }}          → "1.00 KB"
{{ 1048576 | format_bytes }}       → "1.00 MB"
{{ 1073741824 | format_bytes(1) }} → "1.0 GB"
```

#### format_percentage
Format number as percentage.

**Parameters:**
- `decimals` (int): Number of decimal places (default: 2)
- `multiply` (bool): Whether to multiply by 100 (default: True)

```jinja2
{{ 0.1234 | format_percentage }}                   → "12.34%"
{{ 50 | format_percentage(multiply=false) }}       → "50.00%"
```

#### format_ordinal
Convert number to ordinal (1st, 2nd, 3rd, etc.).

```jinja2
{{ 1 | format_ordinal }}       → "1st"
{{ 22 | format_ordinal }}      → "22nd"
{{ 103 | format_ordinal }}     → "103rd"
```

### Currency Formatting

#### format_currency
Format number as currency.

**Parameters:**
- `symbol` (str): Currency symbol (default: "$")
- `position` (str): Symbol position "before" or "after" (default: "before")

```jinja2
{{ 1234.56 | format_currency }}                    → "$1,234.56"
{{ 1234.56 | format_currency("€", "after") }}      → "1,234.56€"
```

### Date/Time Formatting

#### format_date
Format datetime object or timestamp.

**Parameters:**
- `format_str` (str): strftime format string (default: "%Y-%m-%d")

```jinja2
{{ now() | format_date }}                                      → "2024-10-16"
{{ timestamp | format_date("%Y-%m-%d %H:%M:%S") }}             → "2024-10-16 14:30:00"
{{ "2024-10-16" | format_date("%B %d, %Y") }}                  → "October 16, 2024"
```

### Other Formatting

#### format_phone
Format phone number.

**Parameters:**
- `format_str` (str): Format string with placeholders (default: "({area}) {prefix}-{line}")

```jinja2
{{ "1234567890" | format_phone }}                                  → "(123) 456-7890"
{{ "1234567890" | format_phone("{area}-{prefix}-{line}") }}        → "123-456-7890"
```

#### pad_left
Pad string on the left to specified width.

**Parameters:**
- `width` (int): Total width
- `fillchar` (str): Fill character (default: " ")

```jinja2
{{ "5" | pad_left(3, "0") }}       → "005"
{{ "test" | pad_left(10) }}        → "      test"
```

#### pad_right
Pad string on the right to specified width.

```jinja2
{{ "5" | pad_right(3, "0") }}      → "500"
{{ "test" | pad_right(10) }}       → "test      "
```

### Data Serialization

#### format_json
Format value as pretty-printed JSON.

**Parameters:**
- `indent` (int): Indentation level (default: 2, None for compact)

```jinja2
{{ {"key": "value"} | format_json }}               → formatted JSON string
{{ data | format_json(4) }}                        → JSON with 4-space indent
```

#### format_yaml
Format value as YAML (requires PyYAML).

```jinja2
{{ {"key": "value"} | format_yaml }}
```

#### format_xml_escape
Escape XML special characters.

```jinja2
{{ "<tag>value</tag>" | format_xml_escape }}       → "&lt;tag&gt;value&lt;/tag&gt;"
```

#### format_sql_escape
Escape single quotes for SQL strings.

```jinja2
{{ "O'Brien" | format_sql_escape }}                → "O''Brien"
```

---

## Utility Filters

Common utility operations and type checking.

### Default Values

#### default_if_none
Return default value if input is None (more explicit than Jinja's default).

```jinja2
{{ None | default_if_none("N/A") }}        → "N/A"
{{ "" | default_if_none("N/A") }}          → ""
{{ False | default_if_none("N/A") }}       → False
```

#### coalesce
Return first non-None value from arguments.

```jinja2
{{ coalesce(None, None, "first", "second") }}      → "first"
{{ coalesce(None, 0, 5) }}                         → 0
```

#### ternary
Ternary operator (condition ? true_value : false_value).

```jinja2
{{ ternary(age >= 18, "Adult", "Minor") }}
{{ ternary(count > 0, "items", "no items") }}
```

### Type Checking

#### type_name
Get type name of value.

```jinja2
{{ "hello" | type_name }}      → "str"
{{ 123 | type_name }}          → "int"
{{ [1, 2, 3] | type_name }}    → "list"
```

#### is_list
Check if value is a list.

```jinja2
{{ [1, 2, 3] | is_list }}      → True
{{ "test" | is_list }}         → False
```

#### is_dict
Check if value is a dictionary.

```jinja2
{{ {"key": "value"} | is_dict }}   → True
{{ [1, 2] | is_dict }}             → False
```

#### is_string
Check if value is a string.

```jinja2
{{ "hello" | is_string }}      → True
{{ 123 | is_string }}          → False
```

#### is_number
Check if value is a number (int or float).

```jinja2
{{ 123 | is_number }}          → True
{{ 45.67 | is_number }}        → True
{{ "123" | is_number }}        → False
```

#### is_even
Check if number is even.

```jinja2
{{ 4 | is_even }}              → True
{{ 5 | is_even }}              → False
```

#### is_odd
Check if number is odd.

```jinja2
{{ 5 | is_odd }}               → True
{{ 4 | is_odd }}               → False
```

### Hashing and Encoding

#### hash_md5
Generate MD5 hash of string.

```jinja2
{{ "hello" | hash_md5 }}       → "5d41402abc4b2a76b9719d911017c592"
```

#### hash_sha256
Generate SHA256 hash of string.

```jinja2
{{ "hello" | hash_sha256 }}    → "2cf24dba5fb0a30e..."
```

#### b64encode
Base64 encode string.

```jinja2
{{ "hello" | b64encode }}      → "aGVsbG8="
```

#### b64decode
Base64 decode string.

```jinja2
{{ "aGVsbG8=" | b64decode }}   → "hello"
```

### Random Generation

#### random_string
Generate random string.

**Parameters:**
- `length` (int): Length of string (default: 10)
- `charset` (str): Character set - "alphanumeric", "alpha", "numeric", "hex" (default: "alphanumeric")

```jinja2
{{ random_string(8) }}                 → "aB3xYz7Q"
{{ random_string(6, "numeric") }}      → "482759"
{{ random_string(8, "hex") }}          → "a3f7e901"
```

#### random_int
Generate random integer in range.

```jinja2
{{ random_int(1, 10) }}                → random number between 1 and 10
```

#### uuid_generate
Generate UUID with optional deterministic mode.

**Parameters:**
- `value` (str, optional): Value/name for deterministic UUID
- `namespace` (str, optional): Namespace - "dns"/"url"/"oid"/"x500"/"pytemplify" or custom UUID

```jinja2
{{ uuid_generate() }}                                  → Random UUID4
{{ uuid_generate("my_service") }}                      → Deterministic UUID5
{{ uuid_generate("my_service", "url") }}               → UUID5 with URL namespace
{{ "my_service" | uuid_generate }}                     → Deterministic UUID5 (as filter)
```

### Math Operations

#### abs_value
Get absolute value of number.

```jinja2
{{ -5 | abs_value }}           → 5
{{ 3.14 | abs_value }}         → 3.14
```

#### clamp
Clamp value between min and max.

```jinja2
{{ 15 | clamp(0, 10) }}        → 10
{{ -5 | clamp(0, 10) }}        → 0
{{ 5 | clamp(0, 10) }}         → 5
```

#### safe_divide
Divide with safe handling of division by zero.

**Parameters:**
- `divisor` (float): Divisor
- `default` (float): Default value if division by zero (default: 0.0)

```jinja2
{{ 10 | safe_divide(2) }}                  → 5.0
{{ 10 | safe_divide(0) }}                  → 0.0
{{ 10 | safe_divide(0, default=-1) }}      → -1.0
```

### Conversion

#### bool_to_string
Convert boolean to custom string representation.

```jinja2
{{ True | bool_to_string }}                        → "true"
{{ False | bool_to_string("yes", "no") }}          → "no"
{{ enabled | bool_to_string("ON", "OFF") }}
```

### File Path Operations

#### file_extension
Get file extension from filename or path.

```jinja2
{{ "document.pdf" | file_extension }}              → "pdf"
{{ "/path/to/file.txt" | file_extension }}         → "txt"
```

#### file_basename
Get filename without path.

```jinja2
{{ "/path/to/file.txt" | file_basename }}          → "file.txt"
```

#### file_dirname
Get directory path from file path.

```jinja2
{{ "/path/to/file.txt" | file_dirname }}           → "/path/to"
```

### Object Access

#### get_attr
Safely get attribute from object.

```jinja2
{{ user | get_attr("email", "no-email@example.com") }}
```

#### get_item
Safely get item from dict/list.

```jinja2
{{ data | get_item("key", "default_value") }}
{{ items | get_item(0, "no items") }}
```

#### map_value
Map value using dictionary lookup.

```jinja2
{{ "red" | map_value({"red": "#FF0000", "blue": "#0000FF"}) }}     → "#FF0000"
{{ "green" | map_value({"red": "#FF0000"}, default="unknown") }}   → "unknown"
```

---

## Using Filters

### Basic Usage

```jinja2
{{ variable | filter_name }}
{{ variable | filter_name(arg1, arg2) }}
{{ variable | filter_name(param=value) }}
```

### Chaining Filters

```jinja2
{{ service.name | snakecase | upper }}
→ "UserService" → "user_service" → "USER_SERVICE"

{{ items | map(attribute='name') | unique | sort | join(', ') }}
```

### In Expressions

```jinja2
{% if name | is_string %}
    String: {{ name }}
{% endif %}

{% for item in items | where("active", true) | sort_by("priority") %}
    {{ item.name }}
{% endfor %}
```

### Disabling Auto-Registration

If you want to use only specific filters:

```python
from pytemplify.renderer import TemplateRenderer

# Disable auto-registration
renderer = TemplateRenderer(data, auto_register_filters=False)

# Register only specific filters
from pytemplify.filters import get_string_filters
renderer.env.filters.update(get_string_filters())
```

### Adding Custom Filters

```python
def custom_filter(value):
    return f"custom_{value}"

renderer = TemplateRenderer(data, filters={"custom": custom_filter})

# In template: {{ "test" | custom }}  → "custom_test"
```

## Complete Filter List

### String Filters (16)
- camelcase, pascalcase, snakecase, kebabcase, screamingsnakecase
- normalize, slugify
- indent_custom, remove_prefix, remove_suffix, wrap_text, truncate_custom
- regex_replace, regex_search, regex_findall, quote_string

### Collection Filters (17)
- flatten, unique, chunk, pluck, where, sort_by, group_by
- merge_dicts, dict_keys, dict_values, dict_items
- zip_lists, index_of, compact
- intersection, difference, union

### Formatting Filters (13)
- format_number, format_bytes, format_percentage, format_ordinal
- format_currency, format_date, format_phone
- pad_left, pad_right
- format_json, format_yaml, format_xml_escape, format_sql_escape

### Utility Filters (24)
- default_if_none, coalesce, ternary
- type_name, is_list, is_dict, is_string, is_number, is_even, is_odd
- hash_md5, hash_sha256, b64encode, b64decode
- random_string, random_int, uuid_generate
- abs_value, clamp, safe_divide
- bool_to_string
- file_extension, file_basename, file_dirname
- get_attr, get_item, map_value

**Total: 70 built-in filters**

## See Also

- [Template Guide](template-guide.md) - Template writing guide
- [API Reference](api-reference.md) - Python API documentation
- [Getting Started](getting-started.md) - Quick start guide
- [Examples](../examples/README.md) - Working examples
