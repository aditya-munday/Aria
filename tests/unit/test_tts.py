"""Unit tests for streaming TTS."""

from collections.abc import AsyncIterator

import pytest

from aria.core.tts.mock_tts import MockStreamingTTS


@pytest.mark.asyncio
@pytest.mark.unit
async def test_mock_tts_audio_streaming() -> None:
    tts = MockStreamingTTS(sample_rate=24000)

    async def token_generator() -> AsyncIterator[str]:
        tokens = ["Good ", "evening, ", "sir."]
        for t in tokens:
            yield t

    chunks = []
    async for chunk in tts.stream_speech(token_generator()):
        chunks.append(chunk)

    assert len(chunks) == 3
    assert chunks[0].is_first_chunk is True
    assert len(chunks[0].audio_bytes) > 0
    assert chunks[0].ttfb_ms > 0
    assert chunks[-1].is_final_chunk is True
    assert tts.recorded_tokens == ["Good ", "evening, ", "sir."]
