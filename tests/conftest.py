"""Shared pytest fixtures for Aria tests."""

from collections.abc import Generator

import pytest

from aria.core.audio.analyzer import AudioAnalyzer
from aria.core.intent.directioner_client import DirectionerAIClient
from aria.core.llm.mock_llm import MockLLMClient
from aria.core.memory.long_term import LongTermMemory
from aria.core.memory.session import SessionMemory
from aria.core.pipeline.events import EventBus
from aria.core.pipeline.orchestrator import PipelineOrchestrator
from aria.core.stt.mock_stt import MockStreamingSTT
from aria.core.tts.mock_tts import MockStreamingTTS
from aria.core.vad.mock_vad import MockVADDetector
from aria.core.wake.mock_detector import MockWakeWordDetector
from aria.visual.overlay.state_machine import VisualStateMachine


@pytest.fixture
def mock_wake() -> MockWakeWordDetector:
    return MockWakeWordDetector()


@pytest.fixture
def mock_vad() -> MockVADDetector:
    return MockVADDetector()


@pytest.fixture
def mock_stt() -> MockStreamingSTT:
    return MockStreamingSTT()


@pytest.fixture
def mock_llm() -> MockLLMClient:
    return MockLLMClient()


@pytest.fixture
def mock_tts() -> MockStreamingTTS:
    return MockStreamingTTS()


@pytest.fixture
def audio_analyzer() -> AudioAnalyzer:
    return AudioAnalyzer()


@pytest.fixture
def session_memory() -> SessionMemory:
    return SessionMemory(max_turns=50)


@pytest.fixture
def long_term_memory() -> Generator[LongTermMemory, None, None]:
    # Use isolated in-memory SQLite database
    mem = LongTermMemory(db_path=":memory:", max_history_entries=5000, max_facts_entries=1000)
    yield mem
    mem.close()


@pytest.fixture
def directioner_client() -> DirectionerAIClient:
    return DirectionerAIClient()


@pytest.fixture
def visual_state_machine() -> VisualStateMachine:
    return VisualStateMachine()


@pytest.fixture
def event_bus() -> EventBus:
    return EventBus()


@pytest.fixture
def full_orchestrator(
    mock_wake: MockWakeWordDetector,
    mock_vad: MockVADDetector,
    mock_stt: MockStreamingSTT,
    mock_llm: MockLLMClient,
    mock_tts: MockStreamingTTS,
    audio_analyzer: AudioAnalyzer,
    session_memory: SessionMemory,
    long_term_memory: LongTermMemory,
    directioner_client: DirectionerAIClient,
    visual_state_machine: VisualStateMachine,
    event_bus: EventBus,
) -> PipelineOrchestrator:
    return PipelineOrchestrator(
        wake_detector=mock_wake,
        vad_detector=mock_vad,
        stt_client=mock_stt,
        llm_client=mock_llm,
        tts_client=mock_tts,
        audio_analyzer=audio_analyzer,
        session_memory=session_memory,
        long_term_memory=long_term_memory,
        directioner_client=directioner_client,
        visual_state_machine=visual_state_machine,
        event_bus=event_bus,
    )
