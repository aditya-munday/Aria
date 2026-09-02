"""Unit tests for streaming STT."""

import pytest

from aria.core.stt.mock_stt import MockStreamingSTT


@pytest.mark.asyncio
@pytest.mark.unit
async def test_mock_stt_streaming_results() -> None:
    stt = MockStreamingSTT("Turn on the living room lights")
    await stt.connect()
    await stt.send_audio(b"\x00" * 1024)

    results = []
    async for res in stt.receive_transcripts():
        results.append(res)

    assert len(results) >= 1
    final_res = results[-1]
    assert final_res.is_final is True
    assert final_res.text == "Turn on the living room lights"
    assert final_res.confidence > 0.9

    await stt.finish_stream()
    await stt.close()
