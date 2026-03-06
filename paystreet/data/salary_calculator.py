"""Salary range formatting and calculation utilities."""

from paystreet.app.models.salary import SalaryRecord


def format_salary_range(salary_min: int, salary_max: int, currency: str = "KRW") -> str:
    """Format salary range as a human-readable Korean string.

    Example: format_salary_range(5000, 7000) -> "5,000만원 ~ 7,000만원"
    """
    if currency == "KRW":
        return f"{salary_min:,}만원 ~ {salary_max:,}만원"
    return f"{salary_min:,} ~ {salary_max:,} {currency}"


def compute_midpoint(salary_min: int, salary_max: int) -> int:
    """Return the midpoint of a salary range."""
    return (salary_min + salary_max) // 2


def aggregate_salary_range(records: list[SalaryRecord]) -> tuple[int, int] | None:
    """Given multiple salary records, return the overall min/max range.

    Returns None if no records provided.
    """
    if not records:
        return None
    overall_min = min(r.salary_min for r in records)
    overall_max = max(r.salary_max for r in records)
    return overall_min, overall_max


def salary_range_for_prompt(records: list[SalaryRecord]) -> str:
    """Format aggregated salary range string suitable for use in LLM prompt."""
    result = aggregate_salary_range(records)
    if result is None:
        return "정보 없음"
    salary_min, salary_max = result
    currency = records[0].currency if records else "KRW"
    return format_salary_range(salary_min, salary_max, currency)
