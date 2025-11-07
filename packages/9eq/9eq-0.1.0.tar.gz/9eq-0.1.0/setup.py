"""
Setup script for nineeq Frequency Visualizer
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="9eq",
    version="0.1.0",
    author="MJ Anglin",
    author_email="contact@mjanglin.com",
    description="A real-time visualizer for the 9 nineeq frequencies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clxrityy/9eq",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
        "sounddevice>=0.4.5",
        "soundfile>=0.11.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "advanced": [
            "librosa>=0.9.0",
            "pygame>=2.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nineeq=nineeq.cli:main",
        ],
    },
    keywords="audio visualization nineeq frequency analysis sound healing",
    project_urls={
        "Bug Reports": "https://github.com/clxrityy/9eq/issues",
        "Source": "https://github.com/clxrityy/9eq",
    },
)
