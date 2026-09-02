"""Abstract base class for streaming Speech-to-Text (STT)."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass
class STTResult:
    """Transcript result emitted by STT stream."""

    text: str
    is_final: bool
    confidence: float = 1.0
    latency_ms: float = 0.0


class StreamingSTT(ABC):
    """Abstract interface for streaming speech-to-text engines."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to STT service."""
        pass

    @abstractmethod
    async def send_audio(self, audio_chunk: bytes) -> None:
        """Stream raw audio chunk to the STT backend."""
        pass

    @abstractmethod
    def receive_transcripts(self) -> AsyncIterator[STTResult]:
        """Asynchronously yield partial and final transcripts as they arrive."""
        pass

    @abstractmethod
    async def finish_stream(self) -> None:
        """Signal end of speech stream for final transcript compilation."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close connection and clean up resources."""
        pass
