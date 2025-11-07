"""
9eq ~

A Python package for detecting, visualizing, and manipulating 9 frequencies: 
174, 285, 396, 417, 639, 741, 852, 963 Hz
"""

__version__ = "0.1.0"
__author__ = "MJ Anglin"
__license__ = "MIT"

from .visualizer import FrequencyVisualizer
from .detector import FrequencyDetector
from .generator import ToneGenerator
from .config import nineeq_FREQS, FREQ_COLORS

__all__ = [
    "FrequencyVisualizer",
    "FrequencyDetector",
    "ToneGenerator",
    "nineeq_FREQS",
    "FREQ_COLORS",
]
