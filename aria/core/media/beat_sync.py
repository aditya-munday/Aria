"""Beat synchronization hook amplifying particle systems during media playback."""

from aria.core.audio.analyzer import AudioMetrics
from aria.visual.overlay.state_machine import VisualStateMachine, VisualStateSnapshot


class BeatVisualSynchronizer:
    """Modulates visual state snapshot dynamics in synchronization with real-time acoustic beats."""

    def __init__(
        self,
        visual_state_machine: VisualStateMachine,
        beat_scale_boost: float = 0.25,
        beat_glow_boost: float = 0.35,
    ) -> None:
        self.visual_state_machine = visual_state_machine
        self.beat_scale_boost = beat_scale_boost
        self.beat_glow_boost = beat_glow_boost
        self.beat_count = 0

    def process_metrics(self, metrics: AudioMetrics) -> VisualStateSnapshot:
        """Process incoming audio metrics and pulse visual elements if a beat occurs."""
        snapshot = self.visual_state_machine.update_audio_reactivity(metrics)

        if metrics.is_beat:
            self.beat_count += 1
            # Intensify scale and glow snapshot properties
            snapshot.scale = round(snapshot.scale + self.beat_scale_boost, 3)
            snapshot.glow_intensity = min(
                1.0, round(snapshot.glow_intensity + self.beat_glow_boost, 3)
            )
            snapshot.is_beat = True

        return snapshot
