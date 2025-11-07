"""
Audio generation module for creating nineeq frequency tones
"""

import numpy as np
from typing import Optional, List
from .config import nineeq_FREQS, DEFAULT_SAMPLE_RATE


class ToneGenerator:
    """
    Generate pure tones and harmonics for nineeq frequencies
    """

    def __init__(self, sample_rate: int = DEFAULT_SAMPLE_RATE):
        """
        Initialize tone generator

        Args:
            sample_rate: Sample rate for generated audio
        """
        self.sample_rate = sample_rate

    def generate_tone(
        self, frequency: float, duration: float, amplitude: float = 0.5
    ) -> np.ndarray:
        """
        Generate a pure sine wave tone

        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            amplitude: Amplitude (0.0 to 1.0)

        Returns:
            Audio samples as numpy array
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        tone = amplitude * np.sin(2 * np.pi * frequency * t)
        return tone

    def generate_nineeq_chord(
        self, frequencies: Optional[List[int]] = None, duration: float = 2.0
    ) -> np.ndarray:
        """
        Generate a chord with multiple nineeq frequencies

        Args:
            frequencies: List of frequencies (defaults to all nineeq_FREQS)
            duration: Duration in seconds

        Returns:
            Mixed audio samples
        """
        if frequencies is None:
            frequencies = nineeq_FREQS

        # Generate individual tones
        tones = [
            self.generate_tone(freq, duration, amplitude=0.3 / len(frequencies))
            for freq in frequencies
        ]

        # Mix tones
        chord = np.sum(tones, axis=0)
        return chord

    def save_tone(self, filename: str, frequency: float, duration: float = 5.0):
        """
        Generate and save a tone to a WAV file

        Args:
            filename: Output filename
            frequency: Frequency in Hz
            duration: Duration in seconds
        """
        import soundfile as sf

        tone = self.generate_tone(frequency, duration)
        sf.write(filename, tone, self.sample_rate)
        print(f"Saved {frequency}Hz tone to {filename}")
