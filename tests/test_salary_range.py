"""Tests for salary range formatting and calculation utilities."""

import pytest
from unittest.mock import MagicMock

from paystreet.data.salary_calculator import (
    format_salary_range,
    compute_midpoint,
    aggregate_salary_range,
    salary_range_for_prompt,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def make_record(salary_min: int, salary_max: int, currency: str = "KRW") -> MagicMock:
    r = MagicMock()
    r.salary_min = salary_min
    r.salary_max = salary_max
    r.currency = currency
    return r


# ---------------------------------------------------------------------------
# format_salary_range
# ---------------------------------------------------------------------------


class TestFormatSalaryRange:
    def test_krw_format(self):
        result = format_salary_range(5000, 7000, "KRW")
        assert "5,000만원" in result
        assert "7,000만원" in result
        assert "~" in result

    def test_default_currency_is_krw(self):
        result = format_salary_range(3000, 4500)
        assert "만원" in result

    def test_non_krw_format_includes_currency(self):
        result = format_salary_range(60000, 80000, "USD")
        assert "USD" in result
        assert "60,000" in result
        assert "80,000" in result

    def test_same_min_max(self):
        result = format_salary_range(6000, 6000)
        assert "6,000만원" in result

    def test_large_values_formatted_with_commas(self):
        result = format_salary_range(10000, 15000)
        assert "10,000만원" in result
        assert "15,000만원" in result


# ---------------------------------------------------------------------------
# compute_midpoint
# ---------------------------------------------------------------------------


class TestComputeMidpoint:
    def test_even_range(self):
        assert compute_midpoint(4000, 6000) == 5000

    def test_odd_range_truncates(self):
        assert compute_midpoint(5000, 6001) == 5500

    def test_same_values(self):
        assert compute_midpoint(5000, 5000) == 5000

    def test_zero_min(self):
        assert compute_midpoint(0, 8000) == 4000


# ---------------------------------------------------------------------------
# aggregate_salary_range
# ---------------------------------------------------------------------------


class TestAggregateSalaryRange:
    def test_empty_returns_none(self):
        assert aggregate_salary_range([]) is None

    def test_single_record(self):
        result = aggregate_salary_range([make_record(5000, 7000)])
        assert result == (5000, 7000)

    def test_multiple_records_min_max(self):
        records = [
            make_record(3000, 5000),
            make_record(4000, 8000),
            make_record(5500, 7000),
        ]
        result = aggregate_salary_range(records)
        assert result == (3000, 8000)

    def test_identical_records(self):
        records = [make_record(6000, 8000), make_record(6000, 8000)]
        assert aggregate_salary_range(records) == (6000, 8000)


# ---------------------------------------------------------------------------
# salary_range_for_prompt
# ---------------------------------------------------------------------------


class TestSalaryRangeForPrompt:
    def test_empty_list_returns_no_info_string(self):
        result = salary_range_for_prompt([])
        assert result == "정보 없음"

    def test_single_record_formats_correctly(self):
        records = [make_record(5000, 7000)]
        result = salary_range_for_prompt(records)
        assert "5,000만원" in result
        assert "7,000만원" in result

    def test_aggregates_across_multiple_records(self):
        records = [make_record(3000, 5000), make_record(6000, 9000)]
        result = salary_range_for_prompt(records)
        assert "3,000만원" in result
        assert "9,000만원" in result

    def test_uses_first_record_currency(self):
        records = [make_record(60000, 80000, "USD"), make_record(50000, 70000, "USD")]
        result = salary_range_for_prompt(records)
        assert "USD" in result
