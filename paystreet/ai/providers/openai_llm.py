# pyright: reportMissingImports=false
"""OpenAI LLM provider for script generation.

API key resolution order:
  1. DB (api_keys table, provider="openai", is_active=True)
  2. Settings / .env  (openai_api_key)
  3. Raise RuntimeError if neither found
"""

import json

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from paystreet.ai.llm import BaseLLMProvider, ScriptContent
from paystreet.ai.script_validator import validate_script_json
from paystreet.app.config import get_settings
from paystreet.app.models.api_key import ApiKey


async def _resolve_openai_key(db: AsyncSession | None) -> str:
    """Return the active OpenAI API key from DB, falling back to settings."""
    if db is not None:
        result = await db.execute(
            select(ApiKey).where(
                ApiKey.provider == "openai",
                ApiKey.is_active.is_(True),
            )
        )
        row = result.scalar_one_or_none()
        if row and row.key_value:
            return row.key_value

    settings = get_settings()
    if settings.openai_api_key:
        return settings.openai_api_key

    raise RuntimeError(
        "No active OpenAI API key found. "
        "Add one via Admin > API Keys or set OPENAI_API_KEY in .env."
    )


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI-backed script generator.

    Pass a live AsyncSession so the provider looks up the key from DB on every
    instantiation.  When no session is available (e.g. unit tests), it falls
    back to the .env setting.
    """

    def __init__(self, api_key: str) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = settings.llm_model
        self._temperature = settings.llm_temperature
        self._max_tokens = settings.llm_max_tokens

    @classmethod
    async def create(cls, db: AsyncSession | None = None) -> "OpenAILLMProvider":
        """Async factory — resolves the API key before construction."""
        key = await _resolve_openai_key(db)
        return cls(api_key=key)

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
