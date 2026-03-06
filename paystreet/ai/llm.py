"""LLM provider abstract interface and Pydantic models."""

from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class DialogueLine(BaseModel):
    speaker: str  # "interviewer" | "interviewee"
    line: str


class ScriptContent(BaseModel):
    hook: str
    dialogue: list[DialogueLine]
    outro: str

    @property
    def total_text(self) -> str:
        parts = [self.hook]
        for d in self.dialogue:
            parts.append(d.line)
        parts.append(self.outro)
        return " ".join(parts)

    @property
    def interviewer_lines(self) -> list[str]:
        return [d.line for d in self.dialogue if d.speaker == "interviewer"]

    @property
    def interviewee_lines(self) -> list[str]:
        return [d.line for d in self.dialogue if d.speaker == "interviewee"]


class BaseLLMProvider(ABC):
    """Abstract base for all LLM providers."""

    @abstractmethod
    async def generate_script(self, prompt: str) -> ScriptContent:
        """Generate a script from the given prompt. Returns ScriptContent."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str: ...
