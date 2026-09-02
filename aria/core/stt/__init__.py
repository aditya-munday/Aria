"""Streaming Speech-to-Text interfaces and clients."""

from aria.core.stt.base import StreamingSTT, STTResult
from aria.core.stt.mock_stt import MockStreamingSTT
from aria.core.stt.smallest_stt import SmallestStreamingSTT

__all__ = [
    "MockStreamingSTT",
    "STTResult",
    "SmallestStreamingSTT",
    "StreamingSTT",
]
