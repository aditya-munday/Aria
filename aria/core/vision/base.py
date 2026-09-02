"""Abstract base classes and data models for screen awareness and vision control."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ScreenFrame:
    """Captured screen or window frame context."""

    image_bytes: bytes = b""
    mime_type: str = "image/png"
    width: int = 1920
    height: int = 1080
    active_window_title: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ScreenCaptureProvider(ABC):
    """Abstract interface for screen capture."""

    @abstractmethod
    def capture_screen(self) -> ScreenFrame | None:
        """Capture the full primary display."""
        pass

    @abstractmethod
    def capture_active_window(self) -> ScreenFrame | None:
        """Capture the currently focused application window."""
        pass


class VisionAnalyzer(ABC):
    """Abstract interface for multimodal vision analysis."""

    @abstractmethod
    async def analyze_frame(self, frame: ScreenFrame, prompt: str) -> str:
        """Analyze a screen frame and return textual descriptions or extracted data."""
        pass
