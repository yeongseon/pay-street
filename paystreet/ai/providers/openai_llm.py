"""OpenAI LLM provider for script generation."""

import json
from openai import AsyncOpenAI
from paystreet.ai.llm import BaseLLMProvider, ScriptContent
from paystreet.ai.script_validator import validate_script_json
from paystreet.app.config import get_settings


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.llm_model
        self._temperature = settings.llm_temperature
        self._max_tokens = settings.llm_max_tokens

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate_script(self, prompt: str) -> ScriptContent:
        response = await self._client.chat.completions.create(
            model=self._model,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a content script writer. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        raw = response.choices[0].message.content or ""
        return validate_script_json(raw)
