"""Unit tests for canvas floating panels and layout engine."""

import time

import pytest

from aria.visual.canvas.panel_manager import (
    CanvasPanelManager,
    PanelLayoutStrategy,
)


@pytest.mark.unit
def test_canvas_panel_lifecycle_and_pinning() -> None:
    manager = CanvasPanelManager(default_ttl_seconds=0.1)

    panel1 = manager.create_panel(title="System Metrics", panel_type="card")
    assert panel1.panel_id in manager.panels
    assert panel1.title == "System Metrics"
    assert not panel1.is_pinned

    # Pin panel
    assert manager.pin_panel(panel1.panel_id) is True
    assert manager.panels[panel1.panel_id].is_pinned is True

    # Sleep past TTL
    time.sleep(0.12)
    pruned = manager.prune_expired()
    # Pinned panel is preserved
    assert pruned == 0
    assert panel1.panel_id in manager.panels

    # Unpin and prune
    manager.unpin_panel(panel1.panel_id)
    # Manually backdate last_interacted_at to trigger expiry
    manager.panels[panel1.panel_id].last_interacted_at = time.time() - 1.0
    pruned_after = manager.prune_expired()
    assert pruned_after == 1
    assert panel1.panel_id not in manager.panels


@pytest.mark.unit
def test_canvas_panel_layout_strategies() -> None:
    manager = CanvasPanelManager()

    # 1 panel -> CENTER
    p1 = manager.create_panel("Panel 1")
    strategy1 = manager.recompute_layout()
    assert strategy1 == PanelLayoutStrategy.CENTER
    assert p1.x == 0.5

    # 2 panels -> FAN
    _ = manager.create_panel("Panel 2")
    strategy2 = manager.recompute_layout()
    assert strategy2 == PanelLayoutStrategy.FAN

    # 4 panels -> GRID
    manager.create_panel("Panel 3")
    manager.create_panel("Panel 4")
    strategy4 = manager.recompute_layout()
    assert strategy4 == PanelLayoutStrategy.GRID

    # Dismiss all
    dismissed = manager.dismiss_all(include_pinned=True)
    assert dismissed == 4
    assert len(manager.panels) == 0
