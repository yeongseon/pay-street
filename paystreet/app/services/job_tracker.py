# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportDeprecated=false
"""Job event tracking for pipeline observability."""

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.events import JobEvent


class JobTracker:
    _db: AsyncSession

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def record_event(
        self,
        job_type: str,
        job_id: uuid.UUID,
        event_type: str,
        payload: Optional[dict[str, object]] = None,
    ) -> JobEvent:
        event = JobEvent(
            job_type=job_type,
            job_id=job_id,
            event_type=event_type,
            payload=payload or {},
        )
        self._db.add(event)
        await self._db.flush()
        return event
