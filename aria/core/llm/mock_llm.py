"""Mock LLM client for automated tests and CI."""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from aria.core.llm.base import LLMClient, LLMStreamChunk, ToolCallChunk


class MockLLMClient(LLMClient):
    """Controllable LLM client for simulation of responses and tool calls in CI."""

    def __init__(
        self,
        canned_response: str = "All systems are nominal.",
        tool_call_to_emit: ToolCallChunk | None = None,
    ) -> None:
        self.canned_response = canned_response
        self.tool_call_to_emit = tool_call_to_emit
        self.recorded_messages: list[list[dict[str, Any]]] = []

    def set_response(self, text: str) -> None:
        """Configure next response text."""
        self.canned_response = text
        self.tool_call_to_emit = None

    def set_tool_call(self, tool_name: str, arguments_json: str) -> None:
        """Configure next response to emit a tool call."""
        self.tool_call_to_emit = ToolCallChunk(
            call_id="call_mock_123",
            tool_name=tool_name,
            arguments_json=arguments_json,
        )

    async def stream_chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[LLMStreamChunk]:
        """Stream simulated tokens or tool calls."""
        self.recorded_messages.append(messages)
        _ = tools

        if self.tool_call_to_emit:
            await asyncio.sleep(0.005)
            yield LLMStreamChunk(
                text="",
                is_first_token=True,
                is_complete=False,
                tool_calls=[self.tool_call_to_emit],
                ttft_ms=5.0,
            )
            await asyncio.sleep(0.005)
            yield LLMStreamChunk(
                text="",
                is_first_token=False,
                is_complete=True,
                ttft_ms=0.0,
            )
            return

        words = self.canned_response.split(" ")
        for i, word in enumerate(words):
            await asyncio.sleep(0.005)
            token = word + (" " if i < len(words) - 1 else "")
            yield LLMStreamChunk(
                text=token,
                is_first_token=(i == 0),
                is_complete=False,
                ttft_ms=5.0 if i == 0 else 0.0,
            )

        yield LLMStreamChunk(
            text="",
            is_first_token=False,
            is_complete=True,
            ttft_ms=0.0,
        )
