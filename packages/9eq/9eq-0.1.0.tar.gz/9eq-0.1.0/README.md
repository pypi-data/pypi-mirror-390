# 9eq

Real-time audio visualizer.

> [!NOTE]
> The CLI command is `nineeq` (nine-e-q) and the Python package is `9eq`

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg) ![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- **Real-time Visualization** - Live frequency spectrum analysis with colorized bars
- **Precise Detection** - FFT-based frequency detection with configurable tolerance
- **Audio File Analysis** - Analyze pre-recorded audio files
- **Tone Generation** - Generate pure nineeq frequency tones
- **Color Mapping** - Each frequency has a unique color based on chakra theory
- **Multiple Visualization Modes** - Bar chart and waveform displays
- **CLI Interface** - Easy command-line usage
- **Modular Design** - Use as a library in your own projects

| Frequency | Color      |
| --------- | ---------- |
| 174 Hz    | Deep Red   |
| 285 Hz    | Orange Red |
| 396 Hz    | Orange     |
| 417 Hz    | Gold       |
| 528 Hz    | Green      |
| 639 Hz    | Blue       |
| 741 Hz    | Purple     |
| 852 Hz    | Deep Pink  |
| 963 Hz    | White      |

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/clxrityy/9eq.git
cd 9eq

# Install with pip
pip install -e .
```

### From PyPI

```bash
pip install 9eq
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Usage

### Command Line Interface

#### List all frequencies

```bash
nineeq list
```

#### Real-time visualization

```bash
# Basic visualization
nineeq visualize

# Choose visualization mode
nineeq visualize --mode wave

# Specify audio device
nineeq visualize --device 1
```

#### Analyze an audio file

```bash
nineeq analyze path/to/audio.wav

# Analyze only first 30 seconds
nineeq analyze path/to/audio.wav --duration 30
```

#### Generate a tone

```bash
# Generate 528 Hz tone (5 seconds)
nineeq generate 528

# Custom duration and output
nineeq generate 528 --duration 10 --output miracle_tone.wav
```

### Python Library Usage

```python
import importlib

# Import the package (note: package name is 'nineeq')
_nineeq = importlib.import_module('nineeq')
FrequencyVisualizer = _nineeq.FrequencyVisualizer
FrequencyDetector = _nineeq.FrequencyDetector
ToneGenerator = _nineeq.ToneGenerator

# Real-time visualization
visualizer = FrequencyVisualizer(mode='bar')
visualizer.start()

# Analyze audio file
visualizer.analyze_file('meditation.wav')

# Detect frequencies in audio data
import numpy as np
detector = FrequencyDetector()
audio_data = np.random.randn(4096)  # Your audio data
detected = detector.detect_frequencies(audio_data)

# Generate a tone
generator = ToneGenerator()
generator.save_tone('528hz.wav', frequency=528, duration=5.0)
```

---

### Frequency Detection

The visualizer uses **Fast Fourier Transform (FFT)** to convert time-domain audio signals into frequency-domain data. For each target nineeq frequency:

1. **Windowing**: Applies a Hann window to reduce spectral leakage
2. **FFT Analysis**: Computes the frequency spectrum
3. **Peak Detection**: Identifies magnitude peaks within ±5 Hz of target frequencies
4. **Normalization**: Scales magnitudes for visualization

---

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black nineeq/
```

## Requirements

- Python 3.8+
- NumPy >= 1.21.0
- SciPy >= 1.7.0
- Matplotlib >= 3.5.0
- sounddevice >= 0.4.5
- soundfile >= 0.11.0

```zsh
pip install -r requirements.txt
```

---
