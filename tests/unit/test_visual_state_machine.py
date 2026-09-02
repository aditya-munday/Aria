"""Unit tests for the visual state machine and overlay snapshots."""

import pytest

from aria.core.audio.analyzer import AudioMetrics
from aria.core.pipeline.state import AssistantMode, PipelineState
from aria.visual.overlay.compositor_bridge import MockCompositorBridge
from aria.visual.overlay.state_machine import VisualStateMachine


@pytest.mark.unit
def test_visual_state_transitions() -> None:
    vsm = VisualStateMachine(initial_mode=AssistantMode.ARIA)
    assert vsm.pipeline_state == PipelineState.IDLE

    snapshot_listening = vsm.transition_state(PipelineState.LISTENING)
    assert snapshot_listening.pipeline_state == PipelineState.LISTENING
    assert snapshot_listening.mode == AssistantMode.ARIA
    assert snapshot_listening.scale >= 1.0

    snapshot_thinking = vsm.transition_state(PipelineState.THINKING)
    assert snapshot_thinking.pipeline_state == PipelineState.THINKING

    snapshot_confirm = vsm.transition_state(PipelineState.CONFIRMATION_REQUIRED)
    assert snapshot_confirm.pipeline_state == PipelineState.CONFIRMATION_REQUIRED
    assert snapshot_confirm.primary_color == "#FFB300"


@pytest.mark.unit
def test_jarvis_mode_transformation_sequence() -> None:
    bridge = MockCompositorBridge()
    vsm = VisualStateMachine(
        initial_mode=AssistantMode.ARIA,
        on_render_update=bridge.push_frame,
    )

    vsm.trigger_mode_transformation(AssistantMode.JARVIS)
    assert vsm.is_transforming is True
    assert vsm.mode == AssistantMode.JARVIS

    # Intermediate progress
    snap_mid = vsm.update_transformation_progress(0.5)
    assert snap_mid.transformation_progress == 0.5
    assert snap_mid.is_transforming is True

    # Complete transformation
    snap_final = vsm.update_transformation_progress(1.0)
    assert snap_final.transformation_progress == 1.0
    assert snap_final.is_transforming is False
    assert snap_final.primary_color == "#00E5FF"  # Electric Cyan
    assert snap_final.particle_density == 200

    assert bridge.frame_count > 0


@pytest.mark.unit
def test_audio_reactivity_visual_pulse() -> None:
    vsm = VisualStateMachine()
    vsm.transition_state(PipelineState.SPEAKING)

    base_snapshot = vsm.get_snapshot()

    # Apply speech frame with high amplitude and beat
    metrics = AudioMetrics(amplitude=0.8, energy=1.2, pitch=220.0, is_beat=True)
    reactive_snapshot = vsm.update_audio_reactivity(metrics)

    assert reactive_snapshot.scale > base_snapshot.scale
    assert reactive_snapshot.glow_intensity > base_snapshot.glow_intensity
    assert reactive_snapshot.is_beat is True
