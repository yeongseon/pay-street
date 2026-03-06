# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportDeprecated=false
"""Build video timeline with timestamps from scene plan + audio durations."""

from dataclasses import dataclass, field
from typing import Optional

from paystreet.app.video.scene_planner import ScenePlan

# Duration rules per scene type (from design spec)
SCENE_DURATION_RULES = {
    "intro": {"min": 1.5, "max": 2.5, "audio_padding": 0.0},
    "question": {"min": 1.0, "max": 30.0, "audio_padding": 0.3},
    "answer": {"min": 1.0, "max": 30.0, "audio_padding": 0.5},
    "highlight": {"min": 1.5, "max": 3.0, "audio_padding": 0.0},
    "outro": {"min": 1.5, "max": 2.5, "audio_padding": 0.0},
}


@dataclass
class TimelineEntry:
    scene_id: str
    scene_type: str
    start_time: float
    end_time: float
    duration: float
    audio_path: Optional[str]
    content: str
    speaker: Optional[str]


@dataclass
class Timeline:
    entries: list[TimelineEntry] = field(default_factory=list)
    total_duration: float = 0.0


def build_timeline(plan: ScenePlan) -> Timeline:
    """Assign start/end timestamps to each scene."""
    timeline = Timeline()
    cursor = 0.0

    for scene in plan.scenes:
        rules = SCENE_DURATION_RULES.get(
            scene.scene_type,
            {"min": 1.5, "max": 5.0, "audio_padding": 0.0},
        )

        if scene.audio_path and scene.duration > 0:
            # Audio-driven: use audio duration + padding
            raw_duration = scene.duration + rules["audio_padding"]
        else:
            # Fixed duration
            raw_duration = scene.duration if scene.duration > 0 else rules["min"]

        # Clamp to min/max
        duration = max(rules["min"], min(rules["max"], raw_duration))

        entry = TimelineEntry(
            scene_id=scene.scene_id,
            scene_type=scene.scene_type,
            start_time=round(cursor, 3),
            end_time=round(cursor + duration, 3),
            duration=round(duration, 3),
            audio_path=scene.audio_path,
            content=scene.content,
            speaker=scene.speaker,
        )
        timeline.entries.append(entry)
        cursor += duration

    timeline.total_duration = round(cursor, 3)
    return timeline
