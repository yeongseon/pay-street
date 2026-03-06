"""Tests for AI providers: OpenAI LLM, OpenAI TTS, ElevenLabs TTS (all mocked)."""

import os
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

import pytest

from paystreet.ai.llm import ScriptContent, DialogueLine


# ---------------------------------------------------------------------------
# OpenAILLMProvider
# ---------------------------------------------------------------------------


def _make_openai_settings():
    s = MagicMock()
    s.openai_api_key = "test-key"
    s.llm_model = "gpt-4o"
    s.llm_temperature = 0.7
    s.llm_max_tokens = 1000
    return s


def _valid_script_json():
    return (
        '{"hook": "연봉 얼마 받으세요?", '
        '"dialogue": [{"speaker": "interviewer", "line": "안녕하세요"}, '
        '{"speaker": "interviewee", "line": "5000만원이요"}], '
        '"outro": "구독 부탁드려요"}'
    )


@pytest.mark.asyncio
async def test_openai_llm_provider_name():
    with patch(
        "paystreet.ai.providers.openai_llm.get_settings",
        return_value=_make_openai_settings(),
    ):
        with patch("paystreet.ai.providers.openai_llm.AsyncOpenAI"):
            from paystreet.ai.providers.openai_llm import OpenAILLMProvider

            provider = OpenAILLMProvider()
            assert provider.provider_name == "openai"


@pytest.mark.asyncio
async def test_openai_llm_generate_script_returns_script_content():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = _valid_script_json()

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch(
        "paystreet.ai.providers.openai_llm.get_settings",
        return_value=_make_openai_settings(),
    ):
        with patch(
            "paystreet.ai.providers.openai_llm.AsyncOpenAI", return_value=mock_client
        ):
            from importlib import reload
            import paystreet.ai.providers.openai_llm as mod

            reload(mod)
            provider = mod.OpenAILLMProvider()
            provider._client = mock_client

            result = await provider.generate_script("write a salary script")

    assert isinstance(result, ScriptContent)
    assert result.hook == "연봉 얼마 받으세요?"
    assert len(result.dialogue) == 2
    assert result.outro == "구독 부탁드려요"


@pytest.mark.asyncio
async def test_openai_llm_generate_script_calls_chat_completion():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = _valid_script_json()

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch(
        "paystreet.ai.providers.openai_llm.get_settings",
        return_value=_make_openai_settings(),
    ):
        with patch(
            "paystreet.ai.providers.openai_llm.AsyncOpenAI", return_value=mock_client
        ):
            import paystreet.ai.providers.openai_llm as mod
            from importlib import reload

            reload(mod)
            provider = mod.OpenAILLMProvider()
            provider._client = mock_client

            await provider.generate_script("test prompt")

    mock_client.chat.completions.create.assert_awaited_once()
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["response_format"] == {"type": "json_object"}
    messages = call_kwargs["messages"]
    assert any("test prompt" in m.get("content", "") for m in messages)


