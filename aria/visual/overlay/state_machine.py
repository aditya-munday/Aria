"""Visual state machine driving overlay animations and mode transformations."""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone

from aria.core.audio.analyzer import AudioMetrics
from aria.core.pipeline.state import AssistantMode, PipelineState

logger = logging.getLogger(__name__)


@dataclass
class VisualStateSnapshot:
    """Current renderable visual frame state."""

    pipeline_state: PipelineState = PipelineState.IDLE
    mode: AssistantMode = AssistantMode.ARIA
    is_transforming: bool = False
    transformation_progress: float = 1.0  # 0.0 to 1.0
    scale: float = 1.0
    glow_intensity: float = 0.2
    particle_density: int = 50
    primary_color: str = "#8FA8FF"  # Soft blue for Aria
    secondary_color: str = "#D4BFFF"  # Soft violet for Aria
    audio_amplitude: float = 0.0
    audio_pitch: float = 0.0
    is_beat: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class VisualStateMachine:
    """State machine governing overlay animations, audio reactivity, and mode transformations."""

    def __init__(
        self,
        initial_mode: AssistantMode = AssistantMode.ARIA,
        on_render_update: Callable[[VisualStateSnapshot], None] | None = None,
    ) -> None:
        self.mode = initial_mode
        self.pipeline_state = PipelineState.IDLE
        self.is_transforming = False
        self.transformation_progress = 1.0
        self.on_render_update = on_render_update

        # Audio reactive properties
        self._last_metrics = AudioMetrics(amplitude=0.0, energy=0.0, pitch=0.0, is_beat=False)

    def transition_state(self, new_state: PipelineState) -> VisualStateSnapshot:
        """Transition pipeline state and update visual characteristics."""
        if self.pipeline_state != new_state:
            logger.info(
                "Visual state transitioned from %s to %s",
                self.pipeline_state.value,
                new_state.value,
            )
            self.pipeline_state = new_state

        snapshot = self.get_snapshot()
        if self.on_render_update:
            self.on_render_update(snapshot)
        return snapshot

    def trigger_mode_transformation(self, target_mode: AssistantMode) -> None:
        """Initiate mode switch sequence between Aria and Jarvis."""
        if self.mode == target_mode:
            return

        logger.info(
            "Initiating visual transformation to %s Mode (target 600-800ms)", target_mode.value
        )
        self.mode = target_mode
        self.is_transforming = True
        self.transformation_progress = 0.0

    def update_transformation_progress(self, progress: float) -> VisualStateSnapshot:
        """Update interpolation progress of transformation (0.0 to 1.0)."""
        self.transformation_progress = max(0.0, min(1.0, progress))
        if self.transformation_progress >= 1.0:
            self.is_transforming = False

        snapshot = self.get_snapshot()
        if self.on_render_update:
            self.on_render_update(snapshot)
        return snapshot

    def update_audio_reactivity(self, metrics: AudioMetrics) -> VisualStateSnapshot:
        """Feed real audio analysis metrics into the visual state."""
        self._last_metrics = metrics
        snapshot = self.get_snapshot()
        if self.on_render_update:
            self.on_render_update(snapshot)
        return snapshot

    def get_snapshot(self) -> VisualStateSnapshot:
        """Compute the full current snapshot based on mode, state, and audio metrics."""
        is_jarvis = self.mode == AssistantMode.JARVIS

        # Color palette selection
        if is_jarvis:
            primary_color = "#00E5FF"  # Electric Cyan
            secondary_color = "#0051FF"  # Deep Blue
            base_particle_density = 200
        else:
            primary_color = "#8FA8FF"  # Soft luminous blue
            secondary_color = "#D4BFFF"  # Soft violet
            base_particle_density = 60

        # State-based visual adjustments
        scale = 1.0
        glow = 0.2

        if self.pipeline_state == PipelineState.IDLE:
            scale = 0.95
            glow = 0.15
        elif self.pipeline_state == PipelineState.LISTENING:
            scale = 1.1 + (self._last_metrics.amplitude * 0.2)
            glow = 0.5 + (self._last_metrics.amplitude * 0.5)
        elif self.pipeline_state == PipelineState.THINKING:
            scale = 1.05
            glow = 0.6
        elif self.pipeline_state == PipelineState.SPEAKING:
            scale = 1.0 + (self._last_metrics.amplitude * 0.35)
            glow = 0.4 + (self._last_metrics.amplitude * 0.6)
        elif self.pipeline_state == PipelineState.CONFIRMATION_REQUIRED:
            primary_color = "#FFB300" if not is_jarvis else "#FF3D00"
            scale = 1.15
            glow = 0.85
        elif self.pipeline_state == PipelineState.DELEGATING:
            scale = 1.08
            glow = 0.7

        if self._last_metrics.is_beat:
            scale *= 1.08
            glow = min(1.0, glow + 0.2)

        return VisualStateSnapshot(
            pipeline_state=self.pipeline_state,
            mode=self.mode,
            is_transforming=self.is_transforming,
            transformation_progress=self.transformation_progress,
            scale=round(scale, 3),
            glow_intensity=round(glow, 3),
            particle_density=base_particle_density,
            primary_color=primary_color,
            secondary_color=secondary_color,
            audio_amplitude=self._last_metrics.amplitude,
            audio_pitch=self._last_metrics.pitch,
            is_beat=self._last_metrics.is_beat,
        )
