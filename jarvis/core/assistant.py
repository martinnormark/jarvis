"""
Main Jarvis assistant class.

Orchestrates the voice assistant functionality with proper error handling
and resource management.
"""

import signal
import sys
from typing import Optional, Callable
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation

from .config import Config
from ..audio.interface import InterruptibleAudioInterface
from ..platforms.detector import PlatformDetector


class JarvisAssistant:
    """
    Main voice assistant class.

    Handles the complete voice assistant workflow including:
    - Platform detection and input handling
    - Audio interface management
    - ElevenLabs conversation management
    - Graceful shutdown and cleanup
    """

    def __init__(self, config: Config):
        """
        Initialize the Jarvis assistant.

        Args:
            config: Configuration object with API keys and settings
        """
        self.config = config
        self.config.validate()

        self.platform_detector = PlatformDetector()
        self.audio_interface: Optional[InterruptibleAudioInterface] = None
        self.conversation: Optional[Conversation] = None
        self.elevenlabs: Optional[ElevenLabs] = None
        self.session_active = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def initialize(self) -> None:
        """
        Initialize all components.

        Raises:
            RuntimeError: If initialization fails
        """
        try:
            # Initialize ElevenLabs client
            self.elevenlabs = ElevenLabs(api_key=self.config.api_key)
            print("✓ ElevenLabs client initialized successfully")

            # Create audio interface
            self.audio_interface = InterruptibleAudioInterface(
                sample_rate=self.config.sample_rate,
                input_frames=self.config.input_frames_per_buffer,
                output_frames=self.config.output_frames_per_buffer,
            )
            print("✓ Audio interface created successfully")

            # Create conversation object
            self.conversation = Conversation(
                self.elevenlabs,
                self.config.agent_id,
                requires_auth=bool(self.config.api_key),
                audio_interface=self.audio_interface,
                callback_agent_response=self._on_agent_response,
                callback_agent_response_correction=self._on_agent_correction,
                callback_user_transcript=self._on_user_transcript,
            )
            print("✓ Conversation object created successfully")

            # Setup platform-specific input handler
            self.platform_detector.setup_input_handler(self._on_input_detected)
            print(f"✓ Running on platform: {self.platform_detector.get_platform()}")

        except Exception as e:
            self.cleanup()
            raise RuntimeError(f"Failed to initialize Jarvis assistant: {e}") from e

    def run(self) -> Optional[str]:
        """
        Run the voice assistant.

        Returns:
            Conversation ID if successful, None otherwise

        Raises:
            RuntimeError: If running fails
        """
        if not self.conversation:
            raise RuntimeError("Assistant not initialized. Call initialize() first.")

        try:
            print("Starting conversation session...")
            self.conversation.start_session()
            self.session_active = True
            print("✓ Conversation session started successfully")

            conversation_id = self.conversation.wait_for_session_end()
            self.session_active = False
            print(f"✓ Conversation ended. ID: {conversation_id}")
            return conversation_id

        except KeyboardInterrupt:
            print("\nReceived keyboard interrupt, shutting down...")
            return None
        except Exception as e:
            print(f"Error during conversation session: {e}")
            return None
        finally:
            self.cleanup()

    def _on_input_detected(self) -> None:
        """Handle input detection (interrupt trigger)."""
        print("Input detected! Interrupting agent speech...")

        try:
            if self.audio_interface:
                self.audio_interface.force_interrupt()
        except Exception as e:
            print(f"Error during audio interruption: {e}")

        # Send contextual update to agent if session is active
        if self.session_active and self.conversation:
            try:
                self.conversation.send_user_message("The user forced an interruption.")
            except Exception as e:
                print(f"Error sending contextual update: {e}")
        else:
            print("Conversation session not yet active, skipping contextual update")

    def _on_agent_response(self, response: str) -> None:
        """Handle agent response callback."""
        print(f"Agent: {response}")

    def _on_agent_correction(self, original: str, corrected: str) -> None:
        """Handle agent response correction callback."""
        print(f"Agent: {original} -> {corrected}")

    def _on_user_transcript(self, transcript: str) -> None:
        """Handle user transcript callback."""
        print(f"User: {transcript}")

    def _signal_handler(self, sig, frame) -> None:
        """Handle shutdown signals."""
        print(f"\nReceived signal {sig}, shutting down gracefully...")
        self.cleanup()
        sys.exit(0)

    def cleanup(self) -> None:
        """Cleanup all resources."""
        try:
            if self.session_active and self.conversation:
                self.conversation.end_session()
                self.session_active = False

            if self.platform_detector:
                self.platform_detector.cleanup()

            if self.audio_interface:
                self.audio_interface.stop()

        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")

    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
