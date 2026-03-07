"""PayStreet FastAPI application."""

# pyright: reportMissingImports=false
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from paystreet.app.database import close_db, init_db
from paystreet.app.logging_config import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging()
    logger.info("PayStreet API starting up")
    await init_db()
    yield
    await close_db()
    logger.info("PayStreet API shut down")


app = FastAPI(
    title="PayStreet API",
    version="0.1.0",
    description="AI-powered salary content pipeline",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from paystreet.app.api.admin import router as admin_router
from paystreet.app.api.api_keys import router as api_keys_router
from paystreet.app.api.pipeline import router as pipeline_router
from paystreet.app.api.salary import router as salary_router
from paystreet.app.api.scripts import router as scripts_router
from paystreet.app.api.topics import router as topics_router

app.include_router(salary_router, prefix="/api/v1/salary", tags=["salary"])
app.include_router(topics_router, prefix="/api/v1/topics", tags=["topics"])
app.include_router(scripts_router, prefix="/api/v1/scripts", tags=["scripts"])
app.include_router(pipeline_router, prefix="/api/v1/pipeline", tags=["pipeline"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(api_keys_router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/health")
async def health_check():
    return {
        "success": True,
        "data": {"status": "ok", "version": "0.1.0"},
        "error": None,
    }
