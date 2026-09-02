"""Audio player and visual analysis bridge."""

import asyncio
import logging
from collections.abc import Callable

from aria.core.audio.analyzer import AudioAnalyzer, AudioMetrics

logger = logging.getLogger(__name__)


class AudioPlayerBridge:
    """Consumes audio byte chunks, coordinates playback, and taps frames for real-time analysis."""

    def __init__(
        self,
        analyzer: AudioAnalyzer | None = None,
        on_metrics: Callable[[AudioMetrics], None] | None = None,
    ) -> None:
        self.analyzer = analyzer or AudioAnalyzer()
        self.on_metrics = on_metrics
        self._is_playing = False
        self._play_queue: asyncio.Queue[bytes] = asyncio.Queue()

    async def play_chunk(self, audio_bytes: bytes) -> None:
        """Process chunk for visual metrics and queue for playback."""
        if not audio_bytes:
            return

        metrics = self.analyzer.analyze_frame(audio_bytes)
        if self.on_metrics:
            try:
                self.on_metrics(metrics)
            except Exception as e:
                logger.error("Error in audio metrics callback: %s", e)

        await self._play_queue.put(audio_bytes)

    def stop(self) -> None:
        """Stop playback and clear queues."""
        self._is_playing = False
        while not self._play_queue.empty():
            try:
                self._play_queue.get_nowait()
            except Exception:
                break
        self.analyzer.reset()
