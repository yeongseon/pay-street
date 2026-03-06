# pyright: reportDeprecated=false
"""Retry policy helpers for pipeline steps."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Optional, Tuple, Type, TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


async def retry_async(
    fn: Callable[[], Awaitable[T]],
    max_attempts: int = 3,
    base_delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> T:
    """Retry an async function with exponential backoff."""
    delay = base_delay
    last_exc: Optional[Exception] = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await fn()
        except exceptions as exc:
            last_exc = exc
            if attempt < max_attempts:
                logger.warning(
                    f"Attempt {attempt}/{max_attempts} failed: {exc}. Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
                delay *= backoff
    raise RuntimeError(f"All {max_attempts} attempts failed") from last_exc
