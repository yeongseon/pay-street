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

DEFAULT_VIDEO_WIDTH = 1080
DEFAULT_VIDEO_HEIGHT = 1920
DEFAULT_FPS = 30


def _resolve_asset(path: str, assets_dir: str) -> str:
    """Resolve asset path - if relative, prepend assets_dir."""
    if os.path.isabs(path):
        return path
    if path.startswith("assets/"):
        return os.path.join(os.path.dirname(assets_dir.rstrip("/")), path)
    return os.path.join(assets_dir, path)


def _escape_filter_path(path: str) -> str:
    normalized = path.replace("\\", "/")
    for old, new in (
        (":", r"\:"),
        ("'", r"\'"),
        (",", r"\,"),
        ("[", r"\["),
        ("]", r"\]"),
    ):
        normalized = normalized.replace(old, new)
    return normalized


def _template_video_settings(template: dict[str, Any]) -> tuple[int, int, int]:
    video = template.get("video", {})
    resolution = video.get("resolution", {})
    width = int(resolution.get("width", DEFAULT_VIDEO_WIDTH))
    height = int(resolution.get("height", DEFAULT_VIDEO_HEIGHT))
    fps = int(video.get("fps", DEFAULT_FPS))
    return width, height, fps


def _extract_background_asset(template: dict[str, Any], assets_dir: str) -> str:
    for scene in template.get("scenes", []):
        for layer in scene.get("layers", []):
            if layer.get("type") == "background" and layer.get("source"):
                return _resolve_asset(str(layer["source"]), assets_dir)
    return _resolve_asset("assets/backgrounds/default_bg.png", assets_dir)


def _extract_logo_asset(
    template: dict[str, Any], assets_dir: str
) -> Optional[str]:
    branding = template.get("branding", {})
    if not branding.get("watermark_enabled"):
        return None
    logo = branding.get("logo")
    if not logo:
        return None
    resolved = _resolve_asset(str(logo), assets_dir)
    return resolved if os.path.exists(resolved) else None


def render_video(
    timeline: Timeline,
    subtitles: list[SubtitleSegment],
    template: dict[str, Any],
    srt_path: Optional[str],
    job_id: str,
) -> str:
    """Render the final mp4 using FFmpeg. Returns output file path."""
    settings = get_settings()
    output_dir = settings.output_dir
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{job_id}.mp4")
    width, height, fps = _template_video_settings(template)
    bg_asset = _extract_background_asset(template, settings.assets_dir)
    logo_asset = _extract_logo_asset(template, settings.assets_dir)

    duration = timeline.total_duration
    if duration < 1.0:
        duration = 10.0

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
        fps=fps,
        width=width,
        height=height,
        logo_asset=logo_asset,
    )

    logger.info(
        "Running FFmpeg for template %s with %s subtitle segments: %s",
        template.get("template_id", template.get("id", "unknown")),
        len(subtitles),
        " ".join(cmd),
    )
    try:
        _ = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        logger.info("FFmpeg completed: %s", output_path)
    except subprocess.CalledProcessError as exc:
        logger.error("FFmpeg failed:\nSTDOUT: %s\nSTDERR: %s", exc.stdout, exc.stderr)
        raise RuntimeError(f"FFmpeg render failed: {exc.stderr[-500:]}") from exc
    except FileNotFoundError as exc:
        raise RuntimeError(
            "FFmpeg not found. Install with your package manager inside the local development environment."
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
    logo_asset: Optional[str] = None,
) -> list[str]:
    """Build FFmpeg command for video rendering."""
    use_subtitles = bool(srt_path and os.path.exists(srt_path))
    use_logo = bool(logo_asset and os.path.exists(logo_asset))
    cmd = ["ffmpeg", "-y", "-loop", "1", "-i", bg_asset]

    next_input_index = 1
    logo_input_index: Optional[int] = None
    if use_logo and logo_asset is not None:
        logo_input_index = next_input_index
        cmd += ["-i", logo_asset]
        next_input_index += 1

    for entry in audio_entries:
        cmd += ["-i", entry.audio_path]

    n_audio = len(audio_entries)
    needs_filter_complex = use_logo or use_subtitles or n_audio > 0

    if not needs_filter_complex:
        cmd += [
            "-vf",
            f"scale={width}:{height},fps={fps}",
            "-t",
            str(duration),
        ]
    else:
        filter_parts: list[str] = []
        video_label = "v0"
        filter_parts.append(f"[0:v]scale={width}:{height},fps={fps}[{video_label}]")

        if logo_input_index is not None:
            overlay_label = "v1"
            filter_parts.append(
                f"[{video_label}][{logo_input_index}:v]overlay=W-w-40:40:format=auto[{overlay_label}]"
            )
            video_label = overlay_label

        if use_subtitles and srt_path is not None:
            subtitle_label = "vout"
            escaped_path = _escape_filter_path(srt_path)
            filter_parts.append(
                f"[{video_label}]subtitles='{escaped_path}'[{subtitle_label}]"
            )
            video_label = subtitle_label

        audio_labels: list[str] = []
        for entry_index, entry in enumerate(audio_entries, start=next_input_index):
            audio_label = f"a{entry_index - next_input_index}"
            delay_ms = max(0, int(round(entry.start_time * 1000)))
            if delay_ms > 0:
                filter_parts.append(
                    f"[{entry_index}:a]adelay={delay_ms}|{delay_ms}[{audio_label}]"
                )
            else:
                filter_parts.append(f"[{entry_index}:a]anull[{audio_label}]")
            audio_labels.append(f"[{audio_label}]")

        if audio_labels:
            mixed_audio_label = "aout"
            filter_parts.append(
                f"{''.join(audio_labels)}amix=inputs={len(audio_labels)}:duration=longest:dropout_transition=0[{mixed_audio_label}]"
            )
            cmd += [
                "-filter_complex",
                ";".join(filter_parts),
                "-map",
                f"[{video_label}]",
                "-map",
                f"[{mixed_audio_label}]",
            ]
        else:
            cmd += ["-filter_complex", ";".join(filter_parts), "-map", f"[{video_label}]"]

        cmd += ["-t", str(duration)]

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
