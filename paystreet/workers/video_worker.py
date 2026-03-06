# pyright: reportMissingImports=false, reportMissingTypeArgument=false, reportMissingTypeStubs=false
"""Celery tasks for video generation pipeline."""

import asyncio
import logging

from celery import shared_task

from paystreet.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


@celery_app.task(
    bind=True,
    name="paystreet.workers.video_worker.run_video_pipeline",
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
)
def run_video_pipeline(
    self,
    job_title: str,
    experience_years: int,
    region: str = "Seoul",
    company_size: str = "mid",
    template_id: str = "street_interview_v1",
) -> dict:
    """Run full video pipeline as a Celery task."""
    logger.info(f"Starting video pipeline: {job_title} {experience_years}yr {region}")
    try:

        async def _pipeline():
            from paystreet.app.database import get_session_factory
            from paystreet.app.pipelines.video_pipeline import VideoPipeline

            factory = get_session_factory()
            async with factory() as session:
                pipeline = VideoPipeline(db=session)
                return await pipeline.run(
                    job_title=job_title,
                    experience_years=experience_years,
                    region=region,
                    company_size=company_size,
                    template_id=template_id,
                )

        result = _run_async(_pipeline())
        logger.info(f"Pipeline completed: {result}")
        return result
    except Exception as exc:
        logger.exception(f"Pipeline failed: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    name="paystreet.workers.video_worker.generate_script_task",
    max_retries=3,
    default_retry_delay=10,
)
def generate_script_task(self, prompt: str, provider: str = "mock") -> dict:
    """Generate a script via LLM as a Celery task."""
    try:

        async def _generate():
            from paystreet.ai.providers.mock_llm import MockLLMProvider
            from paystreet.ai.providers.openai_llm import OpenAILLMProvider

            p = MockLLMProvider() if provider == "mock" else OpenAILLMProvider()
            script = await p.generate_script(prompt)
            return script.model_dump()

        return _run_async(_generate())
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    name="paystreet.workers.video_worker.synthesize_audio_task",
    max_retries=3,
    default_retry_delay=10,
)
def synthesize_audio_task(
    self, text: str, output_path: str, provider: str = "mock"
) -> dict:
    """Synthesize audio via TTS as a Celery task."""
    try:

        async def _synth():
            from paystreet.ai.providers.mock_tts import MockTTSProvider
            from paystreet.ai.providers.openai_tts import OpenAITTSProvider

            p = MockTTSProvider() if provider == "mock" else OpenAITTSProvider()
            result = await p.synthesize(text=text, output_path=output_path)
            return {
                "file_path": result.file_path,
                "duration_seconds": result.duration_seconds,
                "provider": result.provider,
            }

        return _run_async(_synth())
    except Exception as exc:
        raise self.retry(exc=exc)
