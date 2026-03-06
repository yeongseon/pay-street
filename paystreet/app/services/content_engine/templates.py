# pyright: reportDeprecated=false
"""Topic title templates for content generation."""

from dataclasses import dataclass
from typing import Optional

TOPIC_TEMPLATES = [
    "{experience}년차 {job_title} 연봉 얼마예요",
    "{region} {job_title} 연봉 현실",
    "{job_title} {experience}년차 연봉 범위",
    "{job_title} vs {job_title_2} 연봉 비교",
]


@dataclass
class TopicParams:
    job_title: str
    experience_years: int
    region: str
    company_size: str
    industry: Optional[str] = None
    job_title_2: Optional[str] = None  # for comparison template


def render_topic_title(template: str, params: TopicParams) -> str:
    """Render a topic title from a template and params."""
    return template.format(
        job_title=params.job_title,
        experience=params.experience_years,
        region=params.region,
        company_size=params.company_size,
        job_title_2=params.job_title_2 or "",
    )
