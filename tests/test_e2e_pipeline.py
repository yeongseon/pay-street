"""End-to-end pipeline tests using mock LLM + TTS providers."""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call

from paystreet.ai.llm import ScriptContent, DialogueLine
from paystreet.ai.providers.mock_llm import MockLLMProvider
from paystreet.ai.providers.mock_tts import MockTTSProvider


# ---------------------------------------------------------------------------
# Mock LLM / TTS providers as standalone units
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mock_llm_returns_script_content():
    provider = MockLLMProvider()
    result = await provider.generate_script("test prompt")
    assert isinstance(result, ScriptContent)
    assert len(result.hook) > 0
    assert len(result.dialogue) >= 2
    assert len(result.outro) > 0


@pytest.mark.asyncio
async def test_mock_tts_creates_wav_file(tmp_path):
    provider = MockTTSProvider()
    output_path = str(tmp_path / "test_audio.wav")
    result = await provider.synthesize(
        text="안녕하세요 테스트입니다",
        output_path=output_path,
        voice="alloy",
    )
    assert os.path.exists(output_path)
    # WAV files start with RIFF header
    with open(output_path, "rb") as f:
        header = f.read(4)
    assert header == b"RIFF"


@pytest.mark.asyncio
async def test_mock_tts_provider_name():
    provider = MockTTSProvider()
    assert provider.provider_name == "mock"


# ---------------------------------------------------------------------------
# Pipeline provider selection
# ---------------------------------------------------------------------------


def test_get_llm_provider_mock():
    from paystreet.app.pipelines.video_pipeline import _get_llm_provider

    provider = _get_llm_provider("mock")
    assert isinstance(provider, MockLLMProvider)


def test_get_llm_provider_unknown_falls_back_to_mock():
    from paystreet.app.pipelines.video_pipeline import _get_llm_provider

    provider = _get_llm_provider("unknown_provider")
    assert isinstance(provider, MockLLMProvider)


def test_get_tts_provider_mock():
    from paystreet.app.pipelines.video_pipeline import _get_tts_provider

    provider = _get_tts_provider("mock")
    assert isinstance(provider, MockTTSProvider)


def test_get_tts_provider_unknown_falls_back_to_mock():
    from paystreet.app.pipelines.video_pipeline import _get_tts_provider

    provider = _get_tts_provider("unknown_provider")
    assert isinstance(provider, MockTTSProvider)


# ---------------------------------------------------------------------------
# Full pipeline: mocked DB + mocked FFmpeg
# ---------------------------------------------------------------------------


def _make_mock_db():
    """Create a fully mocked async SQLAlchemy session.
    Configures execute() to return a result mock that supports .scalars().all().
    """
    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()

    # Configure execute() so that result.scalars().all() returns empty list
    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=execute_result)

    return db


@pytest.mark.asyncio
async def test_video_pipeline_run_with_mock_providers(tmp_path):
    """Full pipeline.run() with mock LLM, mock TTS, and mocked FFmpeg subprocess."""
    from paystreet.app.pipelines.video_pipeline import VideoPipeline

    mock_db = _make_mock_db()

    # Fake settings
    settings = MagicMock()
    settings.llm_provider = "mock"
    settings.tts_provider = "mock"
    settings.llm_model = "mock-model"
    settings.temp_dir = str(tmp_path / "temp")
    settings.output_dir = str(tmp_path / "output")
    settings.assets_dir = str(tmp_path / "assets")
    settings.templates_dir = str(tmp_path / "templates")

    # Ensure dirs exist
    os.makedirs(settings.temp_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)
    os.makedirs(settings.assets_dir, exist_ok=True)

    # Create fake background asset
    bg_dir = tmp_path / "assets" / "backgrounds"
    bg_dir.mkdir(parents=True, exist_ok=True)
    (bg_dir / "default_bg.png").write_bytes(b"fake png")

    # Create fake template
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir(exist_ok=True)
    template_content = """
id: street_interview_v1
resolution:
  width: 1080
  height: 1920
fps: 30
scenes:
  - type: intro
    duration: 2
"""
    (templates_dir / "street_interview_v1.yaml").write_text(template_content)

    with (
        patch(
            "paystreet.app.pipelines.video_pipeline.get_settings", return_value=settings
        ),
        patch("paystreet.app.video.render_engine.get_settings", return_value=settings),
        patch(
            "paystreet.app.video.template_selector.get_settings", return_value=settings
        ),
        patch("paystreet.app.video.render_engine.subprocess.run") as mock_ffmpeg,
    ):
        mock_ffmpeg.return_value = MagicMock(returncode=0, stdout="", stderr="")

        pipeline = VideoPipeline(db=mock_db)
        result = await pipeline.run(
            job_title="Backend Developer",
            experience_years=4,
            region="Seoul",
            company_size="mid",
        )

    # Verify result shape
    assert isinstance(result, dict)
    assert "job_id" in result
    assert "output_path" in result
    assert "status" in result
    assert result["status"] == "completed"
    assert result["output_path"].endswith(".mp4")
    assert result["duration"] > 0


