"""Streaming Text-to-Speech interfaces and clients."""

from aria.core.tts.base import StreamingTTS, TTSAudioChunk
from aria.core.tts.mock_tts import MockStreamingTTS
from aria.core.tts.smallest_tts import SmallestStreamingTTS

__all__ = [
    "MockStreamingTTS",
    "SmallestStreamingTTS",
    "StreamingTTS",
    "TTSAudioChunk",
]
