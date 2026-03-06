# pyright: reportMissingImports=false
"""SQLAlchemy models — import all to ensure they're registered with Base.metadata."""

from paystreet.app.models.content import (
    AudioJob,
    ContentTopic,
    RenderJob,
    Script,
    SubtitleAsset,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_PENDING,
    STATUS_QUEUED,
    STATUS_RUNNING,
    STATUS_SKIPPED,
)
from paystreet.app.models.events import JobEvent
from paystreet.app.models.salary import JobTitle, Region, SalaryRecord

__all__ = [
    "SalaryRecord",
    "JobTitle",
    "Region",
    "ContentTopic",
    "Script",
    "AudioJob",
    "SubtitleAsset",
    "RenderJob",
    "JobEvent",
    "STATUS_PENDING",
    "STATUS_QUEUED",
    "STATUS_RUNNING",
    "STATUS_COMPLETED",
    "STATUS_FAILED",
    "STATUS_SKIPPED",
]
