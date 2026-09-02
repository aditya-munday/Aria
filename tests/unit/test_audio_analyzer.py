"""Unit tests for real-time audio analysis and metrics."""

import numpy as np
import pytest

from aria.core.audio.analyzer import AudioAnalyzer
from aria.core.audio.player import AudioPlayerBridge


@pytest.mark.unit
def test_audio_analyzer_synthetic_sine_wave() -> None:
    analyzer = AudioAnalyzer(sample_rate=24000)

    # 440 Hz sine wave for 50ms
    duration = 0.05
    t = np.linspace(0, duration, int(24000 * duration), endpoint=False)
    sine = (np.sin(2 * np.pi * 440 * t) * 30000).astype(np.int16)
    audio_bytes = sine.tobytes()

    metrics = analyzer.analyze_frame(audio_bytes)
    assert metrics.amplitude > 0.1
    assert metrics.energy > 0.0
    assert 350 <= metrics.pitch <= 550


@pytest.mark.unit
def test_audio_analyzer_empty_frame() -> None:
    analyzer = AudioAnalyzer()
    metrics = analyzer.analyze_frame(b"")
    assert metrics.amplitude == 0.0
    assert metrics.is_beat is False


@pytest.mark.asyncio
@pytest.mark.unit
async def test_audio_player_bridge() -> None:
    captured_metrics = []
    player = AudioPlayerBridge(on_metrics=lambda m: captured_metrics.append(m))

    dummy_frame = b"\x00\x00" * 512
    await player.play_chunk(dummy_frame)

    assert len(captured_metrics) == 1
    assert captured_metrics[0].amplitude == 0.0

    player.stop()
