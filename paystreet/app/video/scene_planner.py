# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportDeprecated=false
"""Scene planner - maps script dialogue to video scenes."""

from dataclasses import dataclass, field
from typing import Optional

from paystreet.ai.llm import ScriptContent


@dataclass
class SceneSegment:
    scene_id: str
    scene_type: str  # intro | question | answer | highlight | outro
    content: str  # text content for this scene
    speaker: Optional[str]  # "interviewer" | "interviewee" | None
    audio_path: Optional[str] = None
    duration: float = 0.0  # seconds; 0 = TBD from audio


@dataclass
class ScenePlan:
    scenes: list[SceneSegment] = field(default_factory=list)
    total_duration: float = 0.0

    def update_duration(self) -> None:
        self.total_duration = sum(s.duration for s in self.scenes)


def plan_scenes(script: ScriptContent, salary_range: str) -> ScenePlan:
    """Convert a ScriptContent into an ordered list of SceneSegments."""
    plan = ScenePlan()

    # Intro scene
    plan.scenes.append(
        SceneSegment(
            scene_id="intro",
            scene_type="intro",
            content=script.hook,
            speaker=None,
            duration=2.0,  # fixed for intro
        )
    )

    # Question/Answer pairs from dialogue
    for i, line in enumerate(script.dialogue):
        scene_type = "question" if line.speaker == "interviewer" else "answer"
        plan.scenes.append(
            SceneSegment(
                scene_id=f"{scene_type}_{i}",
                scene_type=scene_type,
                content=line.line,
                speaker=line.speaker,
                duration=0.0,  # will be set after TTS
            )
        )

    # Highlight scene with salary info
    plan.scenes.append(
        SceneSegment(
            scene_id="highlight",
            scene_type="highlight",
            content=salary_range,
            speaker=None,
            duration=2.0,
        )
    )

    # Outro
    plan.scenes.append(
        SceneSegment(
            scene_id="outro",
            scene_type="outro",
            content=script.outro,
            speaker=None,
            duration=2.0,
        )
    )

    return plan
