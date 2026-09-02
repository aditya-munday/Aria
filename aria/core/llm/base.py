"""Abstract base class for LLM reasoning and streaming token generation."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCallChunk:
    """Incremental or complete tool call invocation from LLM."""

    call_id: str
    tool_name: str
    arguments_json: str


@dataclass
class LLMStreamChunk:
    """Streaming chunk from reasoning model."""

    text: str = ""
    is_first_token: bool = False
    is_complete: bool = False
    tool_calls: list[ToolCallChunk] = field(default_factory=list)
    ttft_ms: float = 0.0


class LLMClient(ABC):
    """Abstract interface for reasoning models (e.g. Grok)."""

    @abstractmethod
    def stream_chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[LLMStreamChunk]:
        """Stream response tokens and tool calls for the given conversational history."""
        pass
