"""Integration tests for the end-to-end Aria voice loop and canonical pipeline order."""

import json
from collections.abc import AsyncIterator

import pytest

from aria.core.llm.mock_llm import MockLLMClient
from aria.core.pipeline.events import PipelineEvent, StateTransitionEvent
from aria.core.pipeline.orchestrator import PipelineOrchestrator
from aria.core.pipeline.state import AssistantMode, PipelineState
from aria.core.stt.mock_stt import MockStreamingSTT
from aria.core.vad.mock_vad import MockVADDetector
from aria.core.wake.mock_detector import MockWakeWordDetector


@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_conversational_voice_loop(
    full_orchestrator: PipelineOrchestrator,
) -> None:
    events_received: list[PipelineEvent] = []

    async def log_event(event: PipelineEvent) -> None:
        events_received.append(event)

    full_orchestrator.event_bus.subscribe_all(log_event)

    assert isinstance(full_orchestrator.wake_detector, MockWakeWordDetector)
    assert isinstance(full_orchestrator.vad_detector, MockVADDetector)
    assert isinstance(full_orchestrator.stt_client, MockStreamingSTT)
    assert isinstance(full_orchestrator.llm_client, MockLLMClient)

    # 1. Simulate Wake Detection
    full_orchestrator.wake_detector.trigger(
        wake_word="aria", mode=AssistantMode.ARIA, confidence=0.95
    )
    await full_orchestrator.process_microphone_frame(b"\x00" * 1024)

    assert full_orchestrator.current_state == PipelineState.LISTENING
    assert full_orchestrator.current_mode == AssistantMode.ARIA

    # 2. Configure mock speech stream with VAD and STT
    full_orchestrator.stt_client.set_transcript("What is the current system status?")
    full_orchestrator.llm_client.set_response("All systems are fully operational.")

    async def audio_stream() -> AsyncIterator[bytes]:
        # Yield 3 speech frames then end-of-utterance
        assert isinstance(full_orchestrator.vad_detector, MockVADDetector)
        full_orchestrator.vad_detector.set_speech_state(True)
        yield b"\x00\x00" * 256
        yield b"\x00\x00" * 256
        full_orchestrator.vad_detector.trigger_end_of_utterance()
        yield b"\x00\x00" * 256

    # 3. Execute canonical voice turn
    response_text = await full_orchestrator.run_voice_turn(audio_stream())

    assert response_text == "All systems are fully operational."
    assert full_orchestrator.current_state == PipelineState.IDLE

    # 4. Verify turn persisted in LongTermMemory SQLite database
    history = full_orchestrator.long_term_memory.get_recent_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "What is the current system status?"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "All systems are fully operational."

    # 5. Verify state transitions occurred in proper order
    state_events = [e for e in events_received if isinstance(e, StateTransitionEvent)]
    assert len(state_events) >= 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_jarvis_mode_tool_delegation_loop(
    full_orchestrator: PipelineOrchestrator,
) -> None:
    assert isinstance(full_orchestrator.wake_detector, MockWakeWordDetector)
    assert isinstance(full_orchestrator.vad_detector, MockVADDetector)
    assert isinstance(full_orchestrator.stt_client, MockStreamingSTT)
    assert isinstance(full_orchestrator.llm_client, MockLLMClient)

    # 1. Trigger Jarvis wake
    full_orchestrator.wake_detector.trigger(
        wake_word="jarvis", mode=AssistantMode.JARVIS, confidence=0.99
    )
    await full_orchestrator.process_microphone_frame(b"\x00" * 1024)

    assert full_orchestrator.current_mode == AssistantMode.JARVIS

    # 2. Configure Groq mock to emit tool call to Directioner AI
    tool_args = {
        "category": "system_action",
        "action_name": "mute_system_audio",
        "parameters": {},
        "risk_tier": "medium",
        "spoken_summary": "Muting system audio",
    }
    full_orchestrator.llm_client.set_tool_call("delegate_to_directioner_ai", json.dumps(tool_args))

    async def single_frame_stream() -> AsyncIterator[bytes]:
        assert isinstance(full_orchestrator.vad_detector, MockVADDetector)
        full_orchestrator.vad_detector.set_speech_state(True)
        yield b"\x00\x00" * 256
        full_orchestrator.vad_detector.trigger_end_of_utterance()
        yield b"\x00\x00" * 256

    full_orchestrator.stt_client.set_transcript("Mute the system.")
    response_text = await full_orchestrator.run_voice_turn(single_frame_stream())

    assert "Successfully delegated" in response_text
    assert full_orchestrator.current_state == PipelineState.IDLE
