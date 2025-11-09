"""Data Helpers for company data structures.

These helpers add computed properties to company, department, and employee data.
"""

from datetime import datetime
from functools import cached_property
from typing import List

from pytemplify.data_helpers import DataHelper


class CompanyHelpers(DataHelper):
    """Helper for company-level data."""

    @staticmethod
    def matches(data: dict) -> bool:
        """Check if data represents a company."""
        return "company_name" in data and "departments" in data

    @property
    def total_employees(self) -> int:
        """Calculate total employees across all departments."""
        return sum(len(dept._data.get("employees", [])) for dept in self._data.departments)

    @property
    def total_salary_expense(self) -> int:
        """Calculate total salary expense across all departments."""
        total = 0
        for dept in self._data.departments:
            for emp in dept._data.get("employees", []):
                total += emp._data.get("salary", 0)
        return total

    @property
    def total_budget(self) -> int:
        """Calculate total budget across all departments."""
        return sum(dept._data.get("budget", 0) for dept in self._data.departments)

    @property
    def company_age(self) -> int:
        """Calculate company age in years."""
        current_year = datetime.now().year
        return current_year - self._raw_data.get("founded_year", current_year)

    @property
    def average_department_size(self) -> float:
        """Calculate average number of employees per department."""
        if not self._data.departments:
            return 0.0
        return self.total_employees / len(self._data.departments)

    @cached_property
    def largest_department(self) -> str:
        """Get the name of the largest department by employee count."""
        if not self._data.departments:
            return "N/A"
        largest = max(
            self._data.departments,
            key=lambda d: len(d._data.get("employees", [])),
            default=None,
        )
        return largest._data.get("department_name", "N/A") if largest else "N/A"

    @property
    def company_summary(self) -> str:
        """Generate a one-line company summary."""
        return (
            f"{self._data.company_name}: "
            f"{self.total_employees} employees in {len(self._data.departments)} departments, "
            f"founded {self.company_age} years ago"
        )


class DepartmentHelpers(DataHelper):
    """Helper for department-level data."""

    @staticmethod
    def matches(data: dict) -> bool:
        """Check if data represents a department."""
        return "department_name" in data and "employees" in data

    @property
    def employee_count(self) -> int:
        """Get the number of employees in this department."""
        return len(self._data.get("employees", []))

    @property
    def department_salary_expense(self) -> int:
        """Calculate total salary expense for this department."""
        return sum(emp._data.get("salary", 0) for emp in self._data.employees)

    @property
    def average_salary(self) -> float:
        """Calculate average salary in this department."""
        if not self._data.employees:
            return 0.0
        return self.department_salary_expense / self.employee_count

    @property
    def is_large_department(self) -> bool:
        """Check if this is a large department (>5 employees)."""
        return self.employee_count > 5

    @property
    def budget_per_employee(self) -> float:
        """Calculate budget per employee."""
        if self.employee_count == 0:
            return 0.0
        return self._raw_data.get("budget", 0) / self.employee_count

    @cached_property
    def highest_paid_employee(self) -> str:
        """Get the name of the highest paid employee."""
        if not self._data.employees:
            return "N/A"
        highest = max(
            self._data.employees,
            key=lambda e: e._data.get("salary", 0),
            default=None,
        )
        return highest._data.get("name", "N/A") if highest else "N/A"

    @property
    def manager_name(self) -> str:
        """Get the manager's name."""
        return self._raw_data.get("manager", "Unknown")

    @property
    def department_summary(self) -> str:
        """Generate a one-line department summary."""
        return (
            f"{self._data.department_name}: "
            f"{self.employee_count} employees, "
            f"${self.department_salary_expense:,} total compensation"
        )


class EmployeeHelpers(DataHelper):
    """Helper for employee-level data."""

    @staticmethod
    def matches(data: dict) -> bool:
        """Check if data represents an employee."""
        return "name" in data and "salary" in data and "title" in data

    @property
    def annual_cost(self) -> int:
        """Calculate annual cost including benefits (30% overhead)."""
        return int(self._raw_data.get("salary", 0) * 1.3)

    @property
    def formatted_salary(self) -> str:
        """Format salary with currency symbol and commas."""
        return f"${self._raw_data.get('salary', 0):,}"

    @property
    def formatted_annual_cost(self) -> str:
        """Format annual cost with currency symbol and commas."""
        return f"${self.annual_cost:,}"

    @property
    def years_of_service(self) -> float:
        """Calculate years of service based on start date."""
        start_date_str = self._raw_data.get("start_date")
        if not start_date_str:
            return 0.0
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            delta = datetime.now() - start_date
            return round(delta.days / 365.25, 1)
        except ValueError:
            return 0.0

    @property
    def is_senior(self) -> bool:
        """Check if employee is senior level."""
        title = self._raw_data.get("title", "").lower()
        return "senior" in title or "principal" in title or "director" in title

    @property
    def seniority_level(self) -> str:
        """Determine seniority level based on title."""
        title = self._raw_data.get("title", "").lower()
        if "principal" in title or "director" in title:
            return "Principal"
        elif "senior" in title or "lead" in title:
            return "Senior"
        elif "junior" in title:
            return "Junior"
        else:
            return "Mid-Level"

    @property
    def employee_summary(self) -> str:
        """Generate a one-line employee summary."""
        return (
            f"{self._data.name} - {self._data.title} "
            f"({self.years_of_service} years, {self.formatted_salary}/year)"
        )
