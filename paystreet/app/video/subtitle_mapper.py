# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportDeprecated=false
"""Map timeline entries to subtitle segments."""

from dataclasses import dataclass
from typing import Optional

from paystreet.app.video.timeline_builder import Timeline


@dataclass
class SubtitleSegment:
    index: int
    start_time: float
    end_time: float
    text: str
    speaker: Optional[str] = None
    highlight: bool = False  # True if contains salary/job info


def map_subtitles(timeline: Timeline) -> list[SubtitleSegment]:
    """Generate subtitle segments from a timeline."""
    segments = []
    idx = 1

    for entry in timeline.entries:
        if not entry.content:
            continue
        # Split long content into chunks of ~15 words
        words = entry.content.split()
        chunks = [words[i : i + 15] for i in range(0, len(words), 15)]
        chunk_count = len(chunks)
        chunk_duration = entry.duration / max(chunk_count, 1)

        for j, chunk in enumerate(chunks):
            text = " ".join(chunk)
            start = entry.start_time + j * chunk_duration
            end = start + chunk_duration - 0.05  # small gap between subtitles
            segments.append(
                SubtitleSegment(
                    index=idx,
                    start_time=round(start, 3),
                    end_time=round(end, 3),
                    text=text,
                    speaker=entry.speaker,
                    highlight="만원" in text or "연봉" in text,
                )
            )
            idx += 1

    return segments
