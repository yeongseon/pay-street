"""Smoke tests for the video rendering pipeline (no FFmpeg required)."""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from paystreet.ai.llm import ScriptContent, DialogueLine
from paystreet.app.video.scene_planner import plan_scenes, SceneSegment, ScenePlan
from paystreet.app.video.timeline_builder import build_timeline, Timeline, TimelineEntry
from paystreet.app.video.subtitle_mapper import map_subtitles, SubtitleSegment
from paystreet.app.video.srt_writer import write_srt, _format_timecode
from paystreet.app.video.render_engine import _build_ffmpeg_command


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_script() -> ScriptContent:
    return ScriptContent(
        hook="4년차 백엔드 개발자 연봉 얼마예요?",
        dialogue=[
            DialogueLine(speaker="interviewer", line="안녕하세요! 무슨 일 하세요?"),
            DialogueLine(
                speaker="interviewee", line="판교에서 백엔드 개발자로 일하고 있습니다."
            ),
            DialogueLine(speaker="interviewer", line="연봉이 어느 정도 되세요?"),
            DialogueLine(speaker="interviewee", line="6천만 원에서 7천만 원 사이예요."),
        ],
        outro="여러분 연봉은 어떤가요? 댓글로 알려주세요!",
    )


# ---------------------------------------------------------------------------
# Scene planner
# ---------------------------------------------------------------------------


class TestScenePlanner:
    def test_plan_scenes_returns_scene_plan(self):
        script = make_script()
        plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
        assert isinstance(plan, ScenePlan)

    def test_always_has_intro_and_outro(self):
        script = make_script()
        plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
        types = [s.scene_type for s in plan.scenes]
        assert "intro" in types
        assert "outro" in types
        assert "highlight" in types

    def test_dialogue_mapped_to_scenes(self):
        script = make_script()
        plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
        dialogue_scenes = [
            s for s in plan.scenes if s.scene_type in ("question", "answer")
        ]
        assert len(dialogue_scenes) == len(script.dialogue)

    def test_speaker_assigned_to_dialogue_scenes(self):
        script = make_script()
        plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
        for scene in plan.scenes:
            if scene.scene_type == "question":
                assert scene.speaker == "interviewer"
            elif scene.scene_type == "answer":
                assert scene.speaker == "interviewee"

    def test_intro_has_fixed_duration(self):
        script = make_script()
        plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
        intro = next(s for s in plan.scenes if s.scene_type == "intro")
        assert intro.duration == 2.0

    def test_highlight_contains_salary_range(self):
        salary = "6,000만원 ~ 7,000만원"
        script = make_script()
        plan = plan_scenes(script, salary)
        highlight = next(s for s in plan.scenes if s.scene_type == "highlight")
        assert salary in highlight.content


# ---------------------------------------------------------------------------
# Timeline builder
# ---------------------------------------------------------------------------


class TestTimelineBuilder:
    def test_build_timeline_from_plan(self):
        script = make_script()
        plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
        timeline = build_timeline(plan)
        assert isinstance(timeline, Timeline)
        assert len(timeline.entries) == len(plan.scenes)

    def test_entries_have_sequential_timestamps(self):
        script = make_script()
        plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
        timeline = build_timeline(plan)
        for i in range(1, len(timeline.entries)):
            prev = timeline.entries[i - 1]
            curr = timeline.entries[i]
            assert abs(curr.start_time - prev.end_time) < 0.001

    def test_total_duration_matches_sum(self):
        script = make_script()
        plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
        timeline = build_timeline(plan)
        expected = sum(e.duration for e in timeline.entries)
        assert abs(timeline.total_duration - expected) < 0.01

    def test_duration_clamped_to_min(self):
        """Scenes with 0 duration get at least the minimum for their type."""
        script = make_script()
        plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
        timeline = build_timeline(plan)
        for entry in timeline.entries:
            assert entry.duration >= 1.0

    def test_start_time_begins_at_zero(self):
        script = make_script()
        plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
        timeline = build_timeline(plan)
        assert timeline.entries[0].start_time == 0.0


# ---------------------------------------------------------------------------
# Subtitle mapper
# ---------------------------------------------------------------------------