@pytest.mark.asyncio
async def test_openai_llm_uses_empty_string_when_content_none():
    """When response content is None, generate_script raises ValueError (empty JSON)."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = None

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch(
        "paystreet.ai.providers.openai_llm.get_settings",
        return_value=_make_openai_settings(),
    ):
        with patch(
            "paystreet.ai.providers.openai_llm.AsyncOpenAI", return_value=mock_client
        ):
            import paystreet.ai.providers.openai_llm as mod
            from importlib import reload

            reload(mod)
            provider = mod.OpenAILLMProvider()
            provider._client = mock_client

            with pytest.raises(ValueError):
                await provider.generate_script("prompt")

# ---------------------------------------------------------------------------
# OpenAITTSProvider
# ---------------------------------------------------------------------------


def _make_tts_settings():
    s = MagicMock()
    s.openai_api_key = "test-key"
    return s


@pytest.mark.asyncio
async def test_openai_tts_provider_name():
    with patch(
        "paystreet.ai.providers.openai_tts.get_settings",
        return_value=_make_tts_settings(),
    ):
        with patch("paystreet.ai.providers.openai_tts.AsyncOpenAI"):
            from importlib import reload
            import paystreet.ai.providers.openai_tts as mod

            reload(mod)
            provider = mod.OpenAITTSProvider()
            assert provider.provider_name == "openai"


@pytest.mark.asyncio
async def test_openai_tts_synthesize_returns_audio_result(tmp_path):
    output_path = str(tmp_path / "output.mp3")

    mock_response = MagicMock()
    mock_response.stream_to_file = MagicMock()

    mock_client = AsyncMock()
    mock_client.audio.speech.create = AsyncMock(return_value=mock_response)

    with patch(
        "paystreet.ai.providers.openai_tts.get_settings",
        return_value=_make_tts_settings(),
    ):
        with patch(
            "paystreet.ai.providers.openai_tts.AsyncOpenAI", return_value=mock_client
        ):
            from importlib import reload
            import paystreet.ai.providers.openai_tts as mod

            reload(mod)
            provider = mod.OpenAITTSProvider()
            provider._client = mock_client

            result = await provider.synthesize(
                text="안녕하세요 테스트입니다",
                output_path=output_path,
                voice="alloy",
            )

    assert result.file_path == output_path
    assert result.provider == "openai"
    assert result.voice_id == "alloy"
    assert result.duration_seconds >= 1.0
    mock_response.stream_to_file.assert_called_once_with(output_path)


@pytest.mark.asyncio
async def test_openai_tts_duration_estimate():
    """Duration estimate = max(1.0, len(text) / 14.0)."""
    output_path = "/tmp/test_tts.mp3"
    text = "a" * 28  # 28 chars -> 2.0 seconds

    mock_response = MagicMock()
    mock_response.stream_to_file = MagicMock()

    mock_client = AsyncMock()
    mock_client.audio.speech.create = AsyncMock(return_value=mock_response)

    with patch(
        "paystreet.ai.providers.openai_tts.get_settings",
        return_value=_make_tts_settings(),
    ):
        with patch(
            "paystreet.ai.providers.openai_tts.AsyncOpenAI", return_value=mock_client
        ):
            with patch("paystreet.ai.providers.openai_tts.os.makedirs"):
                from importlib import reload
                import paystreet.ai.providers.openai_tts as mod

                reload(mod)
                provider = mod.OpenAITTSProvider()
                provider._client = mock_client

                result = await provider.synthesize(text=text, output_path=output_path)

    assert result.duration_seconds == pytest.approx(2.0, abs=0.1)


@pytest.mark.asyncio
async def test_openai_tts_minimum_duration():
    """Very short text still gets at least 1.0s duration."""
    output_path = "/tmp/short.mp3"
    text = "hi"  # 2 chars -> would be 0.14s, but clamped to 1.0

    mock_response = MagicMock()
    mock_response.stream_to_file = MagicMock()

    mock_client = AsyncMock()
    mock_client.audio.speech.create = AsyncMock(return_value=mock_response)

    with patch(
        "paystreet.ai.providers.openai_tts.get_settings",
        return_value=_make_tts_settings(),
    ):
        with patch(
            "paystreet.ai.providers.openai_tts.AsyncOpenAI", return_value=mock_client
        ):
            with patch("paystreet.ai.providers.openai_tts.os.makedirs"):
                from importlib import reload
                import paystreet.ai.providers.openai_tts as mod

                reload(mod)
                provider = mod.OpenAITTSProvider()
                provider._client = mock_client

                result = await provider.synthesize(text=text, output_path=output_path)

    assert result.duration_seconds == 1.0


@pytest.mark.asyncio
async def test_openai_tts_creates_output_directory(tmp_path):
    """Ensures os.makedirs is called for nested paths."""
    nested_path = str(tmp_path / "subdir" / "audio.mp3")

    mock_response = MagicMock()
    mock_response.stream_to_file = MagicMock()

    mock_client = AsyncMock()
    mock_client.audio.speech.create = AsyncMock(return_value=mock_response)

    with patch(
        "paystreet.ai.providers.openai_tts.get_settings",
        return_value=_make_tts_settings(),
    ):
        with patch(
            "paystreet.ai.providers.openai_tts.AsyncOpenAI", return_value=mock_client
        ):
            from importlib import reload
            import paystreet.ai.providers.openai_tts as mod

            reload(mod)
            provider = mod.OpenAITTSProvider()
            provider._client = mock_client

            result = await provider.synthesize(text="test", output_path=nested_path)

    # The directory must now exist
    assert os.path.isdir(str(tmp_path / "subdir"))


# ---------------------------------------------------------------------------
# ElevenLabsTTSProvider
# ---------------------------------------------------------------------------


def _make_elevenlabs_settings():
    s = MagicMock()
    s.elevenlabs_api_key = "test-elevenlabs-key"
    return s


@pytest.mark.asyncio
async def test_elevenlabs_tts_provider_name():
    with patch(
        "paystreet.ai.providers.elevenlabs_tts.get_settings",
        return_value=_make_elevenlabs_settings(),
    ):
        with patch("paystreet.ai.providers.elevenlabs_tts.AsyncElevenLabs"):
            from importlib import reload
            import paystreet.ai.providers.elevenlabs_tts as mod

            reload(mod)
            provider = mod.ElevenLabsTTSProvider()
            assert provider.provider_name == "elevenlabs"


@pytest.mark.asyncio
async def test_elevenlabs_tts_synthesize_returns_audio_result(tmp_path):
    output_path = str(tmp_path / "output.mp3")
    text = "안녕하세요 ElevenLabs 테스트"

    async def async_gen():
        yield b"chunk1"
        yield b"chunk2"

    mock_client = AsyncMock()
    mock_client.generate = AsyncMock(return_value=async_gen())

    with patch(
        "paystreet.ai.providers.elevenlabs_tts.get_settings",
        return_value=_make_elevenlabs_settings(),
    ):
        with patch(
            "paystreet.ai.providers.elevenlabs_tts.AsyncElevenLabs",
            return_value=mock_client,
        ):
            from importlib import reload
            import paystreet.ai.providers.elevenlabs_tts as mod

            reload(mod)
            provider = mod.ElevenLabsTTSProvider()
            provider._client = mock_client

            result = await provider.synthesize(
                text=text,
                output_path=output_path,
                voice="Rachel",
            )

    assert result.file_path == output_path
    assert result.provider == "elevenlabs"
    assert result.voice_id == "Rachel"
    assert result.duration_seconds >= 1.0
    # File should exist with the written chunks
    assert os.path.exists(output_path)
    with open(output_path, "rb") as f:
        content = f.read()
    assert content == b"chunk1chunk2"


@pytest.mark.asyncio
async def test_elevenlabs_tts_duration_estimate(tmp_path):
    """Duration is max(1.0, len(text)/14.0)."""
    output_path = str(tmp_path / "audio.mp3")
    text = "a" * 42  # 42 chars -> 3.0 seconds

    async def async_gen():
        yield b""

    mock_client = AsyncMock()
    mock_client.generate = AsyncMock(return_value=async_gen())

    with patch(
        "paystreet.ai.providers.elevenlabs_tts.get_settings",
        return_value=_make_elevenlabs_settings(),
    ):
        with patch(
            "paystreet.ai.providers.elevenlabs_tts.AsyncElevenLabs",
            return_value=mock_client,
        ):
            from importlib import reload
            import paystreet.ai.providers.elevenlabs_tts as mod

            reload(mod)
            provider = mod.ElevenLabsTTSProvider()
            provider._client = mock_client

            result = await provider.synthesize(text=text, output_path=output_path)

    assert result.duration_seconds == pytest.approx(3.0, abs=0.1)


@pytest.mark.asyncio
async def test_elevenlabs_tts_creates_output_directory(tmp_path):
    nested_path = str(tmp_path / "el_subdir" / "audio.mp3")

    async def async_gen():
        yield b"data"

    mock_client = AsyncMock()
    mock_client.generate = AsyncMock(return_value=async_gen())

    with patch(
        "paystreet.ai.providers.elevenlabs_tts.get_settings",
        return_value=_make_elevenlabs_settings(),
    ):
        with patch(
            "paystreet.ai.providers.elevenlabs_tts.AsyncElevenLabs",
            return_value=mock_client,
        ):
            from importlib import reload
            import paystreet.ai.providers.elevenlabs_tts as mod

            reload(mod)
            provider = mod.ElevenLabsTTSProvider()
            provider._client = mock_client

            await provider.synthesize(text="test", output_path=nested_path)

    assert os.path.isdir(str(tmp_path / "el_subdir"))


@pytest.mark.asyncio
async def test_elevenlabs_tts_calls_generate_with_correct_params(tmp_path):
    output_path = str(tmp_path / "out.mp3")

    async def async_gen():
        yield b""

    mock_client = AsyncMock()
    mock_client.generate = AsyncMock(return_value=async_gen())

    with patch(
        "paystreet.ai.providers.elevenlabs_tts.get_settings",
        return_value=_make_elevenlabs_settings(),
    ):
        with patch(
            "paystreet.ai.providers.elevenlabs_tts.AsyncElevenLabs",
            return_value=mock_client,
        ):
            from importlib import reload
            import paystreet.ai.providers.elevenlabs_tts as mod

            reload(mod)
            provider = mod.ElevenLabsTTSProvider()
            provider._client = mock_client

            await provider.synthesize(
                text="hello", output_path=output_path, voice="Adam"
            )

    mock_client.generate.assert_awaited_once()
    call_kwargs = mock_client.generate.call_args.kwargs
    assert call_kwargs["text"] == "hello"
    assert call_kwargs["voice"] == "Adam"
    assert call_kwargs["model"] == "eleven_multilingual_v2"
