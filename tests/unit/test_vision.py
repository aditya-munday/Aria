"""Unit tests for screen awareness, vision tools, and capture providers."""

import pytest

from aria.core.vision.base import ScreenFrame
from aria.core.vision.mock_provider import (
    MockScreenCaptureProvider,
    MockVisionAnalyzer,
)
from aria.core.vision.provider import DesktopScreenCaptureProvider
from aria.core.vision.tools import VisionToolHandler


@pytest.mark.asyncio
@pytest.mark.unit
async def test_mock_vision_capture_and_analysis() -> None:
    provider = MockScreenCaptureProvider(default_window_title="VS Code - orchestrator.py")
    analyzer = MockVisionAnalyzer()
    handler = VisionToolHandler(capture_provider=provider, vision_analyzer=analyzer)

    result = await handler.handle_inspect_screen(
        query="What function is on line 20?", target="active_window"
    )
    assert "VS Code - orchestrator.py" in result
    assert len(analyzer.analyzed_prompts) == 1
    assert analyzer.analyzed_prompts[0] == "What function is on line 20?"


@pytest.mark.unit
def test_desktop_capture_provider_graceful_fallback() -> None:
    # On headless CI without display server/mss, returns None gracefully
    provider = DesktopScreenCaptureProvider()
    frame = provider.capture_screen()
    # Frame is either ScreenFrame or None
    assert frame is None or isinstance(frame, ScreenFrame)