class TestSubtitleMapper:
    def test_produces_subtitle_segments(self):
        script = make_script()
        plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
        timeline = build_timeline(plan)
        segments = map_subtitles(timeline)
        assert len(segments) > 0
        assert all(isinstance(s, SubtitleSegment) for s in segments)

    def test_indices_are_sequential(self):
        script = make_script()
        plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
        timeline = build_timeline(plan)
        segments = map_subtitles(timeline)
        for i, seg in enumerate(segments, start=1):
            assert seg.index == i

    def test_all_segments_have_text(self):
        script = make_script()
        plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
        timeline = build_timeline(plan)
        segments = map_subtitles(timeline)
        for seg in segments:
            assert len(seg.text.strip()) > 0

    def test_salary_segment_marked_highlight(self):
        salary = "6,000만원 ~ 7,000만원"
        script = make_script()
        plan = plan_scenes(script, salary)
        timeline = build_timeline(plan)
        segments = map_subtitles(timeline)
        highlight_segs = [s for s in segments if s.highlight]
        assert len(highlight_segs) > 0

    def test_no_overlapping_timestamps(self):
        script = make_script()
        plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
        timeline = build_timeline(plan)
        segments = map_subtitles(timeline)
        for i in range(1, len(segments)):
            assert segments[i].start_time >= segments[i - 1].end_time - 0.001


# ---------------------------------------------------------------------------
# SRT writer
# ---------------------------------------------------------------------------


class TestSrtWriter:
    def test_format_timecode_zero(self):
        assert _format_timecode(0.0) == "00:00:00,000"

    def test_format_timecode_minutes(self):
        assert _format_timecode(90.5) == "00:01:30,500"

    def test_format_timecode_hours(self):
        assert _format_timecode(3661.1) == "01:01:01,100"

    def test_write_srt_creates_file(self):
        segments = [
            SubtitleSegment(index=1, start_time=0.0, end_time=2.0, text="안녕하세요"),
            SubtitleSegment(index=2, start_time=2.1, end_time=4.0, text="반갑습니다"),
        ]
        with tempfile.NamedTemporaryFile(suffix=".srt", delete=False) as f:
            path = f.name
        try:
            result = write_srt(segments, path)
            assert result == path
            assert os.path.exists(path)
            content = open(path, encoding="utf-8").read()
            assert "안녕하세요" in content
            assert "반갑습니다" in content
            assert "-->" in content
        finally:
            os.unlink(path)

    def test_srt_format_has_blank_lines_between_entries(self):
        segments = [
            SubtitleSegment(index=1, start_time=0.0, end_time=1.0, text="첫 번째"),
            SubtitleSegment(index=2, start_time=1.1, end_time=2.0, text="두 번째"),
        ]
        with tempfile.NamedTemporaryFile(suffix=".srt", delete=False, mode="w") as f:
            path = f.name
        try:
            write_srt(segments, path)
            content = open(path, encoding="utf-8").read()
            # SRT entries separated by blank lines
            assert "\n\n" in content
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# FFmpeg command builder (no FFmpeg installed required)
# ---------------------------------------------------------------------------


