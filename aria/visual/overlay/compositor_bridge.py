"""Abstract compositor bridge for transparent overlay rendering."""

import logging
from abc import ABC, abstractmethod

from aria.visual.overlay.state_machine import VisualStateSnapshot

logger = logging.getLogger(__name__)


class CompositorBridge(ABC):
    """Bridge communicating visual snapshots to compositor or webview canvas overlay."""

    @abstractmethod
    def push_frame(self, snapshot: VisualStateSnapshot) -> None:
        """Render a single visual frame snapshot."""
        pass

    @abstractmethod
    def set_overlay_visibility(self, visible: bool) -> None:
        """Toggle transparent overlay visibility."""
        pass


class MockCompositorBridge(CompositorBridge):
    """In-memory compositor bridge for testing and CI."""

    def __init__(self) -> None:
        self.last_snapshot: VisualStateSnapshot | None = None
        self.is_visible: bool = True
        self.frame_count: int = 0

    def push_frame(self, snapshot: VisualStateSnapshot) -> None:
        """Record pushed frame."""
        self.last_snapshot = snapshot
        self.frame_count += 1

    def set_overlay_visibility(self, visible: bool) -> None:
        """Set visibility."""
        self.is_visible = visible
