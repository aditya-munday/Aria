"""Mock VAD detector for automated unit and integration tests."""

from aria.core.vad.base import VADDecision, VADDetector


class MockVADDetector(VADDetector):
    """Controllable VAD for simulating speech streams and end-of-utterance."""

    def __init__(self, frame_duration_ms: float = 32.0) -> None:
        self.frame_duration_ms = frame_duration_ms
        self._simulate_speech = False
        self._force_end_of_utterance = False
        self._speech_duration_ms = 0.0
        self._silence_duration_ms = 0.0

    def set_speech_state(self, is_speech: bool) -> None:
        """Set whether incoming frames should register as active speech."""
        self._simulate_speech = is_speech

    def trigger_end_of_utterance(self) -> None:
        """Signal end of utterance on the next frame."""
        self._force_end_of_utterance = True

    def process_frame(self, audio_chunk: bytes) -> VADDecision:
        """Process frame according to mock settings."""
        _ = len(audio_chunk)
        if self._simulate_speech:
            self._speech_duration_ms += self.frame_duration_ms
            self._silence_duration_ms = 0.0
            prob = 0.95
        else:
            self._silence_duration_ms += self.frame_duration_ms
            prob = 0.05

        end_of_utterance = self._force_end_of_utterance
        if self._force_end_of_utterance:
            self._force_end_of_utterance = False
            self._simulate_speech = False

        return VADDecision(
            is_speech=self._simulate_speech,
            speech_probability=prob,
            is_end_of_utterance=end_of_utterance,
            speech_duration_ms=self._speech_duration_ms,
            silence_duration_ms=self._silence_duration_ms,
        )

    def reset(self) -> None:
        """Reset mock state."""
        self._simulate_speech = False
        self._force_end_of_utterance = False
        self._speech_duration_ms = 0.0
        self._silence_duration_ms = 0.0
