# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportDeprecated=false, reportAny=false, reportExplicitAny=false
"""FFmpeg-based video render engine."""

import logging
import os
import subprocess
from typing import Any, Optional

from paystreet.app.config import get_settings
from paystreet.app.video.subtitle_mapper import SubtitleSegment
from paystreet.app.video.timeline_builder import Timeline, TimelineEntry

logger = logging.getLogger(__name__)

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30


def _resolve_asset(path: str, assets_dir: str) -> str:
    """Resolve asset path - if relative, prepend assets_dir."""
    if os.path.isabs(path):
        return path
    if path.startswith("assets/"):
        return os.path.join(os.path.dirname(assets_dir.rstrip("/")), path)
    return os.path.join(assets_dir, path)


def render_video(
    timeline: Timeline,
    subtitles: list[SubtitleSegment],
    template: dict[str, Any],
    srt_path: Optional[str],
    job_id: str,
) -> str:
    """Render the final mp4 using FFmpeg. Returns output file path."""
    _ = subtitles, template
    settings = get_settings()
    output_dir = settings.output_dir
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{job_id}.mp4")
    bg_asset = _resolve_asset("assets/backgrounds/default_bg.png", settings.assets_dir)

    duration = timeline.total_duration
    if duration < 1.0:
        duration = 10.0  # safety minimum

    # Collect audio inputs
    audio_entries = [
        entry
        for entry in timeline.entries
        if entry.audio_path and os.path.exists(entry.audio_path)
    ]

    cmd = _build_ffmpeg_command(
        bg_asset=bg_asset,
        audio_entries=audio_entries,
        duration=duration,
        srt_path=srt_path,
        output_path=output_path,
        fps=FPS,
        width=VIDEO_WIDTH,
        height=VIDEO_HEIGHT,
    )

    logger.info("Running FFmpeg: %s", " ".join(cmd))
    try:
        _ = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        logger.info("FFmpeg completed: %s", output_path)
    except subprocess.CalledProcessError as exc:
        logger.error("FFmpeg failed:\nSTDOUT: %s\nSTDERR: %s", exc.stdout, exc.stderr)
        raise RuntimeError(f"FFmpeg render failed: {exc.stderr[-500:]}") from exc
    except FileNotFoundError as exc:
        raise RuntimeError(
            "FFmpeg not found. Install with: brew install ffmpeg"
        ) from exc

    return output_path


def _build_ffmpeg_command(
    bg_asset: str,
    audio_entries: list[TimelineEntry],
    duration: float,
    srt_path: Optional[str],
    output_path: str,
    fps: int,
    width: int,
    height: int,
) -> list[str]:
    """Build FFmpeg command for video rendering."""
    cmd = ["ffmpeg", "-y"]

    # Background image (loop for the full duration)
    cmd += ["-loop", "1", "-i", bg_asset]

    # Audio inputs
    for entry in audio_entries:
        cmd += ["-i", entry.audio_path]

    n_audio = len(audio_entries)

    if n_audio > 0:
        # Build filter_complex: concat audio + scale video
        filter_parts = []
        # Scale video
        filter_parts.append(f"[0:v]scale={width}:{height},fps={fps}[v]")
        # Concat audio streams
        audio_labels = "".join(f"[{i + 1}:a]" for i in range(n_audio))
        filter_parts.append(f"{audio_labels}concat=n={n_audio}:v=0:a=1[a]")
        filter_complex = ";".join(filter_parts)

        cmd += [
            "-filter_complex",
            filter_complex,
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-t",
            str(duration),
        ]
    else:
        # No audio: just scale and set duration
        cmd += [
            "-vf",
            f"scale={width}:{height},fps={fps}",
            "-t",
            str(duration),
        ]

    if srt_path and os.path.exists(srt_path):
        pass

    # Output codec settings
    cmd += [
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
    ]
    if n_audio > 0:
        cmd += ["-c:a", "aac", "-b:a", "128k"]

    cmd.append(output_path)
    return cmd
