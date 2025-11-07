"""
Frequency detection module for identifying nineeq frequencies in audio
"""

import numpy as np
from scipy import signal
from typing import Dict, List, Optional, Tuple
from .config import (
    nineeq_FREQS,
    DEFAULT_SAMPLE_RATE,
    FREQUENCY_TOLERANCE,
    MIN_MAGNITUDE_THRESHOLD,
)


class FrequencyDetector:
    """
    Detects and analyzes nineeq frequencies in audio signals
    """

    def __init__(
        self,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        frequencies: Optional[List[int]] = None,
        tolerance: float = FREQUENCY_TOLERANCE,
    ):
        """
        Initialize the frequency detector

        Args:
            sample_rate: Audio sample rate in Hz
            frequencies: List of target frequencies to detect (defaults to nineeq_FREQS)
            tolerance: Frequency detection tolerance window in Hz
        """
        self.sample_rate = sample_rate
        self.target_freqs = frequencies or nineeq_FREQS
        self.tolerance = tolerance

    def detect_frequencies(self, audio_data: np.ndarray) -> Dict[int, float]:
        """
        Detect presence and amplitude of target frequencies using FFT

        Args:
            audio_data: 1D numpy array of audio samples

        Returns:
            Dictionary mapping frequency -> magnitude
        """
        # Ensure audio is 1D
        if audio_data.ndim > 1:
            audio_data = audio_data.flatten()

        # Apply window function to reduce spectral leakage
        windowed_data = audio_data * signal.windows.hann(len(audio_data))  # type: ignore

        # Perform FFT
        fft_data = np.fft.rfft(windowed_data)
        fft_freqs = np.fft.rfftfreq(len(windowed_data), 1 / self.sample_rate)
        magnitudes = np.abs(fft_data)

        detected = {}
        for target_freq in self.target_freqs:
            # Find frequency bin closest to target
            idx = np.argmin(np.abs(fft_freqs - target_freq))

            # Get magnitude in a window around target frequency
            freq_range = int(self.tolerance * len(windowed_data) / self.sample_rate)
            window_start = max(0, idx - freq_range)
            window_end = min(len(magnitudes), idx + freq_range + 1)

            # Use peak magnitude in window
            detected[target_freq] = np.max(magnitudes[window_start:window_end])

        return detected

    def detect_with_bandpass(
        self, audio_data: np.ndarray, target_freq: int
    ) -> Tuple[float, np.ndarray]:
        """
        Detect a specific frequency using bandpass filtering (more accurate)

        Args:
            audio_data: 1D numpy array of audio samples
            target_freq: Target frequency to isolate

        Returns:
            Tuple of (magnitude, filtered_signal)
        """
        # Design bandpass filter
        lowcut = target_freq - self.tolerance
        highcut = target_freq + self.tolerance
        nyquist = self.sample_rate / 2
        low = lowcut / nyquist
        high = highcut / nyquist

        # Create butterworth bandpass filter
        b, a = signal.butter(4, [low, high], btype="band")  # type: ignore

        # Apply filter
        filtered = signal.filtfilt(b, a, audio_data)

        # Calculate RMS magnitude
        magnitude = np.sqrt(np.mean(filtered**2))

        return magnitude, filtered

    def get_dominant_frequency(self, audio_data: np.ndarray) -> Optional[int]:
        """
        Get the dominant nineeq frequency present in the audio

        Args:
            audio_data: 1D numpy array of audio samples

        Returns:
            The dominant frequency or None if below threshold
        """
        detected = self.detect_frequencies(audio_data)

        # Find maximum magnitude
        max_freq = max(detected.items(), key=lambda x: x[1])

        if max_freq[1] > MIN_MAGNITUDE_THRESHOLD:
            return max_freq[0]
        return None

    def get_frequency_spectrum(
        self, audio_data: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get the full frequency spectrum

        Args:
            audio_data: 1D numpy array of audio samples

        Returns:
            Tuple of (frequencies, magnitudes)
        """
        windowed_data = audio_data * signal.windows.hann(len(audio_data))  # type: ignore
        fft_data = np.fft.rfft(windowed_data)
        fft_freqs = np.fft.rfftfreq(len(windowed_data), 1 / self.sample_rate)
        magnitudes = np.abs(fft_data)

        return fft_freqs, magnitudes

    def normalize_magnitudes(self, magnitudes: Dict[int, float]) -> Dict[int, float]:
        """
        Normalize magnitude values to 0-1 range

        Args:
            magnitudes: Dictionary of frequency -> magnitude

        Returns:
            Normalized magnitudes
        """
        max_mag = max(magnitudes.values()) if magnitudes else 1
        if max_mag == 0:
            return dict.fromkeys(magnitudes, 0)

        return {freq: mag / max_mag for freq, mag in magnitudes.items()}
