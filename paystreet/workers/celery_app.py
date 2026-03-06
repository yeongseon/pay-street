# pyright: reportMissingImports=false, reportMissingTypeStubs=false, reportUnknownMemberType=false, reportUnnecessaryTypeIgnoreComment=false
"""Celery application configuration for PayStreet."""

from celery import Celery

from paystreet.app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "paystreet",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["paystreet.workers.video_worker"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
    # Important for long-running FFmpeg tasks
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Result expiry
    result_expires=3600,
    # Routing
    task_routes={
        "paystreet.workers.video_worker.run_video_pipeline": {"queue": "video"},
        "paystreet.workers.video_worker.generate_script_task": {"queue": "default"},
        "paystreet.workers.video_worker.synthesize_audio_task": {"queue": "default"},
    },
)
