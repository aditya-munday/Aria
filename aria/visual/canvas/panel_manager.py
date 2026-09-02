"""Canvas panel manager governing floating cards, layout strategies, and lifecycle."""

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class PanelLayoutStrategy(str, Enum):
    """Layout engine placement strategies for active panels."""
    CENTER = "center"   # 1 panel
    FAN = "fan"         # 2-3 panels
    GRID = "grid"       # 4+ panels
    DOCKED = "docked"   # Edge-docked with core as gravity center


@dataclass
class CanvasPanel:
    """Individual floating canvas panel card."""
    panel_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    panel_type: str = "card"  # 'card' | 'chart' | 'media' | 'terminal' | 'weather'
    content: dict[str, Any] = field(default_factory=dict)
    is_pinned: bool = False
    ttl_seconds: float = 60.0
    created_at: float = field(default_factory=time.time)
    last_interacted_at: float = field(default_factory=time.time)
    x: float = 0.5  # Normalized screen position [0.0, 1.0]
    y: float = 0.5
    width: float = 0.3
    height: float = 0.25


class CanvasPanelManager:
    """Manages ephemeral and persistent visual panels linked to Aria core presence."""

    def __init__(self, default_ttl_seconds: float = 60.0) -> None:
        self.default_ttl_seconds = default_ttl_seconds
        self.panels: dict[str, CanvasPanel] = {}

    def create_panel(
        self,
        title: str,
        panel_type: str = "card",
        content: dict[str, Any] | None = None,
        is_pinned: bool = False,
        ttl_seconds: float | None = None,
    ) -> CanvasPanel:
        """Create and register a new floating canvas panel."""
        panel = CanvasPanel(
            title=title,
            panel_type=panel_type,
            content=content or {},
            is_pinned=is_pinned,
            ttl_seconds=ttl_seconds or self.default_ttl_seconds,
        )
        self.panels[panel.panel_id] = panel
        self.recompute_layout()
        logger.info("Created canvas panel: %s ('%s')", panel.panel_id, title)
        return panel

    def dismiss_panel(self, panel_id: str) -> bool:
        """Dismiss and remove a specific panel."""
        if panel_id in self.panels:
            del self.panels[panel_id]
            self.recompute_layout()
            logger.info("Dismissed canvas panel: %s", panel_id)
            return True
        return False

    def dismiss_all(self, include_pinned: bool = False) -> int:
        """Dismiss all unpinned panels (or all if include_pinned=True)."""
        to_remove = [
            pid for pid, p in self.panels.items()
            if include_pinned or not p.is_pinned
        ]
        for pid in to_remove:
            del self.panels[pid]
        self.recompute_layout()
        return len(to_remove)

    def pin_panel(self, panel_id: str) -> bool:
        """Pin a panel to prevent auto-expiry."""
        if panel_id in self.panels:
            self.panels[panel_id].is_pinned = True
            return True
        return False

    def unpin_panel(self, panel_id: str) -> bool:
        """Unpin a panel allowing normal auto-expiry."""
        if panel_id in self.panels:
            self.panels[panel_id].is_pinned = False
            self.panels[panel_id].last_interacted_at = time.time()
            return True
        return False

    def prune_expired(self) -> int:
        """Remove panels exceeding TTL that are not pinned."""
        now = time.time()
        expired = [
            pid for pid, p in self.panels.items()
            if not p.is_pinned and (now - p.last_interacted_at) > p.ttl_seconds
        ]
        for pid in expired:
            del self.panels[pid]
        if expired:
            self.recompute_layout()
        return len(expired)

    def recompute_layout(self) -> PanelLayoutStrategy:
        """Calculate spatial coordinates for all active panels based on density."""
        count = len(self.panels)
        panel_list = list(self.panels.values())

        if count == 0:
            return PanelLayoutStrategy.CENTER
        if count == 1:
            panel_list[0].x = 0.5
            panel_list[0].y = 0.5
            return PanelLayoutStrategy.CENTER
        if count in (2, 3):
            # Fan layout
            spacing = 0.8 / count
            for i, p in enumerate(panel_list):
                p.x = 0.2 + (i * spacing)
                p.y = 0.5
            return PanelLayoutStrategy.FAN
        # 4+ panels -> Grid layout
        cols = 2
        for i, p in enumerate(panel_list):
            row = i // cols
            col = i % cols
            p.x = 0.3 + (col * 0.4)
            p.y = 0.3 + (row * 0.35)
        return PanelLayoutStrategy.GRID

    def get_active_panel_ids(self) -> list[str]:
        """Return list of active panel IDs."""
        return list(self.panels.keys())
