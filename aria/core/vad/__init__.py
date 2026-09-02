"""Voice Activity Detection interfaces and wrappers."""

from aria.core.vad.base import VADDecision, VADDetector
from aria.core.vad.mock_vad import MockVADDetector
from aria.core.vad.silero import SileroVADDetector

__all__ = [
    "MockVADDetector",
    "SileroVADDetector",
    "VADDecision",
    "VADDetector",
]