class TestBuildFfmpegCommand:
    def test_command_starts_with_ffmpeg(self):
        cmd = _build_ffmpeg_command(
            bg_asset="/fake/bg.png",
            audio_entries=[],
            duration=20.0,
            srt_path=None,
            output_path="/tmp/out.mp4",
            fps=30,
            width=1080,
            height=1920,
        )
        assert cmd[0] == "ffmpeg"
        assert "-y" in cmd

    def test_command_includes_output_path(self):
        cmd = _build_ffmpeg_command(
            bg_asset="/fake/bg.png",
            audio_entries=[],
            duration=20.0,
            srt_path=None,
            output_path="/tmp/test_output.mp4",
            fps=30,
            width=1080,
            height=1920,
        )
        assert "/tmp/test_output.mp4" == cmd[-1]

    def test_command_uses_libx264(self):
        cmd = _build_ffmpeg_command(
            bg_asset="/fake/bg.png",
            audio_entries=[],
            duration=20.0,
            srt_path=None,
            output_path="/tmp/out.mp4",
            fps=30,
            width=1080,
            height=1920,
        )
        assert "libx264" in cmd

    def test_command_sets_yuv420p(self):
        cmd = _build_ffmpeg_command(
            bg_asset="/fake/bg.png",
            audio_entries=[],
            duration=20.0,
            srt_path=None,
            output_path="/tmp/out.mp4",
            fps=30,
            width=1080,
            height=1920,
        )
        assert "yuv420p" in cmd

    def test_command_includes_background_image(self):
        cmd = _build_ffmpeg_command(
            bg_asset="/fake/bg.png",
            audio_entries=[],
            duration=20.0,
            srt_path=None,
            output_path="/tmp/out.mp4",
            fps=30,
            width=1080,
            height=1920,
        )
        assert "/fake/bg.png" in cmd
        assert "-loop" in cmd

    def test_command_with_audio_uses_filter_complex(self):
        mock_entry = MagicMock()
        mock_entry.audio_path = "/tmp/audio.wav"
        cmd = _build_ffmpeg_command(
            bg_asset="/fake/bg.png",
            audio_entries=[mock_entry],
            duration=20.0,
            srt_path=None,
            output_path="/tmp/out.mp4",
            fps=30,
            width=1080,
            height=1920,
        )
        assert "-filter_complex" in cmd
        assert "-c:a" in cmd
        assert "aac" in cmd

    def test_command_no_audio_uses_vf(self):
        cmd = _build_ffmpeg_command(
            bg_asset="/fake/bg.png",
            audio_entries=[],
            duration=20.0,
            srt_path=None,
            output_path="/tmp/out.mp4",
            fps=30,
            width=1080,
            height=1920,
        )
        assert "-vf" in cmd
        assert "-filter_complex" not in cmd


# ---------------------------------------------------------------------------
# render_video: mock subprocess
# ---------------------------------------------------------------------------


def test_render_video_calls_ffmpeg(tmp_path):
    """render_video() assembles correct args and calls subprocess.run."""
    from paystreet.app.video.render_engine import render_video

    script = make_script()
    plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
    timeline = build_timeline(plan)
    subtitles = map_subtitles(timeline)

    template = {
        "id": "street_interview_v1",
        "resolution": {"width": 1080, "height": 1920},
    }

    with (
        patch("paystreet.app.video.render_engine.subprocess.run") as mock_run,
        patch("paystreet.app.video.render_engine.get_settings") as mock_settings,
    ):
        settings = MagicMock()
        settings.output_dir = str(tmp_path)
        settings.assets_dir = str(tmp_path)
        settings.temp_dir = str(tmp_path)
        mock_settings.return_value = settings

        # Create a fake background PNG so path exists
        bg_path = tmp_path / "backgrounds" / "default_bg.png"
        bg_path.parent.mkdir(parents=True, exist_ok=True)
        bg_path.write_bytes(b"fake png")

        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        output_path = render_video(
            timeline=timeline,
            subtitles=subtitles,
            template=template,
            srt_path=None,
            job_id="test-job-001",
        )

    assert mock_run.called
    ffmpeg_cmd = mock_run.call_args[0][0]
    assert "ffmpeg" in ffmpeg_cmd[0]
    assert output_path.endswith(".mp4")
    assert "test-job-001" in output_path


def test_render_video_raises_on_ffmpeg_not_found(tmp_path):
    """render_video() raises RuntimeError when FFmpeg is not installed."""
    import subprocess
    from paystreet.app.video.render_engine import render_video

    script = make_script()
    plan = plan_scenes(script, "6,000만원 ~ 7,000만원")
    timeline = build_timeline(plan)
    subtitles = map_subtitles(timeline)
    template = {}

    with (
        patch(
            "paystreet.app.video.render_engine.subprocess.run",
            side_effect=FileNotFoundError("ffmpeg not found"),
        ),
        patch("paystreet.app.video.render_engine.get_settings") as mock_settings,
    ):
        settings = MagicMock()
        settings.output_dir = str(tmp_path)
        settings.assets_dir = str(tmp_path)
        mock_settings.return_value = settings

        with pytest.raises(RuntimeError, match="FFmpeg not found"):
            render_video(
                timeline=timeline,
                subtitles=subtitles,
                template=template,
                srt_path=None,
                job_id="test-job-002",
            )
