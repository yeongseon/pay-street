"""Tests for topic generation and scoring."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from paystreet.app.services.content_engine.templates import (
    TopicParams,
    render_topic_title,
    TOPIC_TEMPLATES,
)
from paystreet.app.services.content_engine.topic_scorer import (
    score_topic,
    score_and_update,
    HIGH_INTEREST_JOBS,
    HIGH_INTEREST_REGIONS,
)
from paystreet.app.models.content import ContentTopic, STATUS_PENDING


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def make_topic(
    job_title: str = "Backend Developer",
    experience_years: int = 3,
    region: str = "Seoul",
    company_size: str = "mid",
) -> ContentTopic:
    return ContentTopic(
        content_type="salary_reveal",
        title="테스트 토픽",
        job_title=job_title,
        experience_years=experience_years,
        region=region,
        company_size=company_size,
        score=0.0,
        status=STATUS_PENDING,
    )


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------


class TestRenderTopicTitle:
    def test_experience_template(self):
        params = TopicParams(
            job_title="Backend Developer",
            experience_years=4,
            region="Seoul",
            company_size="mid",
        )
        title = render_topic_title(TOPIC_TEMPLATES[0], params)
        assert "4년차" in title
        assert "Backend Developer" in title

    def test_region_template(self):
        params = TopicParams(
            job_title="ML Engineer",
            experience_years=3,
            region="Pangyo",
            company_size="large",
        )
        title = render_topic_title(TOPIC_TEMPLATES[1], params)
        assert "Pangyo" in title
        assert "ML Engineer" in title

    def test_range_template(self):
        params = TopicParams(
            job_title="Frontend Developer",
            experience_years=5,
            region="Seoul",
            company_size="startup",
        )
        title = render_topic_title(TOPIC_TEMPLATES[2], params)
        assert "Frontend Developer" in title
        assert "5년차" in title

    def test_missing_optional_job_title_2_does_not_raise(self):
        """Comparison template with no job_title_2 renders empty string, not KeyError."""
        params = TopicParams(
            job_title="DevOps",
            experience_years=4,
            region="Seoul",
            company_size="mid",
        )
        # Template index 3 uses {job_title_2} — should NOT raise
        title = render_topic_title(TOPIC_TEMPLATES[3], params)
        assert "DevOps" in title


# ---------------------------------------------------------------------------
# TopicGenerator (mocked DB)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_topic_generator_creates_topics():
    """TopicGenerator.generate_topics() creates ContentTopic rows and flushes."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()

    from paystreet.app.services.content_engine.topic_generator import TopicGenerator

    gen = TopicGenerator(mock_db)
    topics = await gen.generate_topics(
        job_title="Backend Developer",
        experience_years=4,
        region="Seoul",
        company_size="mid",
    )

    assert len(topics) > 0
    for t in topics:
        assert isinstance(t, ContentTopic)
        assert t.job_title == "Backend Developer"
        assert t.experience_years == 4
        assert t.status == STATUS_PENDING

    mock_db.flush.assert_awaited_once()
    assert mock_db.add.call_count == len(topics)


@pytest.mark.asyncio
async def test_topic_generator_returns_at_most_three_topics():
    """Generator skips comparison template when job_title_2 is missing — ≤3 topics."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()

    from paystreet.app.services.content_engine.topic_generator import TopicGenerator

    gen = TopicGenerator(mock_db)
    topics = await gen.generate_topics(
        job_title="ML Engineer",
        experience_years=2,
        region="Pangyo",
        company_size="large",
    )
    assert 0 < len(topics) <= 3


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------


class TestScoreTopic:
    def test_score_in_valid_range(self):
        topic = make_topic()
        score = score_topic(topic)
        assert 0.0 <= score <= 10.0

    def test_high_interest_job_gets_bonus(self):
        hi_topic = make_topic(job_title="Backend Developer")
        lo_topic = make_topic(job_title="QA Engineer")
        assert score_topic(hi_topic) > score_topic(lo_topic)

    def test_high_interest_region_bonus(self):
        seoul_topic = make_topic(region="Seoul")
        busan_topic = make_topic(region="Busan")
        assert score_topic(seoul_topic) > score_topic(busan_topic)

    def test_large_company_beats_unknown(self):
        large = make_topic(company_size="large")
        unknown = make_topic(company_size="unknown_size")
        assert score_topic(large) >= score_topic(unknown)

    def test_score_and_update_mutates_topic(self):
        topic = make_topic()
        assert topic.score == 0.0
        updated = score_and_update(topic)
        assert updated.score > 0.0
        assert updated is topic  # same object

    def test_sweet_spot_experience(self):
        """5-year experience scores higher than 1-year for same profile."""
        t5 = make_topic(experience_years=5)
        t1 = make_topic(experience_years=1)
        assert score_topic(t5) > score_topic(t1)
