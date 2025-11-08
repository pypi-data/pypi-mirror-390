# Data Helpers

## Overview

The `data_helpers` module provides a powerful way to add computed properties and methods to dictionary data without modifying the original data structure. This is especially useful when working with JSON data or dictionaries that need additional helper methods for template rendering.

## Key Features

✅ **Automatic Schema Detection** - Helpers are automatically applied based on data structure matching
✅ **Property & Method Support** - Use `@property`, `@cached_property`, and regular methods
✅ **Nested Data Wrapping** - Automatically wraps nested dictionaries and lists
✅ **Helper-to-Helper Communication** - Helpers can access other helpers seamlessly
✅ **Cross-Level Queries** - Access root and parent data from nested helpers
✅ **Template Integration** - Works seamlessly with `TemplateRenderer`
✅ **Non-Invasive** - Original data remains unchanged

## Quick Start

```python
from pytemplify.data_helpers import wrap_with_helpers, DataHelper
from pytemplify.renderer import TemplateRenderer

# Define a helper class
class CompanyHelpers(DataHelper):
    @staticmethod
    def matches(data: dict) -> bool:
        return "company_name" in data and "employees" in data

    @property
    def employee_count(self):
        return len(self._data.employees)

    @property
    def total_salary(self):
        return sum(emp.salary for emp in self._data.employees)

# Your data
data = {
    "company_name": "TechCorp",
    "employees": [
        {"name": "Alice", "salary": 100000},
        {"name": "Bob", "salary": 80000}
    ]
}

# Wrap with helpers
wrapped = wrap_with_helpers(data, [CompanyHelpers])

# Use directly
print(wrapped.employee_count)  # 2
print(wrapped.total_salary)     # 180000

# Use with templates
renderer = TemplateRenderer(data={"company": wrapped})
output = renderer.render_string("{{ company.company_name }}: {{ company.employee_count }} employees")
print(output)  # "TechCorp: 2 employees"
```

## Core Concepts

### DataHelper Base Class

All helpers must inherit from `DataHelper` and implement the `matches()` method:

```python
from pytemplify.data_helpers import DataHelper

class MyHelper(DataHelper):
    @staticmethod
    def matches(data: dict) -> bool:
        """Return True if this helper should be applied to the given data."""
        return "some_key" in data and isinstance(data.get("other_key"), list)

    @property
    def computed_value(self):
        """Computed properties are accessible as attributes."""
        return self._data.some_key * 2

    def helper_method(self, param):
        """Methods can accept parameters."""
        return [item for item in self._data.other_key if item > param]
```

### Accessing Data

Within a helper, you have access to:

- **`self._data`** - Smart wrapper that automatically wraps nested values
- **`self._raw_data`** - Unwrapped original dictionary
- **`self._root_data`** - Root-level data for cross-level queries
- **`self._parent_data`** - Parent-level data (None at root level)

```python
class EmployeeHelpers(DataHelper):
    @staticmethod
    def matches(data: dict) -> bool:
        return "name" in data and "salary" in data

    @property
    def annual_cost(self):
        # Access primitive values directly
        return self._data.salary * 1.2

    @property
    def company_name(self):
        # Access root data from nested context
        return self._root_data.get("company_name", "Unknown")
```

## Advanced Usage

### Nested Helpers

Helpers automatically apply to nested structures:

```python
data = {
    "company_name": "TechCorp",
    "offices": [
        {
            "city": "NYC",
            "employees": [
                {"name": "Alice", "salary": 100000}
            ]
        }
    ]
}

class CompanyHelpers(DataHelper):
    @staticmethod
    def matches(data: dict) -> bool:
        return "company_name" in data

    @property
    def total_employees(self):
        # OfficeHelpers automatically applied to each office
        return sum(office.employee_count for office in self._data.offices)

class OfficeHelpers(DataHelper):
    @staticmethod
    def matches(data: dict) -> bool:
        return "city" in data and "employees" in data

    @property
    def employee_count(self):
        return len(self._data.employees)

wrapped = wrap_with_helpers(data, [CompanyHelpers, OfficeHelpers])
print(wrapped.total_employees)  # Counts employees across all offices
```

### Cross-Helper Communication

Helpers can access properties/methods from other helpers:

```python
class CompanyHelpers(DataHelper):
    @property
    def total_cost(self):
        # Uses OfficeHelpers.total_salary_cost which uses EmployeeHelpers.annual_cost
        return sum(office.total_salary_cost for office in self._data.offices)

class OfficeHelpers(DataHelper):
    @property
    def total_salary_cost(self):
        # EmployeeHelpers automatically applied to each employee
        return sum(emp.annual_cost for emp in self._data.employees)

class EmployeeHelpers(DataHelper):
    @property
    def annual_cost(self):
        return self._data.salary * 1.2  # Salary + 20% benefits
```

### Cached Properties

Use `@cached_property` for expensive computations:

```python
from functools import cached_property

class DataHelper(DataHelper):
    @cached_property
    def expensive_computation(self):
        # Computed only once, then cached
        return complex_analysis(self._data)
```

