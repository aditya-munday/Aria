"""Pipeline and visual presence state definitions for Aria."""

from enum import Enum


class AssistantMode(str, Enum):
    """Active persona and visual theme mode."""

    ARIA = "aria"
    JARVIS = "jarvis"


class PipelineState(str, Enum):
    """Runtime voice pipeline states."""

    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    DELEGATING = "delegating"
    CONFIRMATION_REQUIRED = "confirmation_required"
    MEDIA_REACTIVE = "media_reactive"
