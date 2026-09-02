"""smallest.ai streaming Speech-to-Text client implementation."""

import json
import logging
import time
from collections.abc import AsyncIterator
from typing import Any

from aria.core.stt.base import StreamingSTT, STTResult

logger = logging.getLogger(__name__)


class SmallestStreamingSTT(StreamingSTT):
    """Streaming STT client utilizing smallest.ai WebSocket API."""

    def __init__(
        self,
        api_key: str,
        endpoint_url: str = "wss://waves-api.smallest.ai/api/v1/lightning/get_speech",
        sample_rate: int = 16000,
        language: str = "en",
    ) -> None:
        self.api_key = api_key
        self.endpoint_url = endpoint_url
        self.sample_rate = sample_rate
        self.language = language

        self._websocket: Any = None
        self._is_connected = False
        self._stream_start_time = 0.0

    async def connect(self) -> None:
        """Connect to smallest.ai streaming WebSocket."""
        try:
            import websockets

            headers = {"Authorization": f"Bearer {self.api_key}"}
            self._websocket = await websockets.connect(
                self.endpoint_url,
                extra_headers=headers,
            )
            self._is_connected = True
            self._stream_start_time = time.time()
            logger.info("Connected to smallest.ai streaming STT.")
        except Exception as e:
            logger.error("Failed to connect to smallest.ai STT: %s", e)
            self._is_connected = False
            raise

    async def send_audio(self, audio_chunk: bytes) -> None:
        """Stream 16-bit PCM audio frame over WebSocket."""
        if not self._is_connected or self._websocket is None:
            raise RuntimeError("STT client is not connected.")

        await self._websocket.send(audio_chunk)

    async def receive_transcripts(self) -> AsyncIterator[STTResult]:
        """Listen on WebSocket and yield partial and final transcripts."""
        if not self._is_connected or self._websocket is None:
            return

        try:
            async for message in self._websocket:
                data = json.loads(message)
                text = data.get("transcript", "") or data.get("text", "")
                is_final = data.get("is_final", False) or data.get("final", False)
                confidence = float(data.get("confidence", 1.0))
                latency_ms = (time.time() - self._stream_start_time) * 1000.0

                if text:
                    yield STTResult(
                        text=text,
                        is_final=is_final,
                        confidence=confidence,
                        latency_ms=latency_ms,
                    )
                if is_final:
                    break
        except Exception as e:
            logger.error("Error receiving STT transcripts: %s", e)
            raise

    async def finish_stream(self) -> None:
        """Send EOF message to indicate end of utterance."""
        if self._is_connected and self._websocket is not None:
            try:
                await self._websocket.send(json.dumps({"eof": True}))
            except Exception as e:
                logger.warning("Error sending EOF to STT: %s", e)

    async def close(self) -> None:
        """Close WebSocket connection."""
        if self._websocket is not None:
            try:
                await self._websocket.close()
            except Exception:
                pass
            self._is_connected = False
            self._websocket = None
