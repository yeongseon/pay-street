# pyright: reportMissingImports=false
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from paystreet.app.database import get_db
from paystreet.app.models.content import ContentTopic

router = APIRouter()


@router.get("/")
async def list_topics(
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ContentTopic).order_by(ContentTopic.score.desc()).limit(limit)
    if status:
        stmt = stmt.where(ContentTopic.status == status.upper())
    result = await db.execute(stmt)
    topics = result.scalars().all()
    data = [
        {
            "id": str(t.id),
            "title": t.title,
            "job_title": t.job_title,
            "experience_years": t.experience_years,
            "region": t.region,
            "score": t.score,
            "status": t.status,
        }
        for t in topics
    ]
    return {"success": True, "data": data, "error": None}
