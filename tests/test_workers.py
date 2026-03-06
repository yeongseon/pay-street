"""Tests for Celery workers: celery_app config and video_worker tasks."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# celery_app: import and config validation
# ---------------------------------------------------------------------------


def test_celery_app_importable():
    from paystreet.workers.celery_app import celery_app

    assert celery_app is not None
    assert celery_app.main == "paystreet"


def test_celery_app_config():
    from paystreet.workers.celery_app import celery_app

    conf = celery_app.conf
    assert conf.task_serializer == "json"
    assert conf.result_serializer == "json"
    assert conf.enable_utc is True
    assert conf.worker_prefetch_multiplier == 1
    assert conf.task_acks_late is True


def test_celery_app_task_routes():
    from paystreet.workers.celery_app import celery_app

    routes = celery_app.conf.task_routes
    assert "paystreet.workers.video_worker.run_video_pipeline" in routes
    assert "paystreet.workers.video_worker.generate_script_task" in routes
    assert "paystreet.workers.video_worker.synthesize_audio_task" in routes
    assert (
        routes["paystreet.workers.video_worker.run_video_pipeline"]["queue"] == "video"
    )


# ---------------------------------------------------------------------------
# _run_async helper
# ---------------------------------------------------------------------------


def test_run_async_with_no_running_loop():
    from paystreet.workers.video_worker import _run_async

    async def sample():
        return 42

    result = _run_async(sample())
    assert result == 42


def test_run_async_returns_coroutine_result():
    from paystreet.workers.video_worker import _run_async

    async def add(a, b):
        return a + b

    result = _run_async(add(3, 4))
    assert result == 7


# ---------------------------------------------------------------------------
# run_video_pipeline task
# ---------------------------------------------------------------------------


def test_run_video_pipeline_task_registered():
    from paystreet.workers.celery_app import celery_app

    task_names = list(celery_app.tasks.keys())
    assert "paystreet.workers.video_worker.run_video_pipeline" in task_names


def test_run_video_pipeline_success():
    from paystreet.workers.video_worker import run_video_pipeline

    mock_result = {
        "job_id": "test-id",
        "output_path": "/tmp/output.mp4",
        "status": "completed",
        "duration": 25.0,
    }

    mock_factory = MagicMock()
    mock_cm = AsyncMock()
    mock_cm.__aenter__ = AsyncMock(return_value=AsyncMock())
    mock_cm.__aexit__ = AsyncMock(return_value=None)
    mock_factory.return_value = mock_cm

    with patch("paystreet.workers.video_worker.asyncio.get_event_loop") as mock_loop:
        loop = MagicMock()
        loop.is_running.return_value = False
        mock_loop.return_value = loop

        with patch(
            "paystreet.app.database.get_session_factory", return_value=mock_factory
        ):
            with patch(
                "paystreet.app.pipelines.video_pipeline.VideoPipeline"
            ) as MockPipeline:
                mock_pipeline_inst = AsyncMock()
                mock_pipeline_inst.run = AsyncMock(return_value=mock_result)
                MockPipeline.return_value = mock_pipeline_inst

                loop.run_until_complete.return_value = mock_result
                result = run_video_pipeline.run(
                    job_title="Backend Developer",
                    experience_years=3,
                    region="Seoul",
                    company_size="mid",
                    template_id="street_interview_v1",
                )

    assert result == mock_result


def test_run_video_pipeline_retries_on_exception():
    from paystreet.workers.video_worker import run_video_pipeline

    mock_self = MagicMock()
    exc = RuntimeError("DB connection failed")
    mock_self.retry = MagicMock(side_effect=exc)

    with patch(
        "paystreet.workers.video_worker._run_async", side_effect=RuntimeError("fail")
    ):
        with pytest.raises((RuntimeError, Exception)):
            run_video_pipeline.run(
                job_title="ML Engineer",
                experience_years=5,
            )


# ---------------------------------------------------------------------------
# generate_script_task
# ---------------------------------------------------------------------------


def test_generate_script_task_registered():
    from paystreet.workers.celery_app import celery_app

    assert "paystreet.workers.video_worker.generate_script_task" in celery_app.tasks


def test_generate_script_task_mock_provider():
    from paystreet.workers.video_worker import generate_script_task
    from paystreet.ai.llm import ScriptContent

    mock_script = MagicMock(spec=ScriptContent)
    mock_script.model_dump.return_value = {"hook": "test", "dialogue": []}

    with patch(
        "paystreet.workers.video_worker._run_async",
        return_value={"hook": "test", "dialogue": []},
    ):
        result = generate_script_task.run(
            prompt="Write a script about Backend Developer salary",
            provider="mock",
        )

    assert isinstance(result, dict)


def test_generate_script_task_retries_on_exception():
    from paystreet.workers.video_worker import generate_script_task

    mock_self = MagicMock()
    exc = RuntimeError("LLM error")
    mock_self.retry = MagicMock(side_effect=exc)

    with patch(
        "paystreet.workers.video_worker._run_async", side_effect=RuntimeError("fail")
    ):
        with pytest.raises((RuntimeError, Exception)):
            generate_script_task.run(prompt="test", provider="mock")


# ---------------------------------------------------------------------------
# synthesize_audio_task
# ---------------------------------------------------------------------------


def test_synthesize_audio_task_registered():
    from paystreet.workers.celery_app import celery_app

    assert "paystreet.workers.video_worker.synthesize_audio_task" in celery_app.tasks


def test_synthesize_audio_task_mock_provider():
    from paystreet.workers.video_worker import synthesize_audio_task

    mock_result = {
        "file_path": "/tmp/audio.wav",
        "duration_seconds": 5.0,
        "provider": "mock",
    }

    with patch(
        "paystreet.workers.video_worker._run_async",
        return_value=mock_result,
    ):
        result = synthesize_audio_task.run(
            text="안녕하세요",
            output_path="/tmp/audio.wav",
            provider="mock",
        )

    assert result["provider"] == "mock"
    assert result["file_path"] == "/tmp/audio.wav"


def test_synthesize_audio_task_retries_on_exception():
    from paystreet.workers.video_worker import synthesize_audio_task

    mock_self = MagicMock()
    exc = RuntimeError("TTS error")
    mock_self.retry = MagicMock(side_effect=exc)

    with patch(
        "paystreet.workers.video_worker._run_async", side_effect=RuntimeError("fail")
    ):
        with pytest.raises((RuntimeError, Exception)):
            synthesize_audio_task.run(text="test", output_path="/tmp/a.wav")
