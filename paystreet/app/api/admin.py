# pyright: reportMissingImports=false
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from paystreet.app.database import get_db
from paystreet.app.models.content import ContentTopic, RenderJob, Script
from paystreet.app.models.salary import SalaryRecord

router = APIRouter()


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    salary_count = (
        await db.execute(select(func.count()).select_from(SalaryRecord))
    ).scalar()
    topic_count = (
        await db.execute(select(func.count()).select_from(ContentTopic))
    ).scalar()
    script_count = (await db.execute(select(func.count()).select_from(Script))).scalar()
    render_count = (
        await db.execute(select(func.count()).select_from(RenderJob))
    ).scalar()
    return {
        "success": True,
        "data": {
            "salary_records": salary_count,
            "topics": topic_count,
            "scripts": script_count,
            "render_jobs": render_count,
        },
        "error": None,
    }
