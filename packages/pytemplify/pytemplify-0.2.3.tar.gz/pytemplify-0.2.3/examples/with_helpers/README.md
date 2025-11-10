# Data Helpers Example - Enhanced Template Capabilities

This example demonstrates how to use **data helpers** to add computed properties and methods to your JSON data without modifying the source data.

## Features Demonstrated

- **Data Helpers** for company, department, and employee data
- **Computed Properties** like `total_employees`, `average_salary`, `years_of_service`
- **Cached Properties** for expensive calculations
- **Helper-to-Helper Communication** across nested data structures
- **Cross-Level Queries** accessing parent and root data
- **YAML Configuration** for helper loading

## Project Structure

```
with_helpers/
├── config.yaml                              # YAML config with data_helpers section
├── data.json                                # Company data
├── templates/
│   ├── company_report.md.j2                # Company-level report
│   ├── _foreach_dept_department.md.j2      # Department reports
│   └── _foreach_emp_employee_card.md.j2    # Employee cards
└── output/                                  # Generated reports
```

```
helpers/
└── company_helpers.py                       # Data helper classes
```

## Running the Example

From the `examples/with_helpers` directory:

```bash
# Using helpers configured in YAML
uv run yagen --config config.yaml --data data.json

# Override with CLI arguments
uv run yagen -c config.yaml -d data.json \
  --helpers "company_helpers.CompanyHelpers" \
  --helper-path "../helpers/"

# Verbose output to see helper loading
uv run yagen -c config.yaml -d data.json -v
```

## Expected Output

```
output/
├── company_report.md
├── departments/
│   ├── Engineering_department.md
│   ├── Sales_department.md
│   └── Marketing_department.md
└── employees/
    ├── Bob Smith_employee_card.md
    ├── Carol White_employee_card.md
    ├── David Brown_employee_card.md
    ├── Frank Miller_employee_card.md
    ├── Grace Lee_employee_card.md
    └── Iris Chen_employee_card.md
```

## Data Helpers Overview

### CompanyHelpers

Adds computed properties to company-level data:

- `total_employees` - Count across all departments
- `total_salary_expense` - Sum of all salaries
- `total_budget` - Sum of all department budgets
- `company_age` - Years since founding
- `average_department_size` - Average employees per department
- `largest_department` - Name of largest department
- `company_summary` - One-line summary

### DepartmentHelpers

Adds computed properties to department data:

- `employee_count` - Number of employees
- `department_salary_expense` - Total salaries in department
- `average_salary` - Average salary in department
- `is_large_department` - Boolean for size classification
- `budget_per_employee` - Budget divided by employee count
- `highest_paid_employee` - Name of highest paid employee
- `manager_name` - Department manager
- `department_summary` - One-line summary

### EmployeeHelpers

Adds computed properties to employee data:

- `annual_cost` - Salary + 30% benefits overhead
- `formatted_salary` - Formatted with $ and commas
- `formatted_annual_cost` - Formatted annual cost
- `years_of_service` - Calculated from start date
- `is_senior` - Boolean for senior positions
- `seniority_level` - Classification (Junior/Mid/Senior/Principal)
- `employee_summary` - One-line summary

## Key Concepts

### 1. Defining Data Helpers

```python
class CompanyHelpers(DataHelper):
    @staticmethod
    def matches(data: dict) -> bool:
        """Check if this helper applies to the data."""
        return "company_name" in data and "departments" in data

    @property
    def total_employees(self) -> int:
        """Computed property accessible in templates."""
        return sum(len(dept._data.get("employees", []))
                  for dept in self._data.departments)
```

### 2. Configuring Helpers in YAML

```yaml
data_helpers:
  helpers:
    - "company_helpers.CompanyHelpers"
    - "company_helpers.DepartmentHelpers"
    - "company_helpers.EmployeeHelpers"
  discovery_paths:
    - "../helpers/"
```

### 3. Using Helpers in Templates

```jinja2
{# Access computed properties directly #}
Total Employees: {{ dd.total_employees }}
Company Age: {{ dd.company_age }} years
Summary: {{ dd.company_summary }}

{# Nested data with helpers #}
{% for dept in dd.departments %}
  Department: {{ dept.department_name }}
  Employee Count: {{ dept.employee_count }}
  Average Salary: {{ dept.average_salary }}

  {% for emp in dept.employees %}
    Employee: {{ emp.name }}
    Annual Cost: {{ emp.formatted_annual_cost }}
    Years of Service: {{ emp.years_of_service }}
    Is Senior: {{ emp.is_senior }}
  {% endfor %}
{% endfor %}
```

### 4. Helper-to-Helper Communication

Helpers automatically wrap nested data, so you can access helper methods across levels:

```python
# In CompanyHelpers
@property
def total_salary_expense(self) -> int:
    total = 0
    for dept in self._data.departments:  # dept has DepartmentHelpers
        for emp in dept._data.employees:  # emp has EmployeeHelpers
            total += emp._data.salary    # Access original data
    return total
```

### 5. Accessing Data in Helpers

- `self._data` - Smart wrapper with nested helpers applied
- `self._raw_data` - Original unwrapped dictionary
- `self._root_data` - Root-level data (for cross-level queries)
- `self._parent_data` - Parent-level data (None at root)

## Helper Loading Methods

### 1. YAML Configuration (Recommended)

```yaml
data_helpers:
  helpers:
    - "module.ClassName"
  discovery_paths:
    - "./helpers/"
```

### 2. CLI Arguments

```bash
yagen -c config.yaml -d data.json \
  --helpers "company_helpers.CompanyHelpers" \
  --helper-path "../helpers/"
```

### 3. Precedence Order

CLI arguments > YAML configuration > Auto-discovery

## Advanced Features

### Cached Properties

For expensive calculations that should only run once:

```python
from functools import cached_property

@cached_property
def expensive_calculation(self):
    # This runs only once and caches the result
    return complex_computation(self._data)
```

### Cross-Level Queries

Access root or parent data from nested helpers:

```python
class EmployeeHelpers(DataHelper):
    @property
    def company_name(self) -> str:
        # Access company name from root data
        return self._root_data.get("company_name", "Unknown")

    @property
    def department_budget(self) -> int:
        # Access parent department's budget
        return self._parent_data.get("budget", 0)
```

### Multiple Helper Classes

You can apply multiple helpers to the same data:

```python
class BaseEmployeeHelpers(DataHelper):
    @staticmethod
    def matches(data: dict) -> bool:
        return "name" in data and "salary" in data

class ExtendedEmployeeHelpers(DataHelper):
    @staticmethod
    def matches(data: dict) -> bool:
        return "name" in data and "performance_rating" in data
```

## Benefits of Data Helpers

✅ **Non-Invasive** - Original data remains unchanged
✅ **Reusable** - Define once, use in all templates
✅ **Testable** - Test helpers independently
✅ **Type-Safe** - Can add type hints to computed properties
✅ **Maintainable** - Centralized business logic
✅ **Composable** - Helpers work together seamlessly

## Next Steps

- Create custom helper classes for your data structures
- Use `@cached_property` for expensive calculations
- Experiment with cross-level queries using `_root_data` and `_parent_data`
- Add custom methods (not just properties) to helpers
- Read the full [DATA_HELPERS.md](../../DATA_HELPERS.md) documentation
