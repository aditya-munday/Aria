"""Silero VAD detector implementation with end-of-utterance state tracking."""

import logging
from typing import Any

import numpy as np

from aria.core.vad.base import VADDecision, VADDetector

logger = logging.getLogger(__name__)


class SileroVADDetector(VADDetector):
    """Voice Activity Detector wrapping the Silero VAD neural model."""

    def __init__(
        self,
        threshold: float = 0.5,
        sample_rate: int = 16000,
        silence_timeout_ms: float = 500.0,
        min_speech_duration_ms: float = 250.0,
    ) -> None:
        self.threshold = threshold
        self.sample_rate = sample_rate
        self.silence_timeout_ms = silence_timeout_ms
        self.min_speech_duration_ms = min_speech_duration_ms

        self._model: Any = None
        self._initialized = False

        # State tracking
        self._is_in_speech = False
        self._current_speech_duration_ms = 0.0
        self._current_silence_duration_ms = 0.0

    def initialize(self) -> bool:
        """Initialize torch/onnx Silero VAD model."""
        try:
            import torch  # type: ignore[import-not-found,import-untyped]

            model, _ = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                force_reload=False,
                onnx=True,
            )
            self._model = model
            self._initialized = True
            logger.info("Silero VAD initialized successfully.")
            return True
        except ImportError:
            logger.warning("torch not installed. Falling back to uninitialized state.")
            self._initialized = False
            return False
        except Exception as e:
            logger.error("Failed to load Silero VAD model: %s", e)
            self._initialized = False
            return False

    def process_frame(self, audio_chunk: bytes) -> VADDecision:
        """Evaluate audio frame and calculate end-of-utterance."""
        # Frame duration calculation: length in bytes / (2 bytes per sample * sample_rate) * 1000
        frame_duration_ms = (len(audio_chunk) / (2 * self.sample_rate)) * 1000.0

        speech_prob = 0.0
        if self._initialized and self._model is not None:
            try:
                import torch

                audio_np = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
                tensor = torch.from_numpy(audio_np)
                speech_prob = float(self._model(tensor, self.sample_rate).item())
            except Exception as e:
                logger.error("Error evaluating Silero VAD frame: %s", e)
                speech_prob = 0.0

        is_speech = speech_prob >= self.threshold
        is_end_of_utterance = False

        if is_speech:
            self._is_in_speech = True
            self._current_speech_duration_ms += frame_duration_ms
            self._current_silence_duration_ms = 0.0
        else:
            if self._is_in_speech:
                self._current_silence_duration_ms += frame_duration_ms
                if (
                    self._current_speech_duration_ms >= self.min_speech_duration_ms
                    and self._current_silence_duration_ms >= self.silence_timeout_ms
                ):
                    is_end_of_utterance = True
                    self._is_in_speech = False

        return VADDecision(
            is_speech=is_speech,
            speech_probability=speech_prob,
            is_end_of_utterance=is_end_of_utterance,
            speech_duration_ms=self._current_speech_duration_ms,
            silence_duration_ms=self._current_silence_duration_ms,
        )

    def reset(self) -> None:
        """Reset utterance duration state."""
        self._is_in_speech = False
        self._current_speech_duration_ms = 0.0
        self._current_silence_duration_ms = 0.0
        if self._initialized and self._model is not None:
            try:
                self._model.reset_states()
            except Exception:
                pass
