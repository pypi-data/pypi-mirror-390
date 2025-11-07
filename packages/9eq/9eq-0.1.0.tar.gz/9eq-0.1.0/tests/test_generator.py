"""
Unit tests for tone generator
"""

import importlib
import pytest
import numpy as np

_9eq_generator = importlib.import_module('nineeq.generator')
_9eq_config = importlib.import_module('nineeq.config')

ToneGenerator = _9eq_generator.ToneGenerator
nineeq_FREQS = _9eq_config.nineeq_FREQS


class TestToneGenerator:
    """Test cases for ToneGenerator class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.generator = ToneGenerator(sample_rate=44100)

    def test_generator_initialization(self):
        """Test generator initializes correctly"""
        assert self.generator.sample_rate == 44100

    def test_generate_tone_length(self):
        """Test generated tone has correct length"""
        duration = 1.0
        tone = self.generator.generate_tone(528, duration)
        
        expected_length = int(44100 * duration)
        assert len(tone) == expected_length

    def test_generate_tone_amplitude(self):
        """Test tone amplitude is within bounds"""
        tone = self.generator.generate_tone(528, duration=1.0, amplitude=0.5)
        
        # Should not exceed amplitude
        assert np.max(np.abs(tone)) <= 0.51  # Small tolerance for float
        # Should actually reach near the amplitude
        assert np.max(np.abs(tone)) >= 0.49

    def test_generate_chord(self):
        """Test generating a chord with multiple frequencies"""
        chord = self.generator.generate_nineeq_chord(
            frequencies=[528, 741, 963],
            duration=1.0
        )
        
        # Check length
        assert len(chord) == 44100
        # Check amplitude is reasonable (combined but not clipping)
        assert np.max(np.abs(chord)) <= 1.0

    def test_generate_all_frequencies(self):
        """Test generating tones for all nineeq frequencies"""
        for freq in nineeq_FREQS:
            tone = self.generator.generate_tone(freq, duration=0.1)
            assert len(tone) > 0
            assert np.max(np.abs(tone)) > 0

    def test_zero_duration(self):
        """Test handling of zero duration"""
        tone = self.generator.generate_tone(528, duration=0)
        assert len(tone) == 0

    def test_negative_duration(self):
        """Test handling of negative duration (should use abs)"""
        # This might raise an error or return empty - adjust based on implementation
        tone = self.generator.generate_tone(528, duration=-1.0)
        # Should either be empty or positive length, not crash
        assert len(tone) > 0
