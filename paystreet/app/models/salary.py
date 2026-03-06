# pyright: reportMissingImports=false
"""Salary-related models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from paystreet.app.database import Base
from paystreet.app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class SalaryRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "salary_records"

    job_title: Mapped[str] = mapped_column(String(200), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    company_size: Mapped[str] = mapped_column(String(50), nullable=False)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    salary_min: Mapped[int] = mapped_column(Integer, nullable=False)
    salary_max: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="KRW", nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("salary_min < salary_max", name="ck_salary_min_lt_max"),
        CheckConstraint(
            "salary_max < salary_min * 2", name="ck_salary_range_reasonable"
        ),
        CheckConstraint(
            "experience_years BETWEEN 0 AND 20", name="ck_experience_range"
        ),
        Index(
            "ix_salary_records_lookup",
            "job_title",
            "experience_years",
            "region",
            "company_size",
        ),
    )


class JobTitle(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "job_titles"

    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


class Region(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "regions"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    country: Mapped[str] = mapped_column(String(100), default="Korea", nullable=False)
    region_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
