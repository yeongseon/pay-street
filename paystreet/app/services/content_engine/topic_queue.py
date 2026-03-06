# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false
"""Manage the topic processing queue."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.content import ContentTopic, STATUS_PENDING, STATUS_QUEUED


class TopicQueue:
    _db: AsyncSession

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def enqueue_pending(self, limit: int = 10) -> list[ContentTopic]:
        """Move PENDING topics to QUEUED and return them."""
        stmt = (
            select(ContentTopic)
            .where(ContentTopic.status == STATUS_PENDING)
            .order_by(ContentTopic.score.desc())
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        topics = list(result.scalars().all())
        for topic in topics:
            topic.status = STATUS_QUEUED
        await self._db.flush()
        return topics

    async def get_queued(self, limit: int = 10) -> list[ContentTopic]:
        """Get topics in QUEUED status."""
        stmt = (
            select(ContentTopic)
            .where(ContentTopic.status == STATUS_QUEUED)
            .order_by(ContentTopic.score.desc())
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())
