"""Tests for FastAPI API routers: admin, pipeline, salary, scripts, topics, health."""

import uuid
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from paystreet.app.database import get_db
from paystreet.app.main import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_execute_result(scalar=0, scalars_list=None, scalar_one_or_none=None):
    result = MagicMock()
    result.scalar.return_value = scalar
    result.scalars.return_value.all.return_value = scalars_list or []
    result.scalar_one_or_none.return_value = scalar_one_or_none
    return result


def _make_mock_db(scalar=0, scalars_list=None, scalar_one_or_none=None):
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.flush = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.execute = AsyncMock(
        return_value=_make_execute_result(
            scalar=scalar,
            scalars_list=scalars_list,
            scalar_one_or_none=scalar_one_or_none,
        )
    )
    return mock_db


@contextmanager
def _patched_client(db=None):
    """Create a TestClient with patched lifespan (no real DB) and optional DB override."""
    if db is None:
        db = _make_mock_db()

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with (
        patch("paystreet.app.main.init_db", new=AsyncMock()),
        patch("paystreet.app.main.close_db", new=AsyncMock()),
        patch("paystreet.app.main.setup_logging"),
    ):
        with TestClient(app) as c:
            yield c, db
    app.dependency_overrides.clear()


@pytest.fixture()
def client():
    with _patched_client() as (c, db):
        yield c, db


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


def test_health_check(client):
    c, _ = client
    resp = c.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"
    assert body["data"]["version"] == "0.1.0"


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------


def test_admin_stats_returns_counts():
    mock_db = _make_mock_db(scalar=5)
    with _patched_client(mock_db) as (c, _):
        resp = c.get("/api/v1/admin/stats")

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "salary_records" in data
    assert "topics" in data
    assert "scripts" in data
    assert "render_jobs" in data