### Methods with Parameters

Helpers can have methods that accept parameters:

```python
class CompanyHelpers(DataHelper):
    def get_employees_by_city(self, city: str):
        """Cross-level query method."""
        for office in self._data.offices:
            if office._data.city == city:
                return office._data.employees
        return []

# In templates
wrapped = wrap_with_helpers(data, [CompanyHelpers])
nyc_employees = wrapped.get_employees_by_city("NYC")
```

## Template Integration

Data helpers work seamlessly with Jinja2 templates:

```python
from pytemplify.renderer import TemplateRenderer
from pytemplify.data_helpers import wrap_with_helpers

wrapped = wrap_with_helpers(data, [CompanyHelpers, EmployeeHelpers])
renderer = TemplateRenderer(data={"company": wrapped})

template = """
Company: {{ company.company_name }}
Employees: {{ company.employee_count }}
Total Cost: ${{ company.total_cost }}

{% for office in company.offices %}
Office: {{ office.city }} - {{ office.employee_count }} employees
  {% for emp in office.employees %}
  - {{ emp.name }}: ${{ emp.annual_cost }}
  {% endfor %}
{% endfor %}
"""

output = renderer.render_string(template)
```

### Using Jinja2 Filters with Helpers

```python
template = "{{ company.employees | map(attribute='name') | join(', ') }}"
# Works! Each employee is wrapped with EmployeeHelpers
```

## Design Principles

### 1. Helper Priority

When accessing attributes:
- **Attribute access (`.`)**: Helper properties/methods take precedence over dict keys
- **Bracket access (`[]`)**: Dict keys are accessed directly (no helper priority)

```python
data = {"name": "Test", "count": 999}

class Helper(DataHelper):
    @property
    def count(self):
        return 42

wrapped = wrap_with_helpers(data, [Helper])
print(wrapped.count)    # 42 (helper property)
print(wrapped["count"]) # 999 (original dict value)
```

### 2. Automatic Wrapping

All nested structures are automatically wrapped:

```python
# When you access self._data.nested_list, each item is automatically wrapped
for item in self._data.nested_list:
    # item is a DictProxy with helpers applied
    print(item.helper_property)
```

### 3. Read-Only Wrapper

DictProxy is read-only to prevent accidental data mutation:

```python
wrapped = wrap_with_helpers(data, [Helper])
wrapped.new_key = "value"  # Raises AttributeError
```

## Best Practices

### 1. Specific Matching

Make your `matches()` method as specific as possible:

```python
# ✅ Good - specific
@staticmethod
def matches(data: dict) -> bool:
    return "company_name" in data and "offices" in data and "founded_year" in data

# ❌ Bad - too broad
@staticmethod
def matches(data: dict) -> bool:
    return "name" in data  # Matches too many things!
```

### 2. Automatic Helper Ordering

By default, helpers are **automatically sorted by specificity** - more specific helpers are checked first:

```python
# ✅ Order doesn't matter - automatic ordering enabled by default
wrapped = wrap_with_helpers(data, [
    GenericCompanyHelpers,   # Checks 1 field - will be checked last
    SpecificCompanyHelpers,  # Checks 3 fields - will be checked first
])
# Automatically reordered to: [SpecificCompanyHelpers, GenericCompanyHelpers]
```

**Specificity Scoring:**

- Each `"key" in data` check: +10 points
- Each `isinstance()` check: +5 points
- Each `.get()` call: +3 points
- Each comparison operator: +2 points

**Manual Ordering (if needed):**

```python
# Disable auto-ordering to preserve your order
wrapped = wrap_with_helpers(data, [Helper1, Helper2], auto_order=False)
```

**Explicit Priority (for fine control):**

```python
class HighPriorityHelper(DataHelper):
    priority = 1000  # Explicit priority overrides automatic calculation

    @staticmethod
    def matches(data: dict) -> bool:
        return "name" in data
```

### 3. Performance

- Use `@cached_property` for expensive computations
- Access `self._raw_data` for raw dictionary access (no wrapping overhead)
- Helpers are cached per data object

### 4. Error Handling

```python
class SafeHelper(DataHelper):
    @property
    def safe_value(self):
        # Handle missing keys gracefully
        return self._data.get("optional_key", "default")

    @property
    def calculated_value(self):
        try:
            return self._data.value1 / self._data.value2
        except (KeyError, ZeroDivisionError):
            return 0
```

## Complete Example

