# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportDeprecated=false
"""Generate content topics from salary data."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ...models.content import ContentTopic, STATUS_PENDING
from .templates import (
    TOPIC_TEMPLATES,
    TopicParams,
    render_topic_title,
)
from ....data.salary_repository import SalaryRepository


class TopicGenerator:
    _db: AsyncSession
    _repo: SalaryRepository

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = SalaryRepository(db)

    async def generate_topics(
        self,
        job_title: str,
        experience_years: int,
        region: str,
        company_size: str = "mid",
        industry: Optional[str] = None,
        content_type: str = "salary_reveal",
    ) -> list[ContentTopic]:
        """Generate ContentTopic rows from a salary data combination."""
        params = TopicParams(
            job_title=job_title,
            experience_years=experience_years,
            region=region,
            company_size=company_size,
            industry=industry,
        )
        topics = []
        for template in TOPIC_TEMPLATES[:3]:  # skip comparison for now
            try:
                title = render_topic_title(template, params)
            except KeyError:
                continue
            topic = ContentTopic(
                content_type=content_type,
                title=title,
                job_title=job_title,
                experience_years=experience_years,
                region=region,
                company_size=company_size,
                industry=industry,
                score=0.0,
                status=STATUS_PENDING,
            )
            self._db.add(topic)
            topics.append(topic)
        await self._db.flush()
        return topics
