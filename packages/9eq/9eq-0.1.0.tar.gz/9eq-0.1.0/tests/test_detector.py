"""
Unit tests for frequency detector
"""

import importlib
import pytest
import numpy as np

_9eq_detector = importlib.import_module('nineeq.detector')
_9eq_config = importlib.import_module('nineeq.config')

FrequencyDetector = _9eq_detector.FrequencyDetector
nineeq_FREQS = _9eq_config.nineeq_FREQS


class TestFrequencyDetector:
    """Test cases for FrequencyDetector class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.detector = FrequencyDetector(sample_rate=44100)
        self.sample_rate = 44100

    def generate_test_tone(self, frequency, duration=1.0, amplitude=0.5):
        """Helper method to generate a pure tone"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        return amplitude * np.sin(2 * np.pi * frequency * t)

    def test_detector_initialization(self):
        """Test detector initializes correctly"""
        assert self.detector.sample_rate == 44100
        assert self.detector.target_freqs == nineeq_FREQS
        assert self.detector.tolerance == 5

    def test_detect_single_frequency(self):
        """Test detection of a single pure tone"""
        # Generate 528 Hz tone
        tone = self.generate_test_tone(528)
        detected = self.detector.detect_frequencies(tone)

        # 528 Hz should be detected
        assert 528 in detected
        assert detected[528] > 0

    def test_detect_multiple_frequencies(self):
        """Test detection of multiple frequencies"""
        # Generate mixed signal
        tone1 = self.generate_test_tone(528, amplitude=0.4)
        tone2 = self.generate_test_tone(741, amplitude=0.3)
        mixed = tone1 + tone2

        detected = self.detector.detect_frequencies(mixed)

        # Both frequencies should be detected
        assert detected[528] > 0
        assert detected[741] > 0

    def test_dominant_frequency(self):
        """Test dominant frequency detection"""
        # Generate strong 528 Hz tone
        tone = self.generate_test_tone(528, amplitude=0.8)
        dominant = self.detector.get_dominant_frequency(tone)

        assert dominant == 528

    def test_normalize_magnitudes(self):
        """Test magnitude normalization"""
        magnitudes = {174: 100, 528: 500, 963: 250}
        normalized = self.detector.normalize_magnitudes(magnitudes)

        # Max should be 1.0
        assert max(normalized.values()) == pytest.approx(1.0)
        assert min(normalized.values()) >= 0.0
        assert normalized[528] == pytest.approx(1.0)  # Highest value

    def test_bandpass_detection(self):
        """Test bandpass filter detection"""
        tone = self.generate_test_tone(528)
        magnitude, filtered = self.detector.detect_with_bandpass(tone, 528)

        assert magnitude > 0
        assert len(filtered) == len(tone)

    def test_empty_signal(self):
        """Test handling of empty signal"""
        empty = np.array([])
        # Should not crash, may return zeros
        detected = self.detector.detect_frequencies(empty)
        assert isinstance(detected, dict)

    def test_noise_signal(self):
        """Test handling of pure noise"""
        rng = np.random.default_rng(42)
        noise = rng.standard_normal(4096) * 0.1
        detected = self.detector.detect_frequencies(noise)

        # All magnitudes should be relatively low
        normalized = self.detector.normalize_magnitudes(detected)
        # No single frequency should dominate
        assert all(v < 0.5 for v in normalized.values())
