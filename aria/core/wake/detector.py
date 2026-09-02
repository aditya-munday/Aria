"""openWakeWord dual-model detector implementation for Aria and Jarvis."""

import logging
from typing import Any

import numpy as np

from aria.core.pipeline.state import AssistantMode
from aria.core.wake.base import WakeWordDetector, WakeWordResult

logger = logging.getLogger(__name__)


class OpenWakeWordDetector(WakeWordDetector):
    """Dual wake-word detector using openWakeWord runtime models."""

    def __init__(
        self,
        aria_threshold: float = 0.5,
        jarvis_threshold: float = 0.5,
        model_paths: list[str] | None = None,
    ) -> None:
        self.aria_threshold = aria_threshold
        self.jarvis_threshold = jarvis_threshold
        self.model_paths = model_paths or []
        self._model: Any = None
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize the openWakeWord model engine."""
        try:
            import openwakeword  # type: ignore[import-not-found,import-untyped]
            from openwakeword.model import Model  # type: ignore[import-not-found,import-untyped]

            logger.info("Initializing openWakeWord with models: %s", self.model_paths)
            if self.model_paths:
                self._model = Model(wakeword_models=self.model_paths)
            else:
                # Default models if available
                openwakeword.utils.download_models()
                self._model = Model()
            self._initialized = True
            return True
        except ImportError:
            logger.warning("openwakeword not installed. Falling back to uninitialized state.")
            self._initialized = False
            return False
        except Exception as e:
            logger.error("Failed to initialize openWakeWord: %s", e)
            self._initialized = False
            return False

    def process_frame(self, audio_chunk: bytes) -> WakeWordResult | None:
        """Process 16-bit 16kHz PCM audio chunk and evaluate dual wake models."""
        if not self._initialized or self._model is None:
            return None

        # Convert raw PCM bytes to int16 numpy array
        audio_array = np.frombuffer(audio_chunk, dtype=np.int16)

        try:
            predictions = self._model.predict(audio_array)
            for model_name, score in predictions.items():
                lower_name = model_name.lower()
                if "aria" in lower_name and score >= self.aria_threshold:
                    logger.info("Aria wake word detected with score %f", score)
                    return WakeWordResult(
                        name="aria",
                        mode=AssistantMode.ARIA,
                        confidence=float(score),
                    )
                if "jarvis" in lower_name and score >= self.jarvis_threshold:
                    logger.info("Jarvis wake word detected with score %f", score)
                    return WakeWordResult(
                        name="jarvis",
                        mode=AssistantMode.JARVIS,
                        confidence=float(score),
                    )
        except Exception as e:
            logger.error("Error during wake word frame prediction: %s", e)

        return None

    def reset(self) -> None:
        """Reset internal openWakeWord buffer."""
        if self._initialized and self._model is not None:
            self._model.reset()