def test_admin_stats_zero_counts(client):
    c, _ = client
    resp = c.get("/api/v1/admin/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert body["error"] is None
    assert body["success"] is True


# ---------------------------------------------------------------------------
# Topics
# ---------------------------------------------------------------------------


def _make_topic(
    title="Backend Dev 3yr",
    job_title="Backend Developer",
    exp=3,
    region="Seoul",
    score=0.8,
    status="PENDING",
):
    t = MagicMock()
    t.id = uuid.uuid4()
    t.title = title
    t.job_title = job_title
    t.experience_years = exp
    t.region = region
    t.score = score
    t.status = status
    return t


def test_list_topics_empty(client):
    c, _ = client
    resp = c.get("/api/v1/topics/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []


def test_list_topics_returns_items():
    topics = [
        _make_topic(),
        _make_topic(title="FE 2yr", job_title="Frontend Developer", exp=2),
    ]
    db = _make_mock_db(scalars_list=topics)
    with _patched_client(db) as (c, _):
        resp = c.get("/api/v1/topics/")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) == 2
    assert body["data"][0]["job_title"] == "Backend Developer"


def test_list_topics_with_status_filter():
    db = _make_mock_db(scalars_list=[])
    with _patched_client(db) as (c, _):
        resp = c.get("/api/v1/topics/?status=pending")

    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_list_topics_with_limit():
    db = _make_mock_db(scalars_list=[])
    with _patched_client(db) as (c, _):
        resp = c.get("/api/v1/topics/?limit=10")

    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Scripts
# ---------------------------------------------------------------------------


def _make_script(
    script_id=None,
    topic_id=None,
    provider="mock",
    status="COMPLETED",
    content=None,
):
    s = MagicMock()
    s.id = script_id or uuid.uuid4()
    s.topic_id = topic_id or uuid.uuid4()
    s.provider = provider
    s.status = status
    s.content = content or {"hook": "test hook"}
    s.created_at = MagicMock()
    return s


def test_list_scripts_empty(client):
    c, _ = client
    resp = c.get("/api/v1/scripts/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []


def test_list_scripts_returns_items():
    scripts = [_make_script(), _make_script(provider="openai")]
    db = _make_mock_db(scalars_list=scripts)
    with _patched_client(db) as (c, _):
        resp = c.get("/api/v1/scripts/")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) == 2
    assert body["data"][0]["provider"] == "mock"


def test_get_script_by_id_found():
    sid = uuid.uuid4()
    script = _make_script(script_id=sid)
    db = _make_mock_db(scalar_one_or_none=script)
    with _patched_client(db) as (c, _):
        resp = c.get(f"/api/v1/scripts/{sid}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["id"] == str(sid)
    assert body["data"]["status"] == "COMPLETED"


def test_get_script_by_id_not_found():
    db = _make_mock_db(scalar_one_or_none=None)
    with _patched_client(db) as (c, _):
        resp = c.get(f"/api/v1/scripts/{uuid.uuid4()}")

    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert "not found" in body["error"].lower()


def test_get_script_invalid_uuid(client):
    c, _ = client
    resp = c.get("/api/v1/scripts/not-a-uuid")
    assert resp.status_code == 400
    body = resp.json()
    assert body["success"] is False
    assert "Invalid" in body["error"]


# ---------------------------------------------------------------------------
# Salary
# ---------------------------------------------------------------------------


def _make_salary_record():
    r = MagicMock()
    r.id = uuid.uuid4()
    r.job_title = "Backend Developer"
    r.experience_years = 3
    r.region = "Seoul"
    r.company_size = "mid"
    r.salary_min = 4500
    r.salary_max = 6000
    r.currency = "KRW"
    return r


def _make_job_title_obj():
    t = MagicMock()
    t.id = uuid.uuid4()
    t.name = "Backend Developer"
    t.category = "engineering"
    return t


def _make_region_obj():
    r = MagicMock()
    r.id = uuid.uuid4()
    r.name = "Seoul"
    r.country = "Korea"
    return r


def test_list_salary_records_empty(client):
    c, _ = client
    with patch("paystreet.app.api.salary.SalaryRepository") as MockRepo:
        mock_repo = AsyncMock()
        mock_repo.get_salary_records = AsyncMock(return_value=[])
        MockRepo.return_value = mock_repo
        resp = c.get("/api/v1/salary/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []


def test_list_salary_records_with_results():
    records = [_make_salary_record(), _make_salary_record()]
    db = _make_mock_db()
    with _patched_client(db) as (c, _):
        with patch("paystreet.app.api.salary.SalaryRepository") as MockRepo:
            mock_repo = AsyncMock()
            mock_repo.get_salary_records = AsyncMock(return_value=records)
            MockRepo.return_value = mock_repo
            resp = c.get("/api/v1/salary/")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) == 2
    assert body["data"][0]["job_title"] == "Backend Developer"


def test_list_salary_records_with_filters():
    db = _make_mock_db()
    with _patched_client(db) as (c, _):
        with patch("paystreet.app.api.salary.SalaryRepository") as MockRepo:
            mock_repo = AsyncMock()
            mock_repo.get_salary_records = AsyncMock(return_value=[])
            MockRepo.return_value = mock_repo
            resp = c.get(
                "/api/v1/salary/?job_title=Backend+Developer"
                "&region=Seoul&experience_years=3&company_size=mid&limit=10"
            )

    assert resp.status_code == 200
    mock_repo.get_salary_records.assert_called_once_with(
        job_title="Backend Developer",
        experience_years=3,
        region="Seoul",
        company_size="mid",
        limit=10,
    )


def test_list_job_titles():
    titles = [_make_job_title_obj()]
    db = _make_mock_db()
    with _patched_client(db) as (c, _):
        with patch("paystreet.app.api.salary.SalaryRepository") as MockRepo:
            mock_repo = AsyncMock()
            mock_repo.get_all_job_titles = AsyncMock(return_value=titles)
            MockRepo.return_value = mock_repo
            resp = c.get("/api/v1/salary/job-titles")

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) == 1
    assert body["data"][0]["name"] == "Backend Developer"
    assert body["data"][0]["category"] == "engineering"


def test_list_regions():
    regions = [_make_region_obj()]
    db = _make_mock_db()
    with _patched_client(db) as (c, _):
        with patch("paystreet.app.api.salary.SalaryRepository") as MockRepo:
            mock_repo = AsyncMock()
            mock_repo.get_all_regions = AsyncMock(return_value=regions)
            MockRepo.return_value = mock_repo
            resp = c.get("/api/v1/salary/regions")

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"][0]["name"] == "Seoul"
    assert body["data"][0]["country"] == "Korea"


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def test_pipeline_run_success():
    mock_result = {
        "job_id": str(uuid.uuid4()),
        "output_path": "/tmp/output.mp4",
        "status": "completed",
        "duration": 25.0,
    }
    db = _make_mock_db()
    with _patched_client(db) as (c, _):
        with patch("paystreet.app.pipelines.video_pipeline.VideoPipeline") as MockPipeline:
            mock_inst = AsyncMock()
            mock_inst.run = AsyncMock(return_value=mock_result)
            MockPipeline.return_value = mock_inst
            resp = c.post(
                "/api/v1/pipeline/run",
                json={
                    "job_title": "Backend Developer",
                    "experience_years": 3,
                    "region": "Seoul",
                    "company_size": "mid",
                    "template_id": "street_interview_v1",
                },
            )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["status"] == "completed"
    assert body["error"] is None


def test_pipeline_run_uses_default_params():
    mock_result = {
        "job_id": "abc",
        "output_path": "/tmp/x.mp4",
        "status": "completed",
        "duration": 20.0,
    }
    db = _make_mock_db()
    with _patched_client(db) as (c, _):
        with patch("paystreet.app.pipelines.video_pipeline.VideoPipeline") as MockPipeline:
            mock_inst = AsyncMock()
            mock_inst.run = AsyncMock(return_value=mock_result)
            MockPipeline.return_value = mock_inst
            resp = c.post(
                "/api/v1/pipeline/run",
                json={"job_title": "ML Engineer", "experience_years": 5},
            )

    assert resp.status_code == 200
    call_kwargs = mock_inst.run.call_args.kwargs
    assert call_kwargs["region"] == "Seoul"
    assert call_kwargs["company_size"] == "mid"
    assert call_kwargs["template_id"] == "street_interview_v1"


def test_pipeline_run_failure_returns_500():
    db = _make_mock_db()
    with _patched_client(db) as (c, _):
        with patch("paystreet.app.pipelines.video_pipeline.VideoPipeline") as MockPipeline:
            mock_inst = AsyncMock()
            mock_inst.run = AsyncMock(side_effect=RuntimeError("FFmpeg crashed"))
            MockPipeline.return_value = mock_inst
            resp = c.post(
                "/api/v1/pipeline/run",
                json={"job_title": "DevOps", "experience_years": 4},
            )

    assert resp.status_code == 500
    body = resp.json()
    assert body["success"] is False
    assert "FFmpeg crashed" in body["error"]


def test_pipeline_run_missing_required_field(client):
    c, _ = client
    # experience_years is required
    resp = c.post("/api/v1/pipeline/run", json={"job_title": "DevOps"})
    assert resp.status_code == 422
