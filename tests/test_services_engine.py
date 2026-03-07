"""Tests for content engine services: topic_dedup, topic_queue, job_tracker, retry_policy."""

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from paystreet.app.models.content import ContentTopic, STATUS_PENDING, STATUS_QUEUED
from paystreet.app.models.events import JobEvent
from paystreet.app.services.content_engine.topic_dedup import (
    deduplicate_topics,
    is_duplicate,
)
from paystreet.app.services.content_engine.topic_queue import TopicQueue
from paystreet.app.services.job_tracker import JobTracker
from paystreet.app.services.retry_policy import retry_async


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_db(scalar_one_or_none=None, scalars_list=None):
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_one_or_none
    result.scalars.return_value.all.return_value = scalars_list or []
    db.execute = AsyncMock(return_value=result)
    return db


def _make_topic(
    job_title="Backend Developer", exp=3, region="Seoul", company_size="mid"
):
    t = MagicMock(spec=ContentTopic)
    t.id = uuid.uuid4()
    t.content_type = "salary_reveal"
    t.title = f"{exp}yr {job_title} salary"
    t.job_title = job_title
    t.experience_years = exp
    t.region = region
    t.company_size = company_size
    t.score = 0.8
    t.status = STATUS_PENDING
    return t


# ---------------------------------------------------------------------------
# is_duplicate
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_is_duplicate_returns_true_when_exists():
    existing = _make_topic()
    db = _make_db(scalar_one_or_none=existing)

    result = await is_duplicate(db, "Backend Developer", 3, "Seoul", "mid")

    assert result is True
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_is_duplicate_returns_false_when_not_exists():
    db = _make_db(scalar_one_or_none=None)

    result = await is_duplicate(db, "Frontend Developer", 2, "Pangyo", "startup")

    assert result is False


# ---------------------------------------------------------------------------
# deduplicate_topics
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deduplicate_topics_all_unique():
    db = _make_db(scalar_one_or_none=None)  # nothing exists in DB

    topics = [
        _make_topic("Backend Developer", 3, "Seoul", "mid"),
        _make_topic("Frontend Developer", 2, "Pangyo", "startup"),
    ]
    result = await deduplicate_topics(db, topics)

    assert len(result) == 2


@pytest.mark.asyncio
async def test_deduplicate_topics_filters_db_duplicates():
    existing = _make_topic()
    db = _make_db(scalar_one_or_none=existing)  # everything already exists

    topics = [_make_topic("Backend Developer", 3, "Seoul", "mid")]
    result = await deduplicate_topics(db, topics)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_deduplicate_topics_filters_in_batch_duplicates():
    db = _make_db(scalar_one_or_none=None)  # nothing in DB

    # Two topics with identical key — second should be deduped within batch
    t1 = _make_topic("Backend Developer", 3, "Seoul", "mid")
    t2 = _make_topic("Backend Developer", 3, "Seoul", "mid")
    result = await deduplicate_topics(db, [t1, t2])

    assert len(result) == 1


@pytest.mark.asyncio
async def test_deduplicate_topics_keeps_distinct_titles():
    db = _make_db(scalar_one_or_none=None)

    t1 = _make_topic("Backend Developer", 3, "Seoul", "mid")
    t2 = _make_topic("Backend Developer", 3, "Seoul", "mid")
    t1.title = "3년차 백엔드 개발자 연봉 얼마예요"
    t2.title = "서울 백엔드 개발자 연봉 현실"
    t1.content_type = "salary_reveal"
    t2.content_type = "salary_reveal"

    result = await deduplicate_topics(db, [t1, t2])

    assert len(result) == 2


@pytest.mark.asyncio
async def test_deduplicate_topics_empty_list():
    db = _make_db()
    result = await deduplicate_topics(db, [])
    assert result == []