```python
from pytemplify.data_helpers import wrap_with_helpers, DataHelper
from pytemplify.renderer import TemplateRenderer
from functools import cached_property

# Sample data
company_data = {
    "company_name": "TechCorp",
    "founded_year": 2010,
    "offices": [
        {
            "city": "NYC",
            "country": "USA",
            "employees": [
                {"name": "Alice", "department": "IT", "salary": 100000, "years": 6},
                {"name": "Bob", "department": "HR", "salary": 80000, "years": 3},
            ]
        },
        {
            "city": "London",
            "country": "UK",
            "employees": [
                {"name": "Charlie", "department": "IT", "salary": 90000, "years": 5},
            ]
        }
    ]
}

# Define helpers
class CompanyHelpers(DataHelper):
    @staticmethod
    def matches(data: dict) -> bool:
        return "company_name" in data and "offices" in data

    @property
    def employee_count(self):
        return sum(office.employee_count for office in self._data.offices)

    @property
    def total_cost(self):
        return sum(office.total_salary_cost for office in self._data.offices)

    def get_employees_by_city(self, city: str):
        for office in self._data.offices:
            if office._data.city == city:
                return office._data.employees
        return []

class OfficeHelpers(DataHelper):
    @staticmethod
    def matches(data: dict) -> bool:
        return "city" in data and "employees" in data

    @property
    def employee_count(self):
        return len(self._data.employees)

    @property
    def total_salary_cost(self):
        return sum(emp.annual_cost for emp in self._data.employees)

class EmployeeHelpers(DataHelper):
    @staticmethod
    def matches(data: dict) -> bool:
        return "name" in data and "salary" in data

    @property
    def annual_cost(self):
        return self._data.salary * 1.2

    @property
    def is_senior(self):
        return self._data.years >= 5

    @cached_property
    def display_name(self):
        return f"{self._data.name} ({self._data.department})"

# Wrap data
wrapped = wrap_with_helpers(company_data, [CompanyHelpers, OfficeHelpers, EmployeeHelpers])

# Use directly
print(f"Total employees: {wrapped.employee_count}")
print(f"Total cost: ${wrapped.total_cost}")

# Use with templates
renderer = TemplateRenderer(data={"company": wrapped})
template = """
Company: {{ company.company_name }} (Founded {{ company.founded_year }})
Total Employees: {{ company.employee_count }}
Total Annual Cost: ${{ company.total_cost }}

Offices:
{% for office in company.offices %}
  {{ office.city }}, {{ office.country }}:
  {% for emp in office.employees %}
    - {{ emp.display_name }}: ${{ emp.annual_cost }} {% if emp.is_senior %}(Senior){% endif %}
  {% endfor %}
{% endfor %}
"""

output = renderer.render_string(template)
print(output)
```

## API Reference

### `wrap_with_helpers(data, helpers)`

Wrap dictionary data with helper extensions.

**Parameters:**
- `data` (dict): Dictionary data to wrap
- `helpers` (List[Type[DataHelper]]): List of DataHelper classes to apply

**Returns:**
- `DictProxy`: Wrapped dictionary with helpers applied

**Raises:**
- `TypeError`: If data is not a dictionary

### `DataHelper` (Abstract Base Class)

Base class for all data helpers.

**Methods to Implement:**
- `matches(data: dict) -> bool`: Return True if helper applies to the data

**Available Attributes:**
- `self._data`: SmartDataDict that auto-wraps nested values
- `self._raw_data`: Unwrapped original dictionary
- `self._root_data`: Root-level data for cross-level queries
- `self._parent_data`: Parent-level data (None at root)

## Troubleshooting

### Helper Not Applied

Check that your `matches()` method returns `True` for your data:

```python
# Debug helper matching
helper_class = MyHelper
print(helper_class.matches(my_data))  # Should print True
```

### Attribute Not Found

Remember that helpers must be in the helpers list:

```python
# ❌ Forgot to include EmployeeHelpers
wrapped = wrap_with_helpers(data, [CompanyHelpers])
wrapped.offices[0].employees[0].annual_cost  # AttributeError!

# ✅ Include all helpers
wrapped = wrap_with_helpers(data, [CompanyHelpers, OfficeHelpers, EmployeeHelpers])
wrapped.offices[0].employees[0].annual_cost  # Works!
```

### Infinite Recursion

Avoid circular references in your data or helpers:

```python
# ❌ Bad - circular reference
data = {"name": "A"}
data["self"] = data  # Don't do this!
```

## Performance Considerations

- **Helper Caching**: Helpers are cached per data object (by `id()`)
- **Lazy Wrapping**: Nested structures are wrapped on access, not upfront
- **SmartDataDict Caching**: SmartDataDict is created once per DictProxy
- **Cached Properties**: Use `@cached_property` for expensive computations

## Comparison with Alternatives

### vs. Dataclasses

| Feature | Data Helpers | Dataclasses |
|---------|--------------|-------------|
| Works with JSON | ✅ Yes | ❌ Requires conversion |
| Dynamic matching | ✅ Yes | ❌ No |
| Nested support | ✅ Automatic | ⚠️ Manual |
| Original data unchanged | ✅ Yes | ❌ Converted |

### vs. Custom Dict Subclass

| Feature | Data Helpers | Dict Subclass |
|---------|--------------|---------------|
| Non-invasive | ✅ Yes | ❌ Requires subclassing |
| Multiple helpers | ✅ Yes | ❌ Single class |
| Auto-detection | ✅ Yes | ❌ Manual |

## License

This feature is part of the pytemplify project and follows the same license.
