"""Groq reasoning client with ultra-low TTFT streaming and tool calling support."""

import json
import logging
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx

from aria.core.llm.base import LLMClient, LLMStreamChunk, ToolCallChunk

logger = logging.getLogger(__name__)


class GroqClient(LLMClient):
    """Client for Groq API (powered by LPU inference engine for low TTFT)."""

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
        base_url: str = "https://api.groq.com/openai/v1",
        timeout_seconds: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def stream_chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[LLMStreamChunk]:
        """Stream response tokens and tool calls from Groq."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": 0.7,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        start_time = time.time()
        is_first_token = True

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                ) as response:
                    if response.status_code != 200:
                        error_body = await response.aread()
                        logger.error(
                            "Groq API error %d: %s",
                            response.status_code,
                            error_body.decode("utf-8", errors="replace"),
                        )
                        raise RuntimeError(f"Groq API returned status {response.status_code}")

                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            yield LLMStreamChunk(
                                text="",
                                is_first_token=False,
                                is_complete=True,
                                ttft_ms=(time.time() - start_time) * 1000.0,
                            )
                            break

                        try:
                            chunk_data = json.loads(data_str)
                            choices = chunk_data.get("choices", [])
                            if not choices:
                                continue
                            delta = choices[0].get("delta", {})

                            token_text = delta.get("content", "") or ""
                            tool_calls_raw = delta.get("tool_calls", [])
                            parsed_tool_calls: list[ToolCallChunk] = []

                            for tc in tool_calls_raw:
                                fn = tc.get("function", {})
                                parsed_tool_calls.append(
                                    ToolCallChunk(
                                        call_id=tc.get("id", ""),
                                        tool_name=fn.get("name", ""),
                                        arguments_json=fn.get("arguments", ""),
                                    )
                                )

                            if token_text or parsed_tool_calls:
                                current_ttft = (
                                    (time.time() - start_time) * 1000.0 if is_first_token else 0.0
                                )
                                yield LLMStreamChunk(
                                    text=token_text,
                                    is_first_token=is_first_token,
                                    is_complete=False,
                                    tool_calls=parsed_tool_calls,
                                    ttft_ms=current_ttft,
                                )
                                is_first_token = False
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.error("Error in Groq streaming request: %s", e)
                raise
