"""Seed database with initial Korean IT salary data."""

import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from paystreet.app.database import get_session_factory, get_engine
from paystreet.app.models import SalaryRecord, JobTitle, Region
from paystreet.data.salary_repository import SalaryRepository

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Seed salary data: (job_title, experience_years, region, company_size, salary_min, salary_max)
SEED_SALARY_DATA = [
    # Backend Developers
    ("Backend Developer", 1, "Seoul", "startup", 3000, 4500),
    ("Backend Developer", 3, "Seoul", "mid", 4500, 6000),
    ("Backend Developer", 4, "Pangyo", "mid", 5500, 7000),
    ("Backend Developer", 5, "Pangyo", "large", 6500, 8500),
    ("Backend Developer", 7, "Seoul", "large", 8000, 11000),
    # Frontend Developers
    ("Frontend Developer", 2, "Seoul", "startup", 3500, 5000),
    ("Frontend Developer", 4, "Pangyo", "mid", 5000, 7000),
    ("Frontend Developer", 6, "Seoul", "large", 7000, 9500),
    # Data / ML
    ("Data Engineer", 3, "Seoul", "mid", 5000, 7000),
    ("ML Engineer", 4, "Pangyo", "large", 7000, 10000),
    # PM / Design
    ("Product Manager", 5, "Seoul", "mid", 6000, 8500),
    ("Designer", 3, "Seoul", "startup", 3500, 5000),
    # Infrastructure / QA
    ("DevOps", 4, "Seoul", "mid", 6000, 8000),
    ("iOS Developer", 3, "Seoul", "mid", 5000, 7000),
    ("Android Developer", 3, "Pangyo", "mid", 5000, 7000),
    ("QA Engineer", 3, "Busan", "mid", 3500, 5000),
]

JOB_TITLE_CATEGORIES = {
    "Backend Developer": "engineering",
    "Frontend Developer": "engineering",
    "Data Engineer": "data",
    "ML Engineer": "data",
    "Product Manager": "product",
    "Designer": "design",
    "DevOps": "infrastructure",
    "iOS Developer": "mobile",
    "Android Developer": "mobile",
    "QA Engineer": "quality",
}

SEED_REGIONS = [
    {"name": "Seoul", "country": "Korea", "region_type": "city"},
    {"name": "Pangyo", "country": "Korea", "region_type": "district"},
    {"name": "Busan", "country": "Korea", "region_type": "city"},
]


async def seed(session: AsyncSession) -> None:
    repo = SalaryRepository(session)

    # Insert regions
    logger.info("Seeding regions...")
    for r in SEED_REGIONS:
        await repo.upsert_region(name=r["name"], country=r["country"])
    logger.info(f"  {len(SEED_REGIONS)} regions done")

    # Insert job titles
    logger.info("Seeding job titles...")
    unique_titles = set(row[0] for row in SEED_SALARY_DATA)
    for title in unique_titles:
        category = JOB_TITLE_CATEGORIES.get(title)
        await repo.upsert_job_title(name=title, category=category)
    logger.info(f"  {len(unique_titles)} job titles done")

    # Insert salary records
    logger.info("Seeding salary records...")
    for i, (
        job_title,
        experience_years,
        region,
        company_size,
        salary_min,
        salary_max,
    ) in enumerate(SEED_SALARY_DATA):
        await repo.create_salary_record(
            job_title=job_title,
            experience_years=experience_years,
            region=region,
            company_size=company_size,
            salary_min=salary_min,
            salary_max=salary_max,
            currency="KRW",
            source="seed_data",
        )
    logger.info(f"  {len(SEED_SALARY_DATA)} salary records done")

    await session.commit()
    logger.info("Seed complete.")


async def main() -> None:
    logger.info("Starting PayStreet seed data import...")
    factory = get_session_factory()
    async with factory() as session:
        await seed(session)


if __name__ == "__main__":
    asyncio.run(main())
