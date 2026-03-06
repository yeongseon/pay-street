"""Async repository for salary data access."""

import uuid
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from paystreet.app.models.salary import SalaryRecord, JobTitle, Region


class SalaryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_salary_records(
        self,
        job_title: str | None = None,
        experience_years: int | None = None,
        region: str | None = None,
        company_size: str | None = None,
        limit: int = 50,
    ) -> list[SalaryRecord]:
        """Query salary records with optional filters."""
        stmt = select(SalaryRecord)
        filters = []
        if job_title:
            filters.append(SalaryRecord.job_title == job_title)
        if experience_years is not None:
            filters.append(SalaryRecord.experience_years == experience_years)
        if region:
            filters.append(SalaryRecord.region == region)
        if company_size:
            filters.append(SalaryRecord.company_size == company_size)
        if filters:
            stmt = stmt.where(and_(*filters))
        stmt = stmt.limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_salary_by_id(self, record_id: uuid.UUID) -> SalaryRecord | None:
        result = await self._session.execute(
            select(SalaryRecord).where(SalaryRecord.id == record_id)
        )
        return result.scalar_one_or_none()

    async def create_salary_record(self, **kwargs) -> SalaryRecord:
        record = SalaryRecord(**kwargs)
        self._session.add(record)
        await self._session.flush()
        return record

    async def get_all_job_titles(self) -> list[JobTitle]:
        result = await self._session.execute(select(JobTitle).order_by(JobTitle.name))
        return list(result.scalars().all())

    async def get_all_regions(self) -> list[Region]:
        result = await self._session.execute(select(Region).order_by(Region.name))
        return list(result.scalars().all())

    async def upsert_job_title(
        self, name: str, category: str | None = None
    ) -> JobTitle:
        result = await self._session.execute(
            select(JobTitle).where(JobTitle.name == name)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        job_title = JobTitle(name=name, category=category)
        self._session.add(job_title)
        await self._session.flush()
        return job_title

    async def upsert_region(self, name: str, country: str = "Korea") -> Region:
        result = await self._session.execute(select(Region).where(Region.name == name))
        existing = result.scalar_one_or_none()
        if existing:
            return existing
        region = Region(name=name, country=country)
        self._session.add(region)
        await self._session.flush()
        return region
