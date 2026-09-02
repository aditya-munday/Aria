"""Groq tool definitions and handlers for screen vision queries."""

import logging
from typing import Any

from aria.core.vision.base import ScreenCaptureProvider, VisionAnalyzer

logger = logging.getLogger(__name__)

VISION_TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "inspect_screen",
            "description": "Capture and inspect the current screen or active application window to answer visual user questions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What specific visual element or information to look for on the screen.",
                    },
                    "target": {
                        "type": "string",
                        "enum": ["full_screen", "active_window"],
                        "description": "Whether to inspect the full screen or only the focused application window.",
                    },
                },
                "required": ["query"],
            },
        },
    }
]


class VisionToolHandler:
    """Dispatches screen capture and vision analysis tool calls."""

    def __init__(
        self,
        capture_provider: ScreenCaptureProvider,
        vision_analyzer: VisionAnalyzer,
    ) -> None:
        self.capture_provider = capture_provider
        self.vision_analyzer = vision_analyzer

    async def handle_inspect_screen(self, query: str, target: str = "full_screen") -> str:
        """Execute screen capture and vision inference."""
        if target == "active_window":
            frame = self.capture_provider.capture_active_window()
        else:
            frame = self.capture_provider.capture_screen()

        if not frame or not frame.image_bytes:
            return "Unable to capture screen display at this time."

        description = await self.vision_analyzer.analyze_frame(frame, query)
        logger.info("Vision inspection completed for query: '%s'", query)
        return description
