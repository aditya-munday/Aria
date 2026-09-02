"""Latency benchmark harness measuring per-component and end-to-end pipeline execution."""

import time
from collections.abc import AsyncIterator

import pytest

from aria.core.audio.analyzer import AudioAnalyzer
from aria.core.llm.mock_llm import MockLLMClient
from aria.core.pipeline.orchestrator import PipelineOrchestrator
from aria.core.stt.mock_stt import MockStreamingSTT
from aria.core.vad.mock_vad import MockVADDetector


@pytest.mark.benchmark
def test_audio_analyzer_frame_latency(audio_analyzer: AudioAnalyzer) -> None:
    """Benchmark raw frame analysis latency for 1000 consecutive 512-sample frames."""
    dummy_frame = b"\x00\x00" * 512
    iterations = 1000

    start_time = time.perf_counter()
    for _ in range(iterations):
        audio_analyzer.analyze_frame(dummy_frame)
    total_time = time.perf_counter() - start_time

    avg_latency_ms = (total_time / iterations) * 1000.0
    print(f"\n[BENCHMARK] AudioAnalyzer avg latency: {avg_latency_ms:.4f} ms per 512-sample frame")
    assert avg_latency_ms < 1.0  # Must be well under 1ms per frame for real-time 60fps budget


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_end_to_end_mock_pipeline_turn_latency(
    full_orchestrator: PipelineOrchestrator,
) -> None:
    """Benchmark end-to-end synthetic pipeline turn execution latency."""
    assert isinstance(full_orchestrator.stt_client, MockStreamingSTT)
    assert isinstance(full_orchestrator.llm_client, MockLLMClient)
    assert isinstance(full_orchestrator.vad_detector, MockVADDetector)

    full_orchestrator.stt_client.set_transcript("What is the time?")
    full_orchestrator.llm_client.set_response("The time is 12:00 PM.")

    async def audio_stream() -> AsyncIterator[bytes]:
        assert isinstance(full_orchestrator.vad_detector, MockVADDetector)
        full_orchestrator.vad_detector.set_speech_state(True)
        yield b"\x00\x00" * 256
        full_orchestrator.vad_detector.trigger_end_of_utterance()
        yield b"\x00\x00" * 256

    start_time = time.perf_counter()
    reply = await full_orchestrator.run_voice_turn(audio_stream())
    total_time_ms = (time.perf_counter() - start_time) * 1000.0

    print(f"\n[BENCHMARK] Synthetic end-to-end turn latency: {total_time_ms:.2f} ms")
    assert reply == "The time is 12:00 PM."
    assert total_time_ms < 500.0  # Synthetic mock pipeline should complete in under 500ms
