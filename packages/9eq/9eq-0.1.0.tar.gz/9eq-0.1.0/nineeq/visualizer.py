"""
Real-time visualization module for nineeq frequencies
"""

import numpy as np
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
from typing import Optional, Callable, Any
from .detector import FrequencyDetector
from .config import (
    nineeq_FREQS,
    FREQ_COLORS,
    DEFAULT_SAMPLE_RATE,
    DEFAULT_BUFFER_SIZE,
    DEFAULT_CHANNELS,
    DEFAULT_FPS,
)


class FrequencyVisualizer:
    """
    Real-time visualization of nineeq frequencies from audio input
    """

    def __init__(
        self,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        buffer_size: int = DEFAULT_BUFFER_SIZE,
        frequencies: Optional[list] = None,
        mode: str = "bar",
    ):
        """
        Initialize the frequency visualizer

        Args:
            sample_rate: Audio sample rate in Hz
            buffer_size: Size of audio buffer for processing
            frequencies: List of frequencies to visualize (defaults to nineeq_FREQS)
            mode: Visualization mode ('bar', 'wave', 'circle')
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.target_freqs = frequencies or nineeq_FREQS
        self.mode = mode

        self.detector = FrequencyDetector(sample_rate=sample_rate)
        self.audio_buffer = deque(maxlen=buffer_size)
        self.magnitude_history = {freq: deque(maxlen=50) for freq in self.target_freqs}

        self.stream: Optional[Any] = None
        self.fig: Optional[Any] = None
        self.ax: Optional[Any] = None
        self.ax2: Optional[Any] = None
        self.bars: Optional[Any] = None
        self.line: Optional[Any] = None

    def audio_callback(self, indata, frames, time, status):
        """
        Callback function for audio input stream

        Args:
            indata: Input audio data
            frames: Number of frames
            time: Time info
            status: Stream status
        """
        if status:
            print(f"Stream status: {status}")

        # Append mono audio to buffer
        if indata.shape[1] > 1:
            # Convert stereo to mono
            mono = np.mean(indata, axis=1)
        else:
            mono = indata[:, 0]

        self.audio_buffer.extend(mono)

    def _setup_bar_plot(self):
        """Setup bar chart visualization"""
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        if hasattr(self.fig.canvas, 'manager') and self.fig.canvas.manager:
            self.fig.canvas.manager.set_window_title("9eq")

        self.bars = self.ax.bar(
            range(len(self.target_freqs)),
            [0] * len(self.target_freqs),
            color=[FREQ_COLORS[f] for f in self.target_freqs],
            alpha=0.7,
            edgecolor="black",
            linewidth=1.5,
        )

        self.ax.set_xlabel("Frequency (Hz)", fontsize=12, fontweight="bold")
        self.ax.set_ylabel("Magnitude", fontsize=12, fontweight="bold")
        self.ax.set_title(
            "nineeq Frequency Spectrum - Real-time Analysis",
            fontsize=14,
            fontweight="bold",
        )
        self.ax.set_xticks(range(len(self.target_freqs)))
        self.ax.grid(True, alpha=0.3, axis="y")
        plt.tight_layout()

    def _setup_wave_plot(self):
        """Setup waveform visualization"""
        self.fig, (self.ax, self.ax2) = plt.subplots(2, 1, figsize=(12, 8))
        if hasattr(self.fig.canvas, 'manager') and self.fig.canvas.manager:
            self.fig.canvas.manager.set_window_title("9eq")

        # Waveform plot
        self.line, = self.ax.plot([], [], lw=1, color="cyan")  # type: ignore
        self.ax.set_xlabel("Time (samples)")  # type: ignore
        self.ax.set_ylabel("Amplitude")  # type: ignore
        self.ax.set_title("Audio Waveform")  # type: ignore
        self.ax.grid(True, alpha=0.3)  # type: ignore

        # Frequency bars
        self.bars = self.ax2.bar(  # type: ignore
            range(len(self.target_freqs)),
            [0] * len(self.target_freqs),
            color=[FREQ_COLORS[f] for f in self.target_freqs],
            alpha=0.7,
        )
        self.ax2.set_xlabel("Frequency (Hz)")  # type: ignore
        self.ax2.set_ylabel("Magnitude")  # type: ignore
        self.ax2.set_xticks(range(len(self.target_freqs)))  # type: ignore
        self.ax2.set_xticklabels(self.target_freqs, rotation=45)  # type: ignore
        self.ax2.grid(True, alpha=0.3, axis="y")  # type: ignore
        plt.tight_layout()

    def _update_bar_plot(self, frame):
        """Update bar chart visualization"""
        if len(self.audio_buffer) >= self.buffer_size and self.bars is not None:
            audio_data = np.array(list(self.audio_buffer))
            detected = self.detector.detect_frequencies(audio_data)
            normalized = self.detector.normalize_magnitudes(detected)

            # Update history
            for freq in self.target_freqs:
                self.magnitude_history[freq].append(normalized.get(freq, 0))

            # Smooth magnitudes using history
            smoothed = {
                freq: np.mean(list(self.magnitude_history[freq]))
                for freq in self.target_freqs
            }

            # Update bars
            for bar, freq in zip(self.bars, self.target_freqs):
                bar.set_height(smoothed[freq])

        return self.bars or []

    def _update_wave_plot(self, frame):
        """Update waveform visualization"""
        if len(self.audio_buffer) >= self.buffer_size and self.ax is not None and self.bars is not None and self.line is not None:
            audio_data = np.array(list(self.audio_buffer))

            # Update waveform
            self.line.set_data(range(len(audio_data)), audio_data)
            self.ax.set_xlim(0, len(audio_data))
            self.ax.set_ylim(-1, 1)

            # Update frequency bars
            detected = self.detector.detect_frequencies(audio_data)
            normalized = self.detector.normalize_magnitudes(detected)

            for bar, freq in zip(self.bars, self.target_freqs):
                bar.set_height(normalized.get(freq, 0))

        return [self.line] + list(self.bars) if self.line is not None and self.bars is not None else []

    def start(self, input_device: Optional[int] = None):
        """
        Start real-time visualization

        Args:
            input_device: Input device index (None for default)
        """
        # Setup visualization based on mode
        if self.mode == "bar":
            self._setup_bar_plot()
            update_func = self._update_bar_plot
        elif self.mode == "wave":
            self._setup_wave_plot()
            update_func = self._update_wave_plot
        else:
            raise ValueError(f"Unknown visualization mode: {self.mode}")

        # Start audio stream
        self.stream = sd.InputStream(
            callback=self.audio_callback,
            channels=DEFAULT_CHANNELS,
            samplerate=self.sample_rate,
            device=input_device,
        )

        print(f"Starting visualization (mode: {self.mode})...")
        print(f"Monitoring frequencies: {self.target_freqs}")
        print("Press Ctrl+C to stop")

        with self.stream:
            # Create animation (stored to prevent garbage collection)
            if self.fig is not None:
                _anim = FuncAnimation(  # noqa: F841
                    self.fig, update_func, interval=1000 // DEFAULT_FPS, blit=False
                )
                plt.show()
            else:
                print("Error: Figure not initialized")

    def stop(self):
        """Stop the visualization"""
        if self.stream:
            self.stream.stop()
            self.stream.close()
        if self.fig:
            plt.close(self.fig)

    def analyze_file(self, filepath: str, duration: Optional[float] = None):
        """
        Analyze audio from a file instead of live input

        Args:
            filepath: Path to audio file
            duration: Duration to analyze (None for entire file)
        """
        import soundfile as sf

        # Read audio file
        audio_data, sample_rate = sf.read(filepath)

        # Convert to mono if stereo
        if audio_data.ndim > 1:
            audio_data = np.mean(audio_data, axis=1)

        # Limit duration if specified
        if duration:
            max_samples = int(duration * sample_rate)
            audio_data = audio_data[:max_samples]

        # Detect frequencies
        detected = self.detector.detect_frequencies(audio_data)
        normalized = self.detector.normalize_magnitudes(detected)

        # Display results
        print(f"\nAnalysis of: {filepath}")
        print("-" * 50)
        for freq in self.target_freqs:
            magnitude = normalized.get(freq, 0)
            bar = "█" * int(magnitude * 30)
            print(f"{freq:4d} Hz | {bar:<30} | {magnitude:.2%}")

        return detected
