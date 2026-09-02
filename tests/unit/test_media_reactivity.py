"""Unit tests for media controller and beat reactivity synchronization."""

import pytest

from aria.core.audio.analyzer import AudioMetrics
from aria.core.media.beat_sync import BeatVisualSynchronizer
from aria.core.media.controller import MediaPlayerController, PlaybackState
from aria.core.pipeline.state import AssistantMode, PipelineState
from aria.visual.overlay.state_machine import VisualStateMachine


@pytest.mark.unit
def test_media_player_lifecycle() -> None:
    vsm = VisualStateMachine(initial_mode=AssistantMode.JARVIS)
    player = MediaPlayerController(visual_state_machine=vsm)

    track = player.play_track("Cyberpunk Symphony", artist="SynthWave", duration=210.0)
    assert player.playback_state == PlaybackState.PLAYING
    assert track.title == "Cyberpunk Symphony"
    assert vsm.pipeline_state == PipelineState.MEDIA_REACTIVE

    player.pause()
    assert player.playback_state == PlaybackState.PAUSED
    assert vsm.pipeline_state == PipelineState.IDLE

    player.resume()
    assert player.playback_state == PlaybackState.PLAYING
    assert vsm.pipeline_state == PipelineState.MEDIA_REACTIVE

    player.stop()
    assert player.playback_state == PlaybackState.STOPPED
    assert player.current_track is None

    # Volume limits [0.0, 1.0]
    assert player.set_volume(1.5) == 1.0
    assert player.set_volume(-0.5) == 0.0


@pytest.mark.unit
def test_beat_synchronizer_boosting() -> None:
    vsm = VisualStateMachine(initial_mode=AssistantMode.ARIA)
    sync = BeatVisualSynchronizer(
        visual_state_machine=vsm, beat_scale_boost=0.3, beat_glow_boost=0.4
    )

    metrics_no_beat = AudioMetrics(amplitude=0.2, energy=0.1, pitch=220.0, is_beat=False)
    snap1 = sync.process_metrics(metrics_no_beat)
    base_scale = snap1.scale

    metrics_beat = AudioMetrics(amplitude=0.8, energy=0.9, pitch=220.0, is_beat=True)
    snap2 = sync.process_metrics(metrics_beat)
    assert snap2.scale > base_scale
    assert snap2.is_beat is True
    assert sync.beat_count == 1
