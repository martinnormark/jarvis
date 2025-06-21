"""
Jarvis - Voice Assistant with Interruptible Audio

A voice assistant built with ElevenLabs Conversational AI that supports
real-time audio interruption. Works on both macOS and Raspberry Pi with
platform-specific input methods.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.assistant import JarvisAssistant
from .core.config import Config
from .platforms.detector import PlatformDetector

__all__ = [
    "JarvisAssistant",
    "Config",
    "PlatformDetector",
    "__version__",
]
