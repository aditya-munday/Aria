"""Built-in media player controller and state management."""

import logging
from dataclasses import dataclass
from enum import Enum

from aria.core.pipeline.state import PipelineState
from aria.visual.overlay.state_machine import VisualStateMachine

logger = logging.getLogger(__name__)


class PlaybackState(str, Enum):
    """Media player playback status."""

    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass
class TrackMetadata:
    """Active media track information."""

    title: str = "Unknown Track"
    artist: str = "Unknown Artist"
    duration_seconds: float = 0.0
    current_position_seconds: float = 0.0


class MediaPlayerController:
    """Controls audio playback, track metadata, and triggers MEDIA_REACTIVE visual mode."""

    def __init__(self, visual_state_machine: VisualStateMachine | None = None) -> None:
        self.visual_state_machine = visual_state_machine
        self.playback_state = PlaybackState.IDLE
        self.current_track: TrackMetadata | None = None
        self.volume: float = 0.8  # 0.0 to 1.0

    def play_track(
        self, title: str, artist: str = "Unknown Artist", duration: float = 180.0
    ) -> TrackMetadata:
        """Begin track playback and transition visual overlay to MEDIA_REACTIVE."""
        self.current_track = TrackMetadata(
            title=title,
            artist=artist,
            duration_seconds=duration,
            current_position_seconds=0.0,
        )
        self.playback_state = PlaybackState.PLAYING
        logger.info("Playing media track: '%s' by %s", title, artist)

        if self.visual_state_machine:
            self.visual_state_machine.transition_state(PipelineState.MEDIA_REACTIVE)

        return self.current_track

    def pause(self) -> None:
        """Pause active media playback."""
        if self.playback_state == PlaybackState.PLAYING:
            self.playback_state = PlaybackState.PAUSED
            logger.info("Media playback paused.")
            if self.visual_state_machine:
                self.visual_state_machine.transition_state(PipelineState.IDLE)

    def resume(self) -> None:
        """Resume paused playback."""
        if self.playback_state == PlaybackState.PAUSED:
            self.playback_state = PlaybackState.PLAYING
            logger.info("Media playback resumed.")
            if self.visual_state_machine:
                self.visual_state_machine.transition_state(PipelineState.MEDIA_REACTIVE)

    def stop(self) -> None:
        """Stop playback completely."""
        self.playback_state = PlaybackState.STOPPED
        self.current_track = None
        logger.info("Media playback stopped.")
        if self.visual_state_machine:
            self.visual_state_machine.transition_state(PipelineState.IDLE)

    def set_volume(self, volume: float) -> float:
        """Adjust playback volume [0.0, 1.0]."""
        self.volume = max(0.0, min(1.0, volume))
        logger.info("Media volume set to %.2f", self.volume)
        return self.volume
