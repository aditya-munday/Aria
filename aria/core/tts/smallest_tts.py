"""smallest.ai streaming Text-to-Speech client implementation."""

import json
import logging
import time
from collections.abc import AsyncIterator
from typing import Any

from aria.core.tts.base import StreamingTTS, TTSAudioChunk

logger = logging.getLogger(__name__)


class SmallestStreamingTTS(StreamingTTS):
    """Streaming TTS client connecting to smallest.ai Waves Lightning API."""

    def __init__(
        self,
        api_key: str,
        endpoint_url: str = "wss://waves-api.smallest.ai/api/v1/lightning/get_speech",
        sample_rate: int = 24000,
        default_voice_id: str = "emily",
    ) -> None:
        self.api_key = api_key
        self.endpoint_url = endpoint_url
        self.sample_rate = sample_rate
        self.default_voice_id = default_voice_id

    async def stream_speech(
        self,
        text_stream: AsyncIterator[str],
        voice_id: str | None = None,
    ) -> AsyncIterator[TTSAudioChunk]:
        """Stream text tokens to smallest.ai WebSocket and yield audio chunks."""
        import websockets

        target_voice = voice_id or self.default_voice_id
        start_time = time.time()
        is_first_chunk = True

        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            async with websockets.connect(
                self.endpoint_url,
                extra_headers=headers,
            ) as ws:
                # Send configuration handshake
                init_config = {
                    "voice_id": target_voice,
                    "sample_rate": self.sample_rate,
                    "speed": 1.0,
                }
                await ws.send(json.dumps(init_config))

                # Background task to send text tokens as they arrive
                async def sender() -> None:
                    try:
                        async for token in text_stream:
                            if token:
                                await ws.send(json.dumps({"text": token}))
                        await ws.send(json.dumps({"flush": True}))
                    except Exception as e:
                        logger.error("Error sending text to TTS: %s", e)

                import asyncio

                send_task = asyncio.create_task(sender())

                try:
                    async for message in ws:
                        if isinstance(message, bytes):
                            current_ttfb = (
                                (time.time() - start_time) * 1000.0 if is_first_chunk else 0.0
                            )
                            yield TTSAudioChunk(
                                audio_bytes=message,
                                sample_rate=self.sample_rate,
                                is_first_chunk=is_first_chunk,
                                is_final_chunk=False,
                                ttfb_ms=current_ttfb,
                            )
                            is_first_chunk = False
                        elif isinstance(message, str):
                            data: dict[str, Any] = json.loads(message)
                            if data.get("is_final") or data.get("end_of_stream"):
                                break
                finally:
                    await send_task
                    yield TTSAudioChunk(
                        audio_bytes=b"",
                        sample_rate=self.sample_rate,
                        is_first_chunk=False,
                        is_final_chunk=True,
                        ttfb_ms=0.0,
                    )
        except Exception as e:
            logger.error("Error during smallest.ai TTS stream: %s", e)
            raise
