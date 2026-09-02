"""Mock streaming STT client for unit tests and CI."""

import asyncio
from collections.abc import AsyncIterator

from aria.core.stt.base import StreamingSTT, STTResult


class MockStreamingSTT(StreamingSTT):
    """Mock STT returning predetermined partials and finals without network dependencies."""

    def __init__(self, transcript_to_emit: str = "Hello Aria, what is the system status?") -> None:
        self.transcript_to_emit = transcript_to_emit
        self._connected = False
        self._audio_chunks_received = 0

    def set_transcript(self, text: str) -> None:
        """Set the transcript text to emit on next run."""
        self.transcript_to_emit = text

    async def connect(self) -> None:
        """Simulate connect."""
        self._connected = True

    async def send_audio(self, audio_chunk: bytes) -> None:
        """Record received audio chunks."""
        self._audio_chunks_received += 1
        _ = len(audio_chunk)

    async def receive_transcripts(self) -> AsyncIterator[STTResult]:
        """Yield a partial and then a final transcript."""
        words = self.transcript_to_emit.split()
        if len(words) > 1:
            partial_text = " ".join(words[: len(words) // 2])
            await asyncio.sleep(0.005)
            yield STTResult(
                text=partial_text,
                is_final=False,
                confidence=0.85,
                latency_ms=10.0,
            )

        await asyncio.sleep(0.005)
        yield STTResult(
            text=self.transcript_to_emit,
            is_final=True,
            confidence=0.98,
            latency_ms=20.0,
        )

    async def finish_stream(self) -> None:
        """Simulate stream completion."""
        pass

    async def close(self) -> None:
        """Simulate close."""
        self._connected = False
