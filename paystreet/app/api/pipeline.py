# pyright: reportMissingImports=false
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from paystreet.app.database import get_db
from paystreet.app.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


class PipelineRunRequest(BaseModel):
    job_title: str
    experience_years: int
    region: str = "Seoul"
    company_size: str = "mid"
    template_id: str = "street_interview_v1"


@router.post("/run")
async def run_pipeline(
    request: PipelineRunRequest,
    db: AsyncSession = Depends(get_db),
):
    from paystreet.app.pipelines.video_pipeline import VideoPipeline

    try:
        pipeline = VideoPipeline(db=db)
        result = await pipeline.run(
            job_title=request.job_title,
            experience_years=request.experience_years,
            region=request.region,
            company_size=request.company_size,
            template_id=request.template_id,
        )
        return {"success": True, "data": result, "error": None}
    except Exception as exc:
        logger.exception("Pipeline run failed")
        return JSONResponse(
            status_code=500,
            content={"success": False, "data": None, "error": str(exc)},
        )
