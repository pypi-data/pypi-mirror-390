"""
Unit tests for configuration module
"""

import importlib
_9eq_config = importlib.import_module('nineeq.config')

nineeq_FREQS = _9eq_config.nineeq_FREQS
FREQ_COLORS = _9eq_config.FREQ_COLORS
FREQ_MEANINGS = _9eq_config.FREQ_MEANINGS
DEFAULT_SAMPLE_RATE = _9eq_config.DEFAULT_SAMPLE_RATE


def test_nineeq_frequencies_count():
    """Test that we have 9 nineeq frequencies"""
    assert len(nineeq_FREQS) == 9


def test_frequencies_sorted():
    """Test that frequencies are in ascending order"""
    assert nineeq_FREQS == sorted(nineeq_FREQS)


def test_color_mapping_complete():
    """Test that all frequencies have color mappings"""
    for freq in nineeq_FREQS:
        assert freq in FREQ_COLORS
        assert FREQ_COLORS[freq].startswith('#')


def test_meaning_mapping_complete():
    """Test that all frequencies have meaning descriptions"""
    for freq in nineeq_FREQS:
        assert freq in FREQ_MEANINGS
        assert len(FREQ_MEANINGS[freq]) > 0


def test_sample_rate_valid():
    """Test that default sample rate is valid"""
    assert DEFAULT_SAMPLE_RATE > 0
    assert DEFAULT_SAMPLE_RATE >= max(nineeq_FREQS) * 2  # Nyquist
