"""TTS provider abstract interface and models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AudioResult:
    file_path: str
    duration_seconds: float
    provider: str
    voice_id: str | None = None


class BaseTTSProvider(ABC):
    """Abstract base for all TTS providers."""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        output_path: str,
        voice: str = "default",
    ) -> AudioResult:
        """Synthesize speech and save to output_path. Returns AudioResult."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str: ...
