"""
Configuration constants for nineeq frequency analysis and visualization
"""

# The 9 nineeq frequencies (Hz)
nineeq_FREQS = [174, 285, 396, 417, 528, 639, 741, 852, 963]

# Color mapping for each frequency (following chakra-inspired color theory)
FREQ_COLORS = {
    174: '#8B0000',  # Deep Red
    285: '#FF4500',  # Orange Red
    396: '#FFA500',  # Orange
    417: '#FFD700',  # Gold
    528: '#00FF00',  # Green
    639: '#1E90FF',  # Blue
    741: '#9370DB',  # Purple
    852: '#FF1493',  # Deep Pink
    963: '#FFFFFF',  # White 
}

# Frequency meanings and associations
FREQ_MEANINGS = {
    174: "Foundation and pain relief",
    285: "Healing and regeneration",
    396: "Liberation from fear and guilt",
    417: "Facilitating change and undoing situations",
    528: "Transformation and miracles (DNA repair)",
    639: "Connecting and relationships",
    741: "Awakening intuition and expression",
    852: "Returning to spiritual order",
    963: "Divine consciousness and enlightenment",
}

# Audio processing parameters
DEFAULT_SAMPLE_RATE = 44100  # CD quality
DEFAULT_BUFFER_SIZE = 4096   # Good balance for real-time
DEFAULT_CHANNELS = 1         # Mono
FREQUENCY_TOLERANCE = 5      # Hz tolerance for detection window

# Visualization parameters
DEFAULT_FPS = 30
DEFAULT_WINDOW_SIZE = (1200, 600)
MIN_MAGNITUDE_THRESHOLD = 100  # Minimum magnitude to display
