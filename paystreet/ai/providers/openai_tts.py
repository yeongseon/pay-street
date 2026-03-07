"""OpenAI TTS provider."""

import os
from openai import AsyncOpenAI
from paystreet.ai.tts import BaseTTSProvider, AudioResult
from paystreet.app.config import get_settings

# Estimate for computing duration before we decode audio
CHARS_PER_SECOND = 14.0


class OpenAITTSProvider(BaseTTSProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    @property
    def provider_name(self) -> str:
        return "openai"

    async def synthesize(
        self,
        text: str,
        output_path: str,
        voice: str = "alloy",
    ) -> AudioResult:
        os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(
            output_path
        ) else None
        response = await self._client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            response_format="mp3",
        )
        await response.stream_to_file(output_path)
        duration = max(1.0, len(text) / CHARS_PER_SECOND)
        return AudioResult(
            file_path=output_path,
            duration_seconds=duration,
            provider="openai",
            voice_id=voice,
        )
