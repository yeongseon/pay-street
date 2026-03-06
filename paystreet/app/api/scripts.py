# pyright: reportMissingImports=false
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from paystreet.app.database import get_db
from paystreet.app.models.content import Script

router = APIRouter()


@router.get("/")
async def list_scripts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Script).order_by(Script.created_at.desc()).limit(50)
    )
    scripts = result.scalars().all()
    data = [
        {
            "id": str(s.id),
            "topic_id": str(s.topic_id),
            "provider": s.provider,
            "status": s.status,
            "content": s.content,
        }
        for s in scripts
    ]
    return {"success": True, "data": data, "error": None}


@router.get("/{script_id}")
async def get_script(script_id: str, db: AsyncSession = Depends(get_db)):
    try:
        sid = uuid.UUID(script_id)
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"success": False, "data": None, "error": "Invalid script ID"},
        )

    result = await db.execute(select(Script).where(Script.id == sid))
    script = result.scalar_one_or_none()
    if not script:
        return JSONResponse(
            status_code=404,
            content={"success": False, "data": None, "error": "Script not found"},
        )

    return {
        "success": True,
        "data": {
            "id": str(script.id),
            "content": script.content,
            "status": script.status,
        },
        "error": None,
    }
