# pyright: reportMissingImports=false
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from paystreet.app.database import get_db
from paystreet.data.salary_calculator import format_salary_range
from paystreet.data.salary_repository import SalaryRepository

router = APIRouter()


@router.get("/")
async def list_salary_records(
    job_title: Optional[str] = Query(None),
    experience_years: Optional[int] = Query(None),
    region: Optional[str] = Query(None),
    company_size: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    repo = SalaryRepository(db)
    records = await repo.get_salary_records(
        job_title=job_title,
        experience_years=experience_years,
        region=region,
        company_size=company_size,
        limit=limit,
    )
    data = [
        {
            "id": str(r.id),
            "job_title": r.job_title,
            "experience_years": r.experience_years,
            "region": r.region,
            "company_size": r.company_size,
            "salary_range": format_salary_range(r.salary_min, r.salary_max, r.currency),
            "salary_min": r.salary_min,
            "salary_max": r.salary_max,
            "currency": r.currency,
        }
        for r in records
    ]
    return {"success": True, "data": data, "error": None}


@router.get("/job-titles")
async def list_job_titles(db: AsyncSession = Depends(get_db)):
    repo = SalaryRepository(db)
    titles = await repo.get_all_job_titles()
    return {
        "success": True,
        "data": [
            {"id": str(t.id), "name": t.name, "category": t.category} for t in titles
        ],
        "error": None,
    }


@router.get("/regions")
async def list_regions(db: AsyncSession = Depends(get_db)):
    repo = SalaryRepository(db)
    regions = await repo.get_all_regions()
    return {
        "success": True,
        "data": [
            {"id": str(r.id), "name": r.name, "country": r.country} for r in regions
        ],
        "error": None,
    }
