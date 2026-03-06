# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false
"""Deduplication logic for content topics."""

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.content import ContentTopic


async def is_duplicate(
    db: AsyncSession,
    job_title: str,
    experience_years: int,
    region: str,
    company_size: str,
) -> bool:
    """Check if a topic with the same key dimensions already exists."""
    stmt = (
        select(ContentTopic)
        .where(
            and_(
                ContentTopic.job_title == job_title,
                ContentTopic.experience_years == experience_years,
                ContentTopic.region == region,
                ContentTopic.company_size == company_size,
            )
        )
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


async def deduplicate_topics(
    db: AsyncSession, topics: list[ContentTopic]
) -> list[ContentTopic]:
    """Filter out topics that are duplicates of existing records. Flush new unique ones."""
    unique = []
    seen = set()
    for topic in topics:
        key = (
            topic.job_title,
            topic.experience_years,
            topic.region,
            topic.company_size,
        )
        if key in seen:
            continue
        exists = await is_duplicate(
            db,
            topic.job_title,
            topic.experience_years,
            topic.region,
            topic.company_size,
        )
        if not exists:
            unique.append(topic)
            seen.add(key)
    return unique
