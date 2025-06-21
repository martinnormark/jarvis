"""
Input handlers for different platforms.

Provides platform-specific input handling using the strategy pattern.
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional


class InputHandler(ABC):
    """Abstract base class for input handlers."""

    @abstractmethod
    def setup(self, callback: Callable[[], None]) -> None:
        """Setup the input handler."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup resources."""
        pass

    @classmethod
    def create_for_platform(
        cls, platform: str, callback: Callable[[], None]
    ) -> "InputHandler":
        """
        Create the appropriate input handler for the platform.

        Args:
            platform: Platform identifier
            callback: Function to call when input is detected

        Returns:
            InputHandler instance for the platform

        Raises:
            ValueError: If platform is not supported
        """
        if platform == "mac":
            return MacInputHandler()
        elif platform == "pi":
            return PiInputHandler()
        else:
            return NoOpInputHandler()

    def setup(self, callback: Callable[[], None]) -> None:
        """Setup the input handler with callback."""
        self._setup_impl(callback)

    @abstractmethod
    def _setup_impl(self, callback: Callable[[], None]) -> None:
        """Platform-specific setup implementation."""
        pass


class MacInputHandler(InputHandler):
    """Keyboard input handler for macOS."""

    def __init__(self):
        self.keyboard = None

    def _setup_impl(self, callback: Callable[[], None]) -> None:
        """Setup keyboard handler for Mac."""
        try:
            import keyboard

            def on_space_press():
                print("Spacebar pressed! Interrupting agent speech...")
                callback()

            keyboard.on_press_key("space", lambda _: on_space_press())
            self.keyboard = keyboard
            print("Keyboard handler setup: Press SPACEBAR to interrupt")

        except ImportError:
            raise ImportError(
                "Keyboard package not installed. Install with: uv add --extra mac"
            )

    def cleanup(self) -> None:
        """Cleanup keyboard handler."""
        if self.keyboard:
            try:
                self.keyboard.unhook_all()
            except Exception as e:
                print(f"Warning: Error cleaning up keyboard handler: {e}")


class PiInputHandler(InputHandler):
    """GPIO input handler for Raspberry Pi."""

    def __init__(self):
        self.button = None

    def _setup_impl(self, callback: Callable[[], None]) -> None:
        """Setup GPIO handler for Raspberry Pi."""
        try:
            from gpiozero import Button

            def on_button_press():
                print("Button pressed! Interrupting agent speech...")
                callback()

            self.button = Button(17)
            self.button.when_pressed = on_button_press
            print("GPIO handler setup: Press button on GPIO17 to interrupt")

        except ImportError:
            raise ImportError(
                "GPIOZero package not installed. Install with: uv add --extra pi"
            )

    def cleanup(self) -> None:
        """Cleanup GPIO handler."""
        if self.button:
            try:
                self.button.close()
            except Exception as e:
                print(f"Warning: Error cleaning up GPIO handler: {e}")


class NoOpInputHandler(InputHandler):
    """No-operation input handler for unsupported platforms."""

    def _setup_impl(self, callback: Callable[[], None]) -> None:
        """No-op setup."""
        print("Warning: No input handler available for this platform")

    def cleanup(self) -> None:
        """No-op cleanup."""
        pass
