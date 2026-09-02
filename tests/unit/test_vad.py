"""Unit tests for Voice Activity Detection."""

import pytest

from aria.core.vad.mock_vad import MockVADDetector
from aria.core.vad.silero import SileroVADDetector


@pytest.mark.unit
def test_mock_vad_speech_and_end_of_utterance() -> None:
    vad = MockVADDetector(frame_duration_ms=32.0)
    decision = vad.process_frame(b"\x00" * 1024)
    assert not decision.is_speech
    assert not decision.is_end_of_utterance

    # Simulate speaking
    vad.set_speech_state(True)
    decision1 = vad.process_frame(b"\x00" * 1024)
    assert decision1.is_speech
    assert decision1.speech_duration_ms == 32.0

    decision2 = vad.process_frame(b"\x00" * 1024)
    assert decision2.is_speech
    assert decision2.speech_duration_ms == 64.0

    # Trigger end of utterance
    vad.trigger_end_of_utterance()
    decision3 = vad.process_frame(b"\x00" * 1024)
    assert decision3.is_end_of_utterance


@pytest.mark.unit
def test_silero_vad_fallback_uninitialized() -> None:
    vad = SileroVADDetector()
    decision = vad.process_frame(b"\x00" * 1024)
    assert not decision.is_speech
    assert decision.speech_probability == 0.0
    vad.reset()
