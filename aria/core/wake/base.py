"""Abstract base class for wake word detection."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from aria.core.pipeline.state import AssistantMode


@dataclass
class WakeWordResult:
    """Result emitted upon wake word detection."""

    name: str
    mode: AssistantMode
    confidence: float


class WakeWordDetector(ABC):
    """Abstract interface for local wake word detectors."""

    @abstractmethod
    def process_frame(self, audio_chunk: bytes) -> WakeWordResult | None:
        """Process a 16-bit PCM audio frame and return result if wake word is detected."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset internal detector state."""
        pass
