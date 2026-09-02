"""Abstract base class for streaming Text-to-Speech (TTS)."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass
class TTSAudioChunk:
    """Audio byte chunk emitted by streaming TTS engine."""

    audio_bytes: bytes
    sample_rate: int = 24000
    is_first_chunk: bool = False
    is_final_chunk: bool = False
    ttfb_ms: float = 0.0


class StreamingTTS(ABC):
    """Abstract interface for streaming text-to-speech engines."""

    @abstractmethod
    def stream_speech(
        self,
        text_stream: AsyncIterator[str],
        voice_id: str | None = None,
    ) -> AsyncIterator[TTSAudioChunk]:
        """Convert an incoming stream of text tokens into an audio byte stream."""
        pass
