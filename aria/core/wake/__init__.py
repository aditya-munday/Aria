"""Wake word detection interfaces and engines."""

from aria.core.wake.base import WakeWordDetector, WakeWordResult
from aria.core.wake.detector import OpenWakeWordDetector
from aria.core.wake.mock_detector import MockWakeWordDetector

__all__ = [
    "MockWakeWordDetector",
    "OpenWakeWordDetector",
    "WakeWordDetector",
    "WakeWordResult",
]
