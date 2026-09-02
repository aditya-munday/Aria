"""System configuration and user preferences manager."""

import logging
from dataclasses import dataclass
from typing import Any

from aria.core.pipeline.state import AssistantMode

logger = logging.getLogger(__name__)


@dataclass
class AriaConfig:
    """Runtime configuration properties."""

    default_mode: AssistantMode = AssistantMode.ARIA
    wake_sensitivity: float = 0.5
    voice_speed: float = 1.0
    voice_id: str = "aria-v1-warm"
    reduce_motion: bool = False
    enable_ambient_glow: bool = True
    max_history_turns: int = 5000
    confirmation_timeout_seconds: float = 10.0


class ConfigManager:
    """Manages application settings and persistent synchronization."""

    def __init__(self, memory_store: Any = None) -> None:
        self.memory_store = memory_store
        self.config = AriaConfig()
        self.load_preferences()

    def load_preferences(self) -> AriaConfig:
        """Load stored preferences from database."""
        if not self.memory_store or not hasattr(self.memory_store, "get_preference"):
            return self.config

        pref_mode = self.memory_store.get_preference("default_mode")
        if pref_mode:
            try:
                self.config.default_mode = AssistantMode(pref_mode)
            except ValueError:
                pass

        pref_reduce_motion = self.memory_store.get_preference("reduce_motion")
        if pref_reduce_motion is not None:
            self.config.reduce_motion = str(pref_reduce_motion).lower() in ("true", "1")

        pref_voice_id = self.memory_store.get_preference("voice_id")
        if pref_voice_id:
            self.config.voice_id = str(pref_voice_id)

        return self.config

    def set_preference(self, key: str, value: Any) -> None:
        """Update and persist a specific user preference."""
        if hasattr(self.config, key):
            setattr(self.config, key, value)

        if self.memory_store and hasattr(self.memory_store, "set_preference"):
            val_str = str(value.value if hasattr(value, "value") else value)
            self.memory_store.set_preference(key, val_str)
            logger.info("Persisted preference '%s' = '%s'", key, val_str)
