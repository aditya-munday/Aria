"""Event bus and typed events for the Aria voice pipeline."""

import asyncio
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from aria.core.pipeline.state import AssistantMode, PipelineState


@dataclass
class PipelineEvent:
    """Base event emitted by pipeline components."""

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class WakeWordDetectedEvent(PipelineEvent):
    """Emitted when openWakeWord identifies an activation phrase."""

    wake_word: str = "aria"
    mode: AssistantMode = AssistantMode.ARIA
    confidence: float = 1.0


@dataclass
class VADStateChangedEvent(PipelineEvent):
    """Emitted on speech start or end-of-utterance detection."""

    is_speech: bool = False
    speech_duration_ms: float = 0.0


@dataclass
class STTTranscriptEvent(PipelineEvent):
    """Emitted when STT yields partial or final transcripts."""

    text: str = ""
    is_final: bool = False
    confidence: float = 1.0


@dataclass
class LLMTokenEvent(PipelineEvent):
    """Emitted as Groq generates streaming tokens."""

    token: str = ""
    is_first_token: bool = False
    is_complete: bool = False


@dataclass
class TTSAudioChunkEvent(PipelineEvent):
    """Emitted as smallest.ai streams audio bytes."""

    audio_bytes: bytes = b""
    sample_rate: int = 24000
    is_first_chunk: bool = False
    is_final_chunk: bool = False


@dataclass
class AudioAnalysisEvent(PipelineEvent):
    """Emitted by real-time audio analyzer for visual reactivity."""

    amplitude: float = 0.0
    pitch: float = 0.0
    energy: float = 0.0
    is_beat: bool = False


@dataclass
class StateTransitionEvent(PipelineEvent):
    """Emitted when pipeline or visual state transitions."""

    previous_state: PipelineState = PipelineState.IDLE
    current_state: PipelineState = PipelineState.IDLE
    mode: AssistantMode = AssistantMode.ARIA


EventHandler = Callable[[PipelineEvent], Coroutine[Any, Any, None]]


class EventBus:
    """Asynchronous pub-sub event bus for decoupled pipeline communication."""

    def __init__(self) -> None:
        self._subscribers: dict[type[PipelineEvent], list[EventHandler]] = {}
        self._global_subscribers: list[EventHandler] = []

    def subscribe(self, event_type: type[PipelineEvent], handler: EventHandler) -> None:
        """Subscribe an asynchronous handler to a specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        """Subscribe to all events across the pipeline."""
        self._global_subscribers.append(handler)

    async def emit(self, event: PipelineEvent) -> None:
        """Emit an event to all registered handlers concurrently."""
        tasks: list[asyncio.Task[None]] = []
        handlers = list(self._subscribers.get(type(event), [])) + self._global_subscribers

        for handler in handlers:
            tasks.append(asyncio.create_task(handler(event)))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=False)
