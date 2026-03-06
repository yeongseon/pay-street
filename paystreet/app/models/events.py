# pyright: reportMissingImports=false
"""Job event log model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from paystreet.app.database import Base
from paystreet.app.models.base import UUIDPrimaryKeyMixin


class JobEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "job_events"

    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[Optional[dict[str, object]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
