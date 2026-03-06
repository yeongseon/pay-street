# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false
"""Write SRT subtitle files."""

from paystreet.app.video.subtitle_mapper import SubtitleSegment


def _format_timecode(seconds: float) -> str:
    """Convert seconds to SRT timecode HH:MM:SS,mmm."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds % 1) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(segments: list[SubtitleSegment], output_path: str) -> str:
    """Write subtitle segments to SRT file. Returns the file path."""
    import os

    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(
        output_path
    ) else None

    lines = []
    for seg in segments:
        lines.append(str(seg.index))
        lines.append(
            f"{_format_timecode(seg.start_time)} --> {_format_timecode(seg.end_time)}"
        )
        lines.append(seg.text)
        lines.append("")  # blank line between entries

    with open(output_path, "w", encoding="utf-8") as file:
        _ = file.write("\n".join(lines))

    return output_path
