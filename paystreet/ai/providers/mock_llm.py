"""Mock LLM provider for testing — returns hardcoded script."""

import asyncio
from paystreet.ai.llm import BaseLLMProvider, ScriptContent, DialogueLine


class MockLLMProvider(BaseLLMProvider):
    @property
    def provider_name(self) -> str:
        return "mock"

    async def generate_script(self, prompt: str) -> ScriptContent:
        await asyncio.sleep(0.05)  # simulate latency
        return ScriptContent(
            hook="4년차 백엔드 개발자 연봉 얼마예요?",
            dialogue=[
                DialogueLine(speaker="interviewer", line="안녕하세요! 무슨 일 하세요?"),
                DialogueLine(
                    speaker="interviewee",
                    line="판교에서 백엔드 개발자로 일하고 있습니다.",
                ),
                DialogueLine(speaker="interviewer", line="연봉이 어느 정도 되세요?"),
                DialogueLine(
                    speaker="interviewee",
                    line="저는 4년차인데, 6천만 원에서 7천만 원 사이예요.",
                ),
            ],
            outro="여러분 연봉은 어떤가요? 댓글로 알려주세요!",
        )
