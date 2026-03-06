"""Tests for AI script format validation."""

import json
import pytest

from paystreet.ai.llm import ScriptContent, DialogueLine
from paystreet.ai.script_validator import validate_script_json


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_SCRIPT_DICT = {
    "hook": "4년차 백엔드 개발자 연봉 얼마예요?",
    "dialogue": [
        {"speaker": "interviewer", "line": "안녕하세요! 무슨 일 하세요?"},
        {"speaker": "interviewee", "line": "판교에서 백엔드 개발자로 일하고 있습니다."},
        {"speaker": "interviewer", "line": "연봉이 어느 정도 되세요?"},
        {"speaker": "interviewee", "line": "6천만 원에서 7천만 원 사이예요."},
    ],
    "outro": "여러분 연봉은 어떤가요? 댓글로 알려주세요!",
}


# ---------------------------------------------------------------------------
# ScriptContent model
# ---------------------------------------------------------------------------


class TestScriptContentModel:
    def test_valid_construction(self):
        sc = ScriptContent(**VALID_SCRIPT_DICT)
        assert sc.hook == VALID_SCRIPT_DICT["hook"]
        assert len(sc.dialogue) == 4
        assert sc.outro == VALID_SCRIPT_DICT["outro"]

    def test_dialogue_line_types(self):
        sc = ScriptContent(**VALID_SCRIPT_DICT)
        for line in sc.dialogue:
            assert isinstance(line, DialogueLine)
            assert line.speaker in ("interviewer", "interviewee")
            assert len(line.line) > 0

    def test_total_text_contains_all_parts(self):
        sc = ScriptContent(**VALID_SCRIPT_DICT)
        text = sc.total_text
        assert sc.hook in text
        assert sc.outro in text
        for d in sc.dialogue:
            assert d.line in text

    def test_interviewer_lines_filter(self):
        sc = ScriptContent(**VALID_SCRIPT_DICT)
        lines = sc.interviewer_lines
        assert len(lines) == 2
        assert all(isinstance(l, str) for l in lines)

    def test_interviewee_lines_filter(self):
        sc = ScriptContent(**VALID_SCRIPT_DICT)
        lines = sc.interviewee_lines
        assert len(lines) == 2

    def test_single_dialogue_line_valid(self):
        sc = ScriptContent(
            hook="훅",
            dialogue=[DialogueLine(speaker="interviewee", line="한 줄만 있어요.")],
            outro="아웃트로",
        )
        assert len(sc.dialogue) == 1

    def test_empty_hook_is_allowed_by_model(self):
        """ScriptContent itself doesn't enforce non-empty hook — validator does."""
        sc = ScriptContent(
            hook="",
            dialogue=[DialogueLine(speaker="interviewer", line="hello")],
            outro="bye",
        )
        assert sc.hook == ""


# ---------------------------------------------------------------------------
# validate_script_json
# ---------------------------------------------------------------------------


class TestValidateScriptJson:
    def test_valid_json_returns_script_content(self):
        raw = json.dumps(VALID_SCRIPT_DICT)
        result = validate_script_json(raw)
        assert isinstance(result, ScriptContent)
        assert result.hook == VALID_SCRIPT_DICT["hook"]

    def test_invalid_json_raises_value_error(self):
        with pytest.raises(ValueError, match="not valid JSON"):
            validate_script_json("{not: valid json}")

    def test_missing_hook_raises_value_error(self):
        bad = {k: v for k, v in VALID_SCRIPT_DICT.items() if k != "hook"}
        with pytest.raises(ValueError, match="hook"):
            validate_script_json(json.dumps(bad))

    def test_missing_dialogue_raises_value_error(self):
        bad = {k: v for k, v in VALID_SCRIPT_DICT.items() if k != "dialogue"}
        with pytest.raises(ValueError, match="dialogue"):
            validate_script_json(json.dumps(bad))

    def test_empty_dialogue_raises_value_error(self):
        bad = {**VALID_SCRIPT_DICT, "dialogue": []}
        with pytest.raises(ValueError, match="empty"):
            validate_script_json(json.dumps(bad))

    def test_dialogue_not_list_raises_value_error(self):
        bad = {**VALID_SCRIPT_DICT, "dialogue": "not a list"}
        with pytest.raises(ValueError, match="dialogue"):
            validate_script_json(json.dumps(bad))

    def test_missing_outro_raises_value_error(self):
        bad = {k: v for k, v in VALID_SCRIPT_DICT.items() if k != "outro"}
        with pytest.raises(ValueError, match="outro"):
            validate_script_json(json.dumps(bad))

    def test_extra_fields_are_ignored(self):
        """Pydantic v2 ignores extra fields by default — should not raise."""
        extra = {**VALID_SCRIPT_DICT, "unexpected_field": "value"}
        result = validate_script_json(json.dumps(extra))
        assert isinstance(result, ScriptContent)

    def test_mock_llm_output_is_valid(self):
        """The hardcoded mock LLM output must pass validation."""
        mock_output = {
            "hook": "4년차 백엔드 개발자 연봉 얼마예요?",
            "dialogue": [
                {"speaker": "interviewer", "line": "안녕하세요! 무슨 일 하세요?"},
                {
                    "speaker": "interviewee",
                    "line": "판교에서 백엔드 개발자로 일하고 있습니다.",
                },
                {"speaker": "interviewer", "line": "연봉이 어느 정도 되세요?"},
                {
                    "speaker": "interviewee",
                    "line": "저는 4년차인데, 6천만 원에서 7천만 원 사이예요.",
                },
            ],
            "outro": "여러분 연봉은 어떤가요? 댓글로 알려주세요!",
        }
        result = validate_script_json(json.dumps(mock_output))
        assert isinstance(result, ScriptContent)
        assert len(result.dialogue) == 4


# ---------------------------------------------------------------------------
# MockLLMProvider output
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mock_llm_provider_returns_valid_script():
    from paystreet.ai.providers.mock_llm import MockLLMProvider

    provider = MockLLMProvider()
    assert provider.provider_name == "mock"

    script = await provider.generate_script("any prompt")
    assert isinstance(script, ScriptContent)
    assert len(script.hook) > 0
    assert len(script.dialogue) >= 2
    assert len(script.outro) > 0
    assert len(script.interviewer_lines) >= 1
    assert len(script.interviewee_lines) >= 1
