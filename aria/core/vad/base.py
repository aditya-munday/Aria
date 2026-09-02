"""Abstract base class for Voice Activity Detection (VAD)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class VADDecision:
    """Decision emitted by VAD after frame analysis."""

    is_speech: bool
    speech_probability: float
    is_end_of_utterance: bool = False
    speech_duration_ms: float = 0.0
    silence_duration_ms: float = 0.0


class VADDetector(ABC):
    """Abstract interface for voice activity detectors."""

    @abstractmethod
    def process_frame(self, audio_chunk: bytes) -> VADDecision:
        """Process an audio frame and evaluate speech activity and end-of-utterance."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset internal speech/silence tracking state."""
        pass
