"""Mock streaming TTS client for unit tests and CI."""

import asyncio
from collections.abc import AsyncIterator

from aria.core.tts.base import StreamingTTS, TTSAudioChunk


class MockStreamingTTS(StreamingTTS):
    """Mock TTS generator yielding synthetic PCM byte chunks."""

    def __init__(self, sample_rate: int = 24000, chunk_size_bytes: int = 1024) -> None:
        self.sample_rate = sample_rate
        self.chunk_size_bytes = chunk_size_bytes
        self.recorded_tokens: list[str] = []

    async def stream_speech(
        self,
        text_stream: AsyncIterator[str],
        voice_id: str | None = None,
    ) -> AsyncIterator[TTSAudioChunk]:
        """Consume text tokens and yield mock audio frames."""
        _ = voice_id
        collected_text = []
        async for token in text_stream:
            collected_text.append(token)
            self.recorded_tokens.append(token)

        # Generate synthetic audio chunks
        synthetic_frame = b"\x00\x00" * (self.chunk_size_bytes // 2)

        # First chunk
        await asyncio.sleep(0.005)
        yield TTSAudioChunk(
            audio_bytes=synthetic_frame,
            sample_rate=self.sample_rate,
            is_first_chunk=True,
            is_final_chunk=False,
            ttfb_ms=10.0,
        )

        # Second chunk
        await asyncio.sleep(0.005)
        yield TTSAudioChunk(
            audio_bytes=synthetic_frame,
            sample_rate=self.sample_rate,
            is_first_chunk=False,
            is_final_chunk=False,
            ttfb_ms=0.0,
        )

        # Final chunk
        yield TTSAudioChunk(
            audio_bytes=b"",
            sample_rate=self.sample_rate,
            is_first_chunk=False,
            is_final_chunk=True,
            ttfb_ms=0.0,
        )
