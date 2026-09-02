"""Unit tests for Groq LLM client, personality prompts, and tool calling."""

import json

import pytest

from aria.core.intent.directioner_client import DIRECTIONER_TOOL_DEFINITION
from aria.core.llm.mock_llm import MockLLMClient
from aria.core.llm.personality_matrix import (
    get_system_prompt,
)
from aria.core.pipeline.state import AssistantMode


@pytest.mark.unit
def test_personality_matrix_prompts() -> None:
    aria_prompt = get_system_prompt(
        AssistantMode.ARIA,
        memory_context="User likes jazz music",
        active_panels=["weather_panel"],
        extra_facts={"theme": "dark"},
    )
    assert "Aria" in aria_prompt
    assert "warm, concise, elegant" in aria_prompt
    assert "User likes jazz music" in aria_prompt
    assert "weather_panel" in aria_prompt

    jarvis_prompt = get_system_prompt(AssistantMode.JARVIS)
    assert "Jarvis" in jarvis_prompt
    assert "tactical intelligence" in jarvis_prompt


@pytest.mark.asyncio
@pytest.mark.unit
async def test_mock_llm_streaming_text() -> None:
    client = MockLLMClient(canned_response="Aria is ready to assist.")
    chunks = []
    async for chunk in client.stream_chat(messages=[{"role": "user", "content": "Hello"}]):
        chunks.append(chunk)

    text_parts = [c.text for c in chunks if c.text]
    full_text = "".join(text_parts)
    assert "Aria is ready to assist." in full_text
    assert chunks[0].is_first_token is True
    assert chunks[-1].is_complete is True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_mock_llm_tool_calling() -> None:
    client = MockLLMClient()
    tool_args = {
        "category": "app_control",
        "action_name": "launch_terminal",
        "risk_tier": "medium",
        "spoken_summary": "Launching system terminal",
    }
    client.set_tool_call("delegate_to_directioner_ai", json.dumps(tool_args))

    chunks = []
    async for chunk in client.stream_chat(
        messages=[{"role": "user", "content": "Open terminal"}],
        tools=[DIRECTIONER_TOOL_DEFINITION],
    ):
        chunks.append(chunk)

    assert len(chunks) == 2
    assert len(chunks[0].tool_calls) == 1
    call = chunks[0].tool_calls[0]
    assert call.tool_name == "delegate_to_directioner_ai"
    assert "launch_terminal" in call.arguments_json