# ---------------------------------------------------------------------------
# TopicQueue
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_topic_queue_enqueue_pending_returns_topics():
    topics = [_make_topic(), _make_topic("ML Engineer", 4, "Pangyo", "large")]
    db = _make_db(scalars_list=topics)

    queue = TopicQueue(db)
    result = await queue.enqueue_pending(limit=5)

    assert len(result) == 2
    # All returned topics should be moved to QUEUED
    for t in result:
        assert t.status == STATUS_QUEUED
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_topic_queue_enqueue_pending_empty():
    db = _make_db(scalars_list=[])

    queue = TopicQueue(db)
    result = await queue.enqueue_pending()

    assert result == []


@pytest.mark.asyncio
async def test_topic_queue_get_queued():
    topics = [_make_topic()]
    db = _make_db(scalars_list=topics)

    queue = TopicQueue(db)
    result = await queue.get_queued(limit=3)

    assert len(result) == 1
    db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_topic_queue_get_queued_empty():
    db = _make_db(scalars_list=[])

    queue = TopicQueue(db)
    result = await queue.get_queued()

    assert result == []


# ---------------------------------------------------------------------------
# JobTracker
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_job_tracker_record_event_returns_job_event():
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()

    tracker = JobTracker(db)
    job_id = uuid.uuid4()
    event = await tracker.record_event(
        job_type="video_pipeline",
        job_id=job_id,
        event_type="started",
        payload={"step": "script_generation"},
    )

    assert isinstance(event, JobEvent)
    assert event.job_type == "video_pipeline"
    assert event.job_id == job_id
    assert event.event_type == "started"
    assert event.payload == {"step": "script_generation"}
    db.add.assert_called_once_with(event)
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_job_tracker_record_event_no_payload():
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()

    tracker = JobTracker(db)
    event = await tracker.record_event(
        job_type="render_job",
        job_id=uuid.uuid4(),
        event_type="completed",
    )

    assert event.payload == {}


@pytest.mark.asyncio
async def test_job_tracker_record_event_multiple():
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()

    tracker = JobTracker(db)
    job_id = uuid.uuid4()

    for event_type in ("started", "script_done", "audio_done", "completed"):
        await tracker.record_event("video_pipeline", job_id, event_type)

    assert db.flush.await_count == 4
    assert db.add.call_count == 4


# ---------------------------------------------------------------------------
# retry_async
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retry_async_succeeds_on_first_attempt():
    call_count = 0

    async def fn():
        nonlocal call_count
        call_count += 1
        return "success"

    result = await retry_async(fn, max_attempts=3, base_delay=0.01)
    assert result == "success"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_async_retries_on_failure():
    call_count = 0

    async def fn():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("transient error")
        return "ok"

    result = await retry_async(fn, max_attempts=3, base_delay=0.01, backoff=1.0)
    assert result == "ok"
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_async_raises_after_all_attempts():
    async def fn():
        raise ConnectionError("network down")

    with pytest.raises(RuntimeError, match="All 3 attempts failed"):
        await retry_async(fn, max_attempts=3, base_delay=0.01, backoff=1.0)


@pytest.mark.asyncio
async def test_retry_async_only_retries_specified_exceptions():
    call_count = 0

    async def fn():
        nonlocal call_count
        call_count += 1
        raise TypeError("unexpected type")

    with pytest.raises(RuntimeError):
        await retry_async(
            fn,
            max_attempts=3,
            base_delay=0.01,
            exceptions=(TypeError,),
        )

    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_async_does_not_retry_non_matching_exception():
    """Exceptions not in the tuple propagate immediately without retry."""

    async def fn():
        raise KeyError("not in exceptions tuple")

    with pytest.raises(KeyError):
        await retry_async(fn, max_attempts=3, base_delay=0.01, exceptions=(ValueError,))


@pytest.mark.asyncio
async def test_retry_async_single_attempt():
    async def fn():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="All 1 attempts failed"):
        await retry_async(fn, max_attempts=1, base_delay=0.01)