@pytest.mark.asyncio
async def test_video_pipeline_run_status_failed_on_ffmpeg_error(tmp_path):
    """Pipeline marks status=failed when FFmpeg errors, and re-raises."""
    from paystreet.app.pipelines.video_pipeline import VideoPipeline
    import subprocess

    mock_db = _make_mock_db()

    settings = MagicMock()
    settings.llm_provider = "mock"
    settings.tts_provider = "mock"
    settings.llm_model = "mock-model"
    settings.temp_dir = str(tmp_path / "temp")
    settings.output_dir = str(tmp_path / "output")
    settings.assets_dir = str(tmp_path / "assets")
    settings.templates_dir = str(tmp_path / "templates")

    os.makedirs(settings.temp_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)

    # Create template
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir(exist_ok=True)
    (templates_dir / "street_interview_v1.yaml").write_text("id: street_interview_v1\n")

    with (
        patch(
            "paystreet.app.pipelines.video_pipeline.get_settings", return_value=settings
        ),
        patch("paystreet.app.video.render_engine.get_settings", return_value=settings),
        patch(
            "paystreet.app.video.template_selector.get_settings", return_value=settings
        ),
        patch(
            "paystreet.app.video.render_engine.subprocess.run",
            side_effect=FileNotFoundError("ffmpeg not found"),
        ),
    ):
        pipeline = VideoPipeline(db=mock_db)
        with pytest.raises(RuntimeError, match="FFmpeg not found"):
            await pipeline.run(
                job_title="Frontend Developer",
                experience_years=3,
                region="Pangyo",
                company_size="large",
            )


@pytest.mark.asyncio
async def test_video_pipeline_db_flush_called(tmp_path):
    """Pipeline must flush DB at each major step (script, audio, subtitle, render)."""
    from paystreet.app.pipelines.video_pipeline import VideoPipeline

    mock_db = _make_mock_db()

    settings = MagicMock()
    settings.llm_provider = "mock"
    settings.tts_provider = "mock"
    settings.llm_model = "mock-model"
    settings.temp_dir = str(tmp_path / "temp")
    settings.output_dir = str(tmp_path / "output")
    settings.assets_dir = str(tmp_path / "assets")
    settings.templates_dir = str(tmp_path / "templates")

    os.makedirs(settings.temp_dir, exist_ok=True)
    os.makedirs(settings.output_dir, exist_ok=True)

    templates_dir = tmp_path / "templates"
    templates_dir.mkdir(exist_ok=True)
    (templates_dir / "street_interview_v1.yaml").write_text("id: street_interview_v1\n")

    with (
        patch(
            "paystreet.app.pipelines.video_pipeline.get_settings", return_value=settings
        ),
        patch("paystreet.app.video.render_engine.get_settings", return_value=settings),
        patch(
            "paystreet.app.video.template_selector.get_settings", return_value=settings
        ),
        patch("paystreet.app.video.render_engine.subprocess.run") as mock_ffmpeg,
    ):
        mock_ffmpeg.return_value = MagicMock(returncode=0, stdout="", stderr="")

        pipeline = VideoPipeline(db=mock_db)
        await pipeline.run(
            job_title="ML Engineer",
            experience_years=5,
            region="Seoul",
            company_size="large",
        )

    # flush must be called multiple times (topic, script, audio, subtitle, render, final)
    assert mock_db.flush.await_count >= 5


@pytest.mark.asyncio
async def test_video_pipeline_uses_mock_providers_by_default(tmp_path):
    """With llm_provider='mock', pipeline uses MockLLMProvider (no API calls)."""
    from paystreet.app.pipelines.video_pipeline import (
        VideoPipeline,
        _get_llm_provider,
        _get_tts_provider,
    )

    llm = _get_llm_provider("mock")
    tts = _get_tts_provider("mock")

    assert isinstance(llm, MockLLMProvider)
    assert isinstance(tts, MockTTSProvider)

    # Ensure mock LLM generates valid script
    script = await llm.generate_script("prompt")
    assert isinstance(script, ScriptContent)
    assert len(script.dialogue) >= 2

    # Ensure mock TTS writes a WAV file
    out = str(tmp_path / "mock_tts.wav")
    await tts.synthesize(text="테스트", output_path=out, voice="alloy")
    assert os.path.exists(out)
