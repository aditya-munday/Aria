"""Mock wake word detector for CI and automated testing."""

from aria.core.pipeline.state import AssistantMode
from aria.core.wake.base import WakeWordDetector, WakeWordResult


class MockWakeWordDetector(WakeWordDetector):
    """Programmatically controllable wake word detector for testing."""

    def __init__(self) -> None:
        self._next_detection: WakeWordResult | None = None
        self._frames_processed = 0

    def trigger(
        self,
        wake_word: str = "aria",
        mode: AssistantMode = AssistantMode.ARIA,
        confidence: float = 0.95,
    ) -> None:
        """Queue a synthetic wake word event for the next frame."""
        self._next_detection = WakeWordResult(
            name=wake_word,
            mode=mode,
            confidence=confidence,
        )

    def process_frame(self, audio_chunk: bytes) -> WakeWordResult | None:
        """Process frame and return queued wake result if triggered."""
        self._frames_processed += 1
        _ = len(audio_chunk)
        if self._next_detection:
            result = self._next_detection
            self._next_detection = None
            return result
        return None

    def reset(self) -> None:
        """Reset mock state."""
        self._next_detection = None
        self._frames_processed = 0
