"""ElevenLabs TTS provider."""

import os
from elevenlabs.client import AsyncElevenLabs
from paystreet.ai.tts import BaseTTSProvider, AudioResult
from paystreet.app.config import get_settings

CHARS_PER_SECOND = 14.0


class ElevenLabsTTSProvider(BaseTTSProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncElevenLabs(api_key=settings.elevenlabs_api_key)

    @property
    def provider_name(self) -> str:
        return "elevenlabs"

    async def synthesize(
        self,
        text: str,
        output_path: str,
        voice: str = "Rachel",
    ) -> AudioResult:
        os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(
            output_path
        ) else None
        audio = await self._client.generate(
            text=text,
            voice=voice,
            model="eleven_multilingual_v2",
        )
        with open(output_path, "wb") as f:
            async for chunk in audio:
                f.write(chunk)
        duration = max(1.0, len(text) / CHARS_PER_SECOND)
        return AudioResult(
            file_path=output_path,
            duration_seconds=duration,
            provider="elevenlabs",
            voice_id=voice,
        )
