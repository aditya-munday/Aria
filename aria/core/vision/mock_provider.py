"""Mock screen capture provider and vision analyzer for CI tests."""

from aria.core.vision.base import (
    ScreenCaptureProvider,
    ScreenFrame,
    VisionAnalyzer,
)


class MockScreenCaptureProvider(ScreenCaptureProvider):
    """Mock screen provider returning synthetic test frames."""

    def __init__(self, default_window_title: str = "Code Editor - main.py") -> None:
        self.default_window_title = default_window_title
        self.capture_count = 0

    def capture_screen(self) -> ScreenFrame:
        """Return synthetic screen frame."""
        self.capture_count += 1
        return ScreenFrame(
            image_bytes=b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRmock_data",
            width=1920,
            height=1080,
            active_window_title=self.default_window_title,
        )

    def capture_active_window(self) -> ScreenFrame:
        """Return synthetic active window frame."""
        self.capture_count += 1
        return ScreenFrame(
            image_bytes=b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRmock_window",
            width=1280,
            height=720,
            active_window_title=self.default_window_title,
        )


class MockVisionAnalyzer(VisionAnalyzer):
    """Mock vision analyzer returning synthetic frame descriptions."""

    def __init__(self, default_description: str = "A code editor with Python files open.") -> None:
        self.default_description = default_description
        self.analyzed_prompts: list[str] = []

    async def analyze_frame(self, frame: ScreenFrame, prompt: str) -> str:
        """Return canned frame description."""
        self.analyzed_prompts.append(prompt)
        return f"{self.default_description} (Window: {frame.active_window_title})"
