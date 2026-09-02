"""Screen capture provider implementation with fallback handling."""

import logging

from aria.core.vision.base import ScreenCaptureProvider, ScreenFrame

logger = logging.getLogger(__name__)


class DesktopScreenCaptureProvider(ScreenCaptureProvider):
    """Captures screen and window frames using native display protocols or mss."""

    def __init__(self) -> None:
        self._initialized = False

    def capture_screen(self) -> ScreenFrame | None:
        """Capture the full screen frame."""
        try:
            import mss  # type: ignore[import-not-found,import-untyped]

            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                import mss.tools  # type: ignore[import-not-found,import-untyped]

                png_bytes = mss.tools.to_png(sct_img.rgb, sct_img.size)
                return ScreenFrame(
                    image_bytes=png_bytes,
                    width=sct_img.width,
                    height=sct_img.height,
                    active_window_title="Desktop",
                )
        except ImportError:
            logger.debug("mss not installed; screen capture unavailable in local environment.")
            return None
        except Exception as e:
            logger.error("Error capturing screen: %s", e)
            return None

    def capture_active_window(self) -> ScreenFrame | None:
        """Capture focused window."""
        # For Linux Wayland/X11 or Electron context
        return self.capture_screen()
