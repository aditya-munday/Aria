"""Unit tests for wake word detection."""

import pytest

from aria.core.pipeline.state import AssistantMode
from aria.core.wake.detector import OpenWakeWordDetector
from aria.core.wake.mock_detector import MockWakeWordDetector


@pytest.mark.unit
def test_mock_wake_detector_trigger_aria() -> None:
    detector = MockWakeWordDetector()
    assert detector.process_frame(b"\x00" * 1024) is None

    detector.trigger(wake_word="aria", mode=AssistantMode.ARIA, confidence=0.92)
    result = detector.process_frame(b"\x00" * 1024)

    assert result is not None
    assert result.name == "aria"
    assert result.mode == AssistantMode.ARIA
    assert result.confidence == 0.92

    # Verify single-shot behavior
    assert detector.process_frame(b"\x00" * 1024) is None


@pytest.mark.unit
def test_mock_wake_detector_trigger_jarvis() -> None:
    detector = MockWakeWordDetector()
    detector.trigger(wake_word="jarvis", mode=AssistantMode.JARVIS, confidence=0.98)
    result = detector.process_frame(b"\x00" * 1024)

    assert result is not None
    assert result.name == "jarvis"
    assert result.mode == AssistantMode.JARVIS
    assert result.confidence == 0.98


@pytest.mark.unit
def test_openwakeword_detector_fallback() -> None:
    detector = OpenWakeWordDetector()
    # Uninitialized returns None safely
    assert detector.process_frame(b"\x00" * 1024) is None
    detector.reset()
