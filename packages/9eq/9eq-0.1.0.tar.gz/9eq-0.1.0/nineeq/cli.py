"""
Command-line interface for nineeq
"""

import argparse
import sys
from .visualizer import FrequencyVisualizer
from .generator import ToneGenerator
from .config import nineeq_FREQS


def list_frequencies():
    """Display all nineeq frequencies"""
    print("\n" + "=" * 70)
    print("FREQUENCIES")
    print("=" * 70)
    for freq in nineeq_FREQS:
        print(f"{freq:4d} Hz")
    print("=" * 70 + "\n")


def visualize_realtime(args):
    """Start real-time visualization"""
    visualizer = FrequencyVisualizer(
        sample_rate=args.sample_rate,
        buffer_size=args.buffer_size,
        mode=args.mode,
    )

    try:
        visualizer.start(input_device=args.device)
    except KeyboardInterrupt:
        print("\nStopping visualization...")
        visualizer.stop()


def analyze_file(args):
    """Analyze an audio file"""
    visualizer = FrequencyVisualizer()
    visualizer.analyze_file(args.file, duration=args.duration)


def generate_tone(args):
    """Generate a nineeq frequency tone"""
    generator = ToneGenerator(sample_rate=args.sample_rate)

    if args.frequency not in nineeq_FREQS:
        print(f"Warning: {args.frequency}Hz is not a standard nineeq frequency")

    output = args.output or f"nineeq_{args.frequency}hz.wav"
    generator.save_tone(output, args.frequency, duration=args.duration)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="9eq - Analyze and visualize frequencies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # List frequencies command
    subparsers.add_parser("list", help="List all nineeq frequencies")

    # Visualize command
    viz_parser = subparsers.add_parser(
        "visualize", help="Start real-time frequency visualization"
    )
    viz_parser.add_argument(
        "--mode",
        choices=["bar", "wave"],
        default="bar",
        help="Visualization mode (default: bar)",
    )
    viz_parser.add_argument(
        "--sample-rate", type=int, default=44100, help="Audio sample rate (default: 44100)"
    )
    viz_parser.add_argument(
        "--buffer-size", type=int, default=4096, help="Buffer size (default: 4096)"
    )
    viz_parser.add_argument(
        "--device", type=int, help="Input device index (default: system default)"
    )

    # Analyze file command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze an audio file")
    analyze_parser.add_argument("file", help="Path to audio file")
    analyze_parser.add_argument(
        "--duration", type=float, help="Duration to analyze (seconds)"
    )

    # Generate tone command
    gen_parser = subparsers.add_parser("generate", help="Generate a nineeq tone")
    gen_parser.add_argument(
        "frequency", type=int, help="Frequency in Hz (e.g., 528)"
    )
    gen_parser.add_argument(
        "--duration", type=float, default=5.0, help="Duration in seconds (default: 5.0)"
    )
    gen_parser.add_argument(
        "--sample-rate", type=int, default=44100, help="Sample rate (default: 44100)"
    )
    gen_parser.add_argument("--output", help="Output filename (default: auto-generated)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == "list":
        list_frequencies()
    elif args.command == "visualize":
        visualize_realtime(args)
    elif args.command == "analyze":
        analyze_file(args)
    elif args.command == "generate":
        generate_tone(args)


if __name__ == "__main__":
    main()
