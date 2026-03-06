# pyright: reportMissingImports=false
"""Initial PayStreet schema."""

from collections.abc import Sequence
from typing import Optional, Union

import alembic.op as op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Optional[str] = None
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


def upgrade() -> None:
    op.create_table(
        "salary_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("job_title", sa.String(length=200), nullable=False),
        sa.Column("experience_years", sa.Integer(), nullable=False),
        sa.Column("region", sa.String(length=100), nullable=False),
        sa.Column("company_size", sa.String(length=50), nullable=False),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("salary_min", sa.Integer(), nullable=False),
        sa.Column("salary_max", sa.Integer(), nullable=False),
        sa.Column(
            "currency",
            sa.String(length=10),
            server_default=sa.text("'KRW'"),
            nullable=False,
        ),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column(
            "last_updated",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("salary_min < salary_max", name="ck_salary_min_lt_max"),
        sa.CheckConstraint(
            "salary_max < salary_min * 2", name="ck_salary_range_reasonable"
        ),
        sa.CheckConstraint(
            "experience_years BETWEEN 0 AND 20", name="ck_experience_range"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_salary_records_lookup",
        "salary_records",
        ["job_title", "experience_years", "region", "company_size"],
        unique=False,
    )

    op.create_table(
        "job_titles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "regions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "country",
            sa.String(length=100),
            server_default=sa.text("'Korea'"),
            nullable=False,
        ),
        sa.Column("region_type", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "content_topics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("content_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("job_title", sa.String(length=200), nullable=False),
        sa.Column("experience_years", sa.Integer(), nullable=False),
        sa.Column("region", sa.String(length=100), nullable=False),
        sa.Column("company_size", sa.String(length=50), nullable=False),
        sa.Column("industry", sa.String(length=100), nullable=True),
        sa.Column("score", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'PENDING'"),
            nullable=False,
        ),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_content_topics_type_status",
        "content_topics",
        ["content_type", "status"],
        unique=False,
    )
    op.create_index(
        "ix_content_topics_lookup",
        "content_topics",
        ["job_title", "experience_years", "region"],
        unique=False,
    )

    op.create_table(
        "scripts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("prompt_version", sa.String(length=20), nullable=True),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'PENDING'"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["topic_id"], ["content_topics.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "audio_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("script_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'PENDING'"),
            nullable=False,
        ),
        sa.Column("interviewer_path", sa.String(length=500), nullable=True),
        sa.Column("interviewee_path", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["script_id"], ["scripts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "subtitle_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("script_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("audio_job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "format",
            sa.String(length=10),
            server_default=sa.text("'srt'"),
            nullable=False,
        ),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'PENDING'"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["audio_job_id"], ["audio_jobs.id"]),
        sa.ForeignKeyConstraint(["script_id"], ["scripts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "render_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("topic_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("script_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("audio_job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subtitle_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("template_id", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'PENDING'"),
            nullable=False,
        ),
        sa.Column("output_path", sa.String(length=500), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["audio_job_id"], ["audio_jobs.id"]),
        sa.ForeignKeyConstraint(["script_id"], ["scripts.id"]),
        sa.ForeignKeyConstraint(["subtitle_id"], ["subtitle_assets.id"]),
        sa.ForeignKeyConstraint(["topic_id"], ["content_topics.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "job_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("job_events")
    op.drop_table("render_jobs")
    op.drop_table("subtitle_assets")
    op.drop_table("audio_jobs")
    op.drop_table("scripts")
    op.drop_index("ix_content_topics_lookup", table_name="content_topics")
    op.drop_index("ix_content_topics_type_status", table_name="content_topics")
    op.drop_table("content_topics")
    op.drop_table("regions")
    op.drop_table("job_titles")
    op.drop_index("ix_salary_records_lookup", table_name="salary_records")
    op.drop_table("salary_records")
