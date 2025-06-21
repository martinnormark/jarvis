"""
Platform detection for Jarvis.

Detects the current platform and provides appropriate input methods
for button presses (GPIO on Raspberry Pi, keyboard on Mac).
"""

import platform
import os
from typing import Optional
from .handlers import InputHandler


class PlatformDetector:
    """Detects the current platform and provides appropriate input methods."""

    def __init__(self):
        self.platform = self._detect_platform()
        self.input_handler: Optional[InputHandler] = None

    def _detect_platform(self) -> str:
        """Detect the current platform."""
        system = platform.system().lower()

        if system == "darwin":
            return "mac"
        elif system == "linux":
            # Check if we're on Raspberry Pi
            if os.path.exists("/proc/device-tree/model"):
                try:
                    with open("/proc/device-tree/model", "r") as f:
                        model = f.read().lower()
                        if "raspberry pi" in model:
                            return "pi"
                except (OSError, IOError):
                    pass
            return "linux"
        else:
            return "unknown"

    def get_platform(self) -> str:
        """Get the detected platform."""
        return self.platform

    def is_mac(self) -> bool:
        """Check if running on Mac."""
        return self.platform == "mac"

    def is_pi(self) -> bool:
        """Check if running on Raspberry Pi."""
        return self.platform == "pi"

    def is_linux(self) -> bool:
        """Check if running on Linux (non-Pi)."""
        return self.platform == "linux"

    def setup_input_handler(self, callback) -> None:
        """
        Setup the appropriate input handler for the current platform.

        Args:
            callback: Function to call when input is detected
        """
        try:
            self.input_handler = InputHandler.create_for_platform(
                self.platform, callback
            )
        except Exception as e:
            print(
                f"Warning: Failed to setup input handler for platform '{self.platform}': {e}"
            )

    def cleanup(self) -> None:
        """Cleanup any resources used by the input handler."""
        if self.input_handler:
            self.input_handler.cleanup()
            self.input_handler = None
