# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnnecessaryTypeIgnoreComment=false
"""Video pipeline orchestrator - end-to-end from topic to mp4."""

import logging
import os
import uuid
from datetime import datetime, timezone

from paystreet.ai.tts import AudioResult
from sqlalchemy.ext.asyncio import AsyncSession

from paystreet.ai.prompts import build_script_prompt
from paystreet.app.config import Settings, get_settings
from paystreet.app.models.content import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_RUNNING,
    AudioJob,
    ContentTopic,
    RenderJob,
    Script,
    SubtitleAsset,
)
from paystreet.app.video.render_engine import render_video
from paystreet.app.video.scene_planner import plan_scenes
from paystreet.app.video.srt_writer import write_srt
from paystreet.app.video.subtitle_mapper import map_subtitles
from paystreet.app.video.template_selector import load_template
from paystreet.app.video.timeline_builder import build_timeline
from paystreet.data.salary_calculator import salary_range_for_prompt
from paystreet.data.salary_repository import SalaryRepository

logger = logging.getLogger(__name__)


def _get_llm_provider(provider_name: str):
    if provider_name == "openai":
        from paystreet.ai.providers.openai_llm import OpenAILLMProvider

        return OpenAILLMProvider()
    from paystreet.ai.providers.mock_llm import MockLLMProvider

    return MockLLMProvider()


def _get_tts_provider(provider_name: str):
    if provider_name == "openai":
        from paystreet.ai.providers.openai_tts import OpenAITTSProvider

        return OpenAITTSProvider()
    if provider_name == "elevenlabs":
        from paystreet.ai.providers.elevenlabs_tts import ElevenLabsTTSProvider

        return ElevenLabsTTSProvider()
    from paystreet.ai.providers.mock_tts import MockTTSProvider

    return MockTTSProvider()


def _audio_extension(provider_name: str) -> str:
    if provider_name in {"openai", "elevenlabs"}:
        return ".mp3"
    return ".wav"


class VideoPipeline:
    _db: AsyncSession
    _settings: Settings

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._settings = get_settings()

    async def run(
        self,
        job_title: str,
        experience_years: int,
        region: str = "Seoul",
        company_size: str = "mid",
        template_id: str = "street_interview_v1",
    ) -> dict[str, object]:
        """Run the full pipeline. Returns a dict with output_path and job IDs."""
        job_id = str(uuid.uuid4())
        logger.info(
            "[%s] Starting pipeline: %s %syr %s",
            job_id,
            job_title,
            experience_years,
            region,
        )

        repo = SalaryRepository(self._db)
        records = await repo.get_salary_records(
            job_title=job_title,
            experience_years=experience_years,
            region=region,
            company_size=company_size,
        )
        salary_range = salary_range_for_prompt(records)
        logger.info("[%s] Salary range: %s", job_id, salary_range)

        topic = ContentTopic(
            content_type="salary_reveal",
            title=f"{experience_years}년차 {job_title} 연봉 얼마예요",
            job_title=job_title,
            experience_years=experience_years,
            region=region,
            company_size=company_size,
            score=7.0,
            status=STATUS_RUNNING,
        )
        self._db.add(topic)
        await self._db.flush()

        llm = _get_llm_provider(self._settings.llm_provider)
        prompt = build_script_prompt(
            job_title=job_title,
            experience_years=experience_years,
            region=region,
            company_size=company_size,
            salary_range=salary_range,
        )
        script_content = await llm.generate_script(prompt)
        logger.info("[%s] Script generated: %s...", job_id, script_content.hook[:50])

        script_record = Script(
            topic_id=topic.id,
            provider=llm.provider_name,
            model=self._settings.llm_model,
            prompt_version="v1.0",
            content=script_content.model_dump(),
            status=STATUS_COMPLETED,
        )
        self._db.add(script_record)
        await self._db.flush()

        tts = _get_tts_provider(self._settings.tts_provider)
        temp_dir = os.path.join(self._settings.temp_dir, job_id)
        os.makedirs(temp_dir, exist_ok=True)

        interviewer_texts = script_content.interviewer_lines
        interviewee_texts = script_content.interviewee_lines

        audio_results: dict[str, AudioResult] = {}
        audio_ext = _audio_extension(tts.provider_name)

        for i, text in enumerate(interviewer_texts):
            path = os.path.join(temp_dir, f"interviewer_{i}{audio_ext}")
            result = await tts.synthesize(text=text, output_path=path, voice="alloy")
            audio_results[f"interviewer_{i}"] = result

        for i, text in enumerate(interviewee_texts):
            path = os.path.join(temp_dir, f"interviewee_{i}{audio_ext}")
            result = await tts.synthesize(text=text, output_path=path, voice="nova")
            audio_results[f"interviewee_{i}"] = result

        audio_record = AudioJob(
            script_id=script_record.id,
            provider=tts.provider_name,
            status=STATUS_COMPLETED,
            interviewer_path=(
                audio_results["interviewer_0"].file_path
                if "interviewer_0" in audio_results
                else None
            ),
            interviewee_path=(
                audio_results["interviewee_0"].file_path
                if "interviewee_0" in audio_results
                else None
            ),
        )
        self._db.add(audio_record)
        await self._db.flush()

        plan = plan_scenes(script_content, salary_range)

        int_idx = 0
        inv_idx = 0
        for scene in plan.scenes:
            if (
                scene.speaker == "interviewer"
                and f"interviewer_{int_idx}" in audio_results
            ):
                result = audio_results[f"interviewer_{int_idx}"]
                scene.audio_path = result.file_path
                scene.duration = result.duration_seconds
                int_idx += 1
            elif (
                scene.speaker == "interviewee"
                and f"interviewee_{inv_idx}" in audio_results
            ):
                result = audio_results[f"interviewee_{inv_idx}"]
                scene.audio_path = result.file_path
                scene.duration = result.duration_seconds
                inv_idx += 1

        timeline = build_timeline(plan)

        subtitle_segments = map_subtitles(timeline)
        srt_path = os.path.join(temp_dir, "subtitles.srt")
        write_srt(subtitle_segments, srt_path)

        subtitle_record = SubtitleAsset(
            script_id=script_record.id,
            audio_job_id=audio_record.id,
            format="srt",
            file_path=srt_path,
            status=STATUS_COMPLETED,
        )
        self._db.add(subtitle_record)
        await self._db.flush()

        template = load_template(template_id)
        render_record = RenderJob(
            topic_id=topic.id,
            script_id=script_record.id,
            audio_job_id=audio_record.id,
            subtitle_id=subtitle_record.id,
            template_id=template_id,
            status=STATUS_RUNNING,
        )
        self._db.add(render_record)
        await self._db.flush()

        try:
            output_path = render_video(
                timeline=timeline,
                subtitles=subtitle_segments,
                template=template,
                srt_path=srt_path,
                job_id=job_id,
            )
            render_record.status = STATUS_COMPLETED
            render_record.output_path = output_path
            render_record.completed_at = datetime.now(timezone.utc)
            topic.status = STATUS_COMPLETED
        except Exception as exc:
            render_record.status = STATUS_FAILED
            render_record.error_message = str(exc)
            topic.status = STATUS_FAILED
            await self._db.flush()
            raise

        await self._db.flush()
        logger.info("[%s] Pipeline complete: %s", job_id, output_path)

        return {
            "job_id": job_id,
            "topic_id": str(topic.id),
            "script_id": str(script_record.id),
            "render_job_id": str(render_record.id),
            "output_path": output_path,
            "duration": timeline.total_duration,
            "status": "completed",
        }
