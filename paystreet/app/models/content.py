# pyright: reportMissingImports=false
"""Content pipeline models."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from paystreet.app.database import Base
from paystreet.app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

STATUS_PENDING = "PENDING"
STATUS_QUEUED = "QUEUED"
STATUS_RUNNING = "RUNNING"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"
STATUS_SKIPPED = "SKIPPED"


class ContentTopic(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "content_topics"

    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    job_title: Mapped[str] = mapped_column(String(200), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    company_size: Mapped[str] = mapped_column(String(50), nullable=False)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=STATUS_PENDING, nullable=False
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index("ix_content_topics_type_status", "content_type", "status"),
        Index("ix_content_topics_lookup", "job_title", "experience_years", "region"),
    )


class Script(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "scripts"

    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_topics.id"),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    content: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=STATUS_PENDING, nullable=False
    )


class AudioJob(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "audio_jobs"

    script_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scripts.id"),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=STATUS_PENDING, nullable=False
    )
    interviewer_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    interviewee_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


class SubtitleAsset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "subtitle_assets"

    script_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scripts.id"),
        nullable=False,
    )
    audio_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audio_jobs.id"),
        nullable=False,
    )
    format: Mapped[str] = mapped_column(String(10), default="srt", nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default=STATUS_PENDING, nullable=False
    )


class RenderJob(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "render_jobs"

    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_topics.id"),
        nullable=False,
    )
    script_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scripts.id"),
        nullable=False,
    )
    audio_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audio_jobs.id"),
        nullable=False,
    )
    subtitle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subtitle_assets.id"),
        nullable=True,
    )
    template_id: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=STATUS_PENDING, nullable=False
    )
    output_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
