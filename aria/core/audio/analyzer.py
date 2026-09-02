"""Real-time audio analyzer for visual reactivity (amplitude, pitch proxy, energy, beat)."""

import math
from typing import NamedTuple

import numpy as np


class AudioMetrics(NamedTuple):
    """Real-time audio metrics extracted from PCM frame."""

    amplitude: float  # Normalized 0.0 to 1.0
    energy: float  # Spectral energy
    pitch: float  # Approximate fundamental frequency in Hz
    is_beat: bool  # Transient beat detection flag


class AudioAnalyzer:
    """Computes real-time acoustic features to drive the visual layer."""

    def __init__(
        self,
        sample_rate: int = 24000,
        beat_threshold_multiplier: float = 1.5,
        energy_history_size: int = 43,  # ~1 second of frames
    ) -> None:
        self.sample_rate = sample_rate
        self.beat_threshold_multiplier = beat_threshold_multiplier
        self.energy_history_size = energy_history_size

        self._energy_history: list[float] = []

    def analyze_frame(self, audio_bytes: bytes) -> AudioMetrics:
        """Analyze a 16-bit PCM audio frame and return visual metrics."""
        if not audio_bytes or len(audio_bytes) < 4:
            return AudioMetrics(amplitude=0.0, energy=0.0, pitch=0.0, is_beat=False)

        # Convert PCM bytes to float array [-1.0, 1.0]
        audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        # 1. RMS Amplitude
        rms = float(np.sqrt(np.mean(np.square(audio_data))))
        normalized_amplitude = min(1.0, rms * 3.0)

        # 2. Instantaneous Spectral Energy
        instant_energy = float(np.sum(np.square(audio_data)))

        # 3. Beat Detection (Dynamic Energy Thresholding)
        is_beat = False
        if len(self._energy_history) > 0:
            avg_energy = sum(self._energy_history) / len(self._energy_history)
            variance = sum((e - avg_energy) ** 2 for e in self._energy_history) / len(
                self._energy_history
            )
            # Dynamic C multiplier based on variance
            c_factor = (-0.0025714 * variance) + 1.5142857
            threshold = avg_energy * max(1.1, c_factor * self.beat_threshold_multiplier)

            if instant_energy > threshold and instant_energy > 0.05:
                is_beat = True

        self._energy_history.append(instant_energy)
        if len(self._energy_history) > self.energy_history_size:
            self._energy_history.pop(0)

        # 4. Zero-Crossing Rate as robust pitch / frequency proxy
        zero_crossings = np.nonzero(np.diff(audio_data > 0))[0]
        num_zero_crossings = len(zero_crossings)
        duration_s = len(audio_data) / self.sample_rate
        estimated_pitch = (num_zero_crossings / (2.0 * duration_s)) if duration_s > 0 else 0.0
        if math.isnan(estimated_pitch) or math.isinf(estimated_pitch):
            estimated_pitch = 0.0

        return AudioMetrics(
            amplitude=round(normalized_amplitude, 4),
            energy=round(instant_energy, 4),
            pitch=round(estimated_pitch, 2),
            is_beat=is_beat,
        )

    def reset(self) -> None:
        """Reset internal history buffers."""
        self._energy_history.clear()
