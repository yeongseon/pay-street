"""Mock TTS provider — generates minimal silent WAV file."""

import asyncio
import struct
import wave
import os
from paystreet.ai.tts import BaseTTSProvider, AudioResult

# Rough estimate: 5 chars per second of speech
CHARS_PER_SECOND = 5.0


def _create_silent_wav(path: str, duration_seconds: float) -> None:
    """Create a silent WAV file at the given path."""
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    sample_rate = 22050
    num_samples = int(sample_rate * duration_seconds)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * num_samples)


class MockTTSProvider(BaseTTSProvider):
    @property
    def provider_name(self) -> str:
        return "mock"

    async def synthesize(
        self,
        text: str,
        output_path: str,
        voice: str = "default",
    ) -> AudioResult:
        await asyncio.sleep(0.05)
        duration = max(1.0, len(text) / CHARS_PER_SECOND)
        _create_silent_wav(output_path, duration)
        return AudioResult(
            file_path=output_path,
            duration_seconds=duration,
            provider="mock",
            voice_id="mock_voice",
        )
